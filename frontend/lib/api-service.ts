import { getApiUrl } from './api-config'
import { FileInfo, Chat } from './types'
import { useStore } from './store'

/**
 * API service for communicating with the backend
 */

// Create a new chat
export const createChat = async (): Promise<{ id: string }> => {
  const response = await fetch(getApiUrl('/chats'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
      title: `New Chat`,
      forceCreate: true // Add this flag to force creation of a new chat
    }),
  })

  if (!response.ok) {
    throw new Error(`Failed to create chat: ${response.statusText}`)
  }

  // Get the response data
  const data = await response.json()
  
  // When the backend returns an existing chat, it will have an ID
  // Convert the numeric ID to string (as the frontend uses string IDs)
  return { id: data.id.toString() }
}

// Get all chats
export const getChats = async (): Promise<Chat[]> => {
  // console.log('Fetching chats from API...');
  try {
    const response = await fetch(getApiUrl('/chats'), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get chats: ${response.statusText}`);
    }

    const data = await response.json();
    // console.log(`Received ${data.length} chats from backend`);
    
    // Convert numeric IDs to strings for frontend consistency
    return data.map((chat: any) => ({
      ...chat,
      id: chat.id.toString(),
      name: chat.title,
      messages: chat.messages?.map((msg: any) => ({
        ...msg,
        id: msg.id.toString(),
        chat_id: msg.chat_id.toString()
      })) || []
    }));
  } catch (error) {
    console.error("Error fetching chats:", error);
    throw error;
  }
}

// Get a single chat
export const getChat = async (chatId: string): Promise<Chat | null> => {
  // console.log(`Fetching chat with ID: ${chatId}...`);
  try {
    const response = await fetch(getApiUrl(`/chats/${chatId}`), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to get chat: ${response.statusText}`);
    }

    const data = await response.json();
    // console.log(`Successfully retrieved chat ${chatId} with ${data.messages.length} messages`);
    
    // When loading a chat, tell the backend to reset its context for this chat
    // This ensures that when we send the next message, it will rebuild the context from the database
    try {
      await fetch(getApiUrl(`/chats/${chatId}/reset-context`), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ chat_id: chatId })
      });
      // console.log(`Reset context for chat ID: ${chatId}`);
    } catch (error) {
      console.error(`Failed to reset context for chat ID: ${chatId}`, error);
    }
    
    // Convert numeric ID to string for frontend consistency
    return {
      ...data,
      id: data.id.toString(),
      name: data.title,
      messages: data.messages?.map((msg: any) => ({
        ...msg,
        id: msg.id.toString(),
        chat_id: msg.chat_id.toString()
      })) || []
    };
  } catch (error) {
    console.error(`Error fetching chat ${chatId}:`, error);
    throw error;
  }
}

// Delete a chat
export const deleteChat = async (chatId: string) => {
  const response = await fetch(getApiUrl(`/chats/${chatId}`), {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to delete chat: ${response.statusText}`)
  }

  // Return successful deletion (HTTP 204 returns no content)
  return { success: true }
}

// Rename a chat
export const renameChat = async (chatId: string, name: string) => {
  const response = await fetch(getApiUrl(`/chats/${chatId}`), {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title: name }),
  })

  if (!response.ok) {
    throw new Error(`Failed to rename chat: ${response.statusText}`)
  }

  const chat = await response.json()
  
  // Convert numeric ID to string for frontend consistency
  return {
    ...chat,
    id: chat.id.toString()
  }
}

// Upload a file
export const uploadFile = async (file: File): Promise<FileInfo> => {
  const formData = new FormData()
  formData.append('file', file)

  let response: Response;
  try {
    response = await fetch(getApiUrl('/files/upload'), {
      method: 'POST',
      body: formData,
    });
  } catch (networkError) {
    // Handle network errors during fetch itself
    console.error('Network error during file upload:', networkError);
    throw new Error('Network error: Failed to connect to server for file upload.');
  }

  if (!response.ok) {
    let errorMessage = `Failed to upload file: ${response.status} ${response.statusText}`;
    try {
      const errorData = await response.json();
      if (errorData && errorData.detail) {
        errorMessage = errorData.detail; // Use detailed error message from backend if available
      }
    } catch (jsonError) {
      // Backend did not return JSON or it was malformed, stick to statusText
      console.error('Could not parse error response from uploadFile:', jsonError);
    }
    console.error('File upload failed with status:', response.status, 'Message:', errorMessage);
    throw new Error(errorMessage);
  }

  try {
    return await response.json();
  } catch (jsonError) {
    console.error('Error parsing JSON response from successful file upload:', jsonError);
    throw new Error('Received an invalid response from the server after file upload.');
  }
}

// Send a message with streaming response
export const streamChatMessage = async (
  chatId: string,
  message: string,
  files?: File[],
  onChunk?: (chunk: string) => void,
  onError?: (error: Error) => void,
  onDone?: () => void
) => {
  let fileIds: string[] = [];
  // Create and store AbortController for this generation
  const abortController = new AbortController();

  try {
    // If files are provided, upload each and collect file IDs
    if (files && files.length > 0) {
      for (const f of files) {
        try {
          const fileInfo = await uploadFile(f);
          fileIds.push(fileInfo.file_id);
        } catch (uploadError: any) {
          console.error('Error uploading file within streamChatMessage:', uploadError);
          const errorMessage = uploadError instanceof Error ? uploadError.message : 'Unknown file upload error';
          onError?.(new Error(errorMessage));
          return;
        }
      }
    }

    const requestBody: { content?: string; file_ids?: string[] } = {};
    if (message) {
      requestBody.content = message; 
    }
    if (fileIds.length > 0) {
      requestBody.file_ids = fileIds;
    }

    if (!requestBody.content && (!requestBody.file_ids || requestBody.file_ids.length === 0)) {
        const noContentError = new Error('No message content or file provided.');
        console.error(noContentError.message);
        onError?.(noContentError);
        return;
    }

    const response = await fetch(getApiUrl(`/chats/${chatId}/stream`), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'X-Debug-Client': 'troubleshooting-stream',
        'X-Chat-Context': 'keep', // Always preserve chat context
        'X-Generation-Id': 'unknown', // Send generation ID
      },
      body: JSON.stringify(requestBody),
      signal: abortController.signal,
    });

    if (!response.ok) {
      let errorDetail = `Error: ${response.status} ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData && errorData.detail) {
          errorDetail = errorData.detail;
        }
      } catch (e) { /* Ignore if error response is not JSON */ }
      throw new Error(errorDetail); // This will be caught by the outer try-catch
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No reader available for stream'); // Caught by outer try-catch
    }

    // Process the stream as Server-Sent Events (SSE)
    const processStream = async () => {
      const decoder = new TextDecoder()
      let buffer = ''
      let streamActive = true;
      let accumulatedText = '';
      
      try {
        while (streamActive) {
          if (abortController.signal.aborted) {
            break;
          }
          const { done, value } = await reader.read()
          
          if (done) {
            streamActive = false;
            break;
          }
          
          // Append the new chunk to the buffer
          const chunk = decoder.decode(value, { stream: true })
          buffer += chunk
          
          // Process lines in the buffer
          const lines = buffer.split('\n')
          
          // Keep the last (potentially incomplete) line in the buffer
          buffer = lines.pop() || ''
          
          for (const line of lines) {
            // Skip empty lines
            if (!line.trim()) continue
            
            if (line.startsWith('data: ')) {
              try {
                // Parse the JSON data
                const dataContent = line.substring(6);
                
                // Check if it's the DONE marker
                if (dataContent === '[DONE]') {
                  onDone?.();
                  streamActive = false;
                  break;
                }
                
                // Attempt to parse JSON
                try {
                  const data = JSON.parse(dataContent);
                  
                  // Handle generation ID
                  if (data.generation_id) {
                    continue;
                  }
                  
                  // Handle text chunks
                  if (data.text) {
                    const textChunk = data.text;
                    
                    // Accumulate the text for logging
                    accumulatedText += textChunk;
                    
                    // Call the chunk handler
                    if (!abortController.signal.aborted) {
                      onChunk?.(textChunk);
                    }
                    continue;
                  }
                  
                  // Handle error messages
                  if (data.error) {
                    const errorMsg = data.text || data.error;
                    onError?.(new Error(errorMsg));
                    continue;
                  }
                  
                  console.warn('Received unexpected data format:', data);
                } catch (parseError) {
                  if (!abortController.signal.aborted) {
                    onChunk?.(dataContent);
                  }
                }
              } catch (processingError) {
                console.error('Error processing data line:', processingError, 'Line:', line);
              }
            } else if (line.startsWith(':')) {
              // This is a comment/keepalive, typically ": keepalive"
              continue;
            } else {
              console.warn('Unexpected line format in SSE stream:', line);
            }
          }
        }
      } catch (error) {
        // Suppress AbortError from fetch aborts
        if ((error as any)?.name === 'AbortError') {
          return;
        }
        onError?.(error instanceof Error ? error : new Error(String(error)));
      } finally {
        try {
          // Ensure the reader is properly closed
          await reader.cancel();
        } catch (e) {
          const err = e as Error;
          if (!(err instanceof DOMException && err.name === 'AbortError')) {
            console.warn('Error closing reader:', err);
          }
          // else: silently ignore AbortError
        }
        
        onDone?.();
      }
    }
    
    // Start the stream processing as a properly awaited async task
    return processStream().catch(error => {
      // Suppress AbortError from fetch aborts
      if ((error as any)?.name === 'AbortError') {
        return;
      }
      console.error('Unhandled error in processStream:', error);
      onError?.(error instanceof Error ? error : new Error('Unhandled stream processing error'));
    });
  } catch (error: any) {
    // Suppress AbortError from fetch aborts
    if ((error as any)?.name === 'AbortError') {
      // Do not call onError for aborts
      return;
    }
    console.error('Error in streamChatMessage main try-catch:', error);
    onError?.(error instanceof Error ? error : new Error('An unexpected error occurred during chat streaming.'));
  }
}

// Interrupt a running generation
export const interruptGeneration = async (generationId: string, chatId: string) => {
  const url = getApiUrl(`/chats/${chatId}/interrupt?generation_id=${encodeURIComponent(generationId)}`);
  const response = await fetch(url, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to interrupt generation: ${response.statusText}`);
  }
  return response.json();
}