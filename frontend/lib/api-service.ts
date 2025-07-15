import axios from "axios";
import { FileInfo, Chat } from "./types";
import { getApiUrl } from "./api-config";

// Create an axios instance
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor: attach token if present
api.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("authToken");
      if (token) {
        config.headers = config.headers || {};
        config.headers["Authorization"] = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Create a new chat
export const createChat = async (): Promise<{ id: string }> => {
  const response = await api.post("/chats", {
    title: "New Chat",
    forceCreate: true,
  });
  const data = response.data;
  return { id: data.id.toString() };
};

// Get all chats
export const getChats = async (): Promise<Chat[]> => {
  const response = await api.get("/chats");
  const data = response.data;
  return data.map((chat: any) => ({
    ...chat,
    id: chat.id.toString(),
    name: chat.title,
    messages:
      chat.messages?.map((msg: any) => ({
        ...msg,
        id: msg.id.toString(),
        chat_id: msg.chat_id.toString(),
      })) || [],
  }));
};

// Get a single chat
export const getChat = async (chatId: string): Promise<Chat | null> => {
  const response = await api.get(`/chats/${chatId}`);
  const data = response.data;
  // Optionally reset context (if needed, can be a separate call)
  // await api.post(`/chats/${chatId}/reset-context`, { chat_id: chatId });
  return {
    ...data,
    id: data.id.toString(),
    name: data.title,
    messages:
      data.messages?.map((msg: any) => ({
        ...msg,
        id: msg.id.toString(),
        chat_id: msg.chat_id.toString(),
      })) || [],
  };
};

// Delete a chat
export const deleteChat = async (chatId: string) => {
  await api.delete(`/chats/${chatId}`);
  return { success: true };
};

// Rename a chat
export const renameChat = async (chatId: string, name: string) => {
  const response = await api.patch(`/chats/${chatId}`, { title: name });
  const chat = response.data;
  return {
    ...chat,
    id: chat.id.toString(),
  };
};

// Upload a file
export const uploadFile = async (file: File): Promise<FileInfo> => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post("/files/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

// Send a message with streaming response (SSE)
export const streamChatMessage = async (
  chatId: string,
  message: string,
  files?: File[],
  onChunk?: (chunk: string) => void,
  onError?: (error: Error) => void,
  onDone?: () => void
) => {
  let fileIds: string[] = [];
  try {
    if (files && files.length > 0) {
      for (const f of files) {
        try {
          const fileInfo = await uploadFile(f);
          fileIds.push(fileInfo.file_id);
        } catch (uploadError: any) {
          onError?.(new Error(uploadError.message || "File upload error"));
          return;
        }
      }
    }
    const requestBody: { content?: string; file_ids?: string[] } = {};
    if (message) requestBody.content = message;
    if (fileIds.length > 0) requestBody.file_ids = fileIds;
    if (!requestBody.content && (!requestBody.file_ids || requestBody.file_ids.length === 0)) {
      onError?.(new Error("No message content or file provided."));
      return;
    }
    // Use fetch for SSE (axios does not support streaming response bodies)
    const token = typeof window !== "undefined" ? localStorage.getItem("authToken") : null;
    const response = await fetch(getApiUrl(`/chats/${chatId}/stream`), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(requestBody),
    });
    if (!response.ok) {
      let errorDetail = `Error: ${response.status} ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData && errorData.detail) errorDetail = errorData.detail;
      } catch {}
      throw new Error(errorDetail);
    }
    const reader = response.body?.getReader();
    if (!reader) throw new Error("No reader available for stream");
    const decoder = new TextDecoder();
    let buffer = "";
    let streamActive = true;
    try {
      while (streamActive) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (!line.trim()) continue;
          if (line.startsWith("data: ")) {
            const dataContent = line.substring(6);
            if (dataContent === "[DONE]") {
              onDone?.();
              streamActive = false;
              break;
            }
            try {
              const data = JSON.parse(dataContent);
              if (data.generation_id) continue;
              if (data.text) onChunk?.(data.text);
              if (data.error) onError?.(new Error(data.text || data.error));
            } catch {
              onChunk?.(dataContent);
            }
          }
        }
      }
    } catch (error) {
      onError?.(error instanceof Error ? error : new Error(String(error)));
    } finally {
      onDone?.();
    }
  } catch (error: any) {
    onError?.(error instanceof Error ? error : new Error("An unexpected error occurred during chat streaming."));
  }
};

// Interrupt a running generation
export const interruptGeneration = async (generationId: string, chatId: string) => {
  const url = `/chats/${chatId}/interrupt?generation_id=${encodeURIComponent(generationId)}`;
  const response = await api.post(url);
  return response.data;
};