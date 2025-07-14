import { create } from "zustand"
import { persist } from "zustand/middleware"
import type { Message, Chat, FileInfo } from "./types"
import * as api from "./api-service"
import { produce } from "immer"

interface StagedFile {
  id: string; // Unique ID for the staged file instance
  file: File; // The actual File object
}

interface StoreState {
  messages: Message[]
  chats: Chat[]
  activeChat: string | null
  isSidebarOpen: boolean
  isGenerating: boolean
  generationId: string | null
  stagedFiles: StagedFile[]
  generationAbortController?: AbortController | null
  isAnimating: boolean   // Track if typewriter animation is ongoing

  // Actions
  addMessage: (message: Message) => void
  updateMessage: (id: string, contentOrUpdater: string | ((message: Message) => Message)) => void
  clearChat: () => Promise<void>
  createNewChat: () => Promise<string>
  setActiveChat: (chatId: string | null) => Promise<void>
  deleteChat: (chatId: string) => Promise<void>
  renameChat: (chatId: string, newName: string) => Promise<void>
  toggleSidebar: () => void
  stopGeneration: () => void
  addStagedFile: (file: File) => void
  removeStagedFile: (fileId: string) => void
  clearStagedFiles: () => void
  loadChats: () => Promise<void>
  setGenerationAbortController: (controller: AbortController | null) => void
  setIsAnimating: (value: boolean) => void   // Setter for animation state
  updateChatNameOptimistically: (chatId: string, newName: string) => void
  regenerateMessage: (chatId: string, messageId: string) => Promise<void>
  editMessage: (chatId: string, messageId: string, newContent: string) => Promise<void>
}

// Message update queue to batch updates
let messageUpdateQueue: {id: string, content: string}[] = [];
let messageUpdateTimeout: NodeJS.Timeout | null = null;
const MESSAGE_UPDATE_BATCH_INTERVAL = 100; // ms

export const useStore = create<StoreState>()(
  persist(
    (set, get) => ({
      messages: [],
      chats: [],
      activeChat: null,
      isSidebarOpen: true,
      isGenerating: false,
      generationId: null,
      stagedFiles: [],
      generationAbortController: null,
      isAnimating: false,

      addMessage: (message: Message) => {
        set(produce((draft: StoreState) => {
          // If message has an ID, try to find and update it (for streaming)
          if (message.id) {
            const existingMessageIndex = draft.messages.findIndex(m => m.id === message.id);
            if (existingMessageIndex !== -1) {
              // Preserve existing files if the new message object doesn't explicitly provide them
              const existingFiles = draft.messages[existingMessageIndex].files;
              draft.messages[existingMessageIndex] = {
                ...draft.messages[existingMessageIndex],
                ...message,
                files: message.files || existingFiles, // Prioritize new files, fallback to existing
              };
              return; // Exit after update
            }
          }
          // If no ID or not found, add as new message
          // Ensure files array is at least initialized if not provided
          draft.messages.push({ ...message, files: message.files || [] });
        }));
      },
      
      updateMessage: (id: string, contentOrUpdater: string | ((message: Message) => Message)) => {
        set(produce((draft: StoreState) => {
          const messageIndex = draft.messages.findIndex(m => m.id === id);
          if (messageIndex !== -1) {
            if (typeof contentOrUpdater === 'function') {
              draft.messages[messageIndex] = contentOrUpdater(draft.messages[messageIndex]);
            } else {
              draft.messages[messageIndex].content = contentOrUpdater;
            }
            // IfisLoading was true, set it to false on update
            if (draft.messages[messageIndex].isLoading) {
              draft.messages[messageIndex].isLoading = false;
            }
          }
        }));
      },

      clearChat: async () => {
        const { activeChat } = get();
        if (activeChat) {
          try {
            await api.deleteChat(activeChat); // API call to delete on backend
            set(produce((draft: StoreState) => {
              draft.chats = draft.chats.filter(chat => chat.id !== activeChat);
              // Always reset to initial app state with no active chat
              draft.activeChat = null;
              draft.messages = [];
              draft.stagedFiles = [];
            }));
          } catch (error) {
            console.error("Failed to delete chat:", error);
            // Optionally show an error to the user
          }
        }
      },

      createNewChat: async () => {
        try {
          const newChatFromApi = await api.createChat();
          const newChat: Chat = {
            id: newChatFromApi.id,
            // Attempt to use name, then title, then default for flexibility
            name: (newChatFromApi as any).name || (newChatFromApi as any).title || "New Chat",
            messages: [],
          };
          set(produce((draft: StoreState) => {
            draft.chats.unshift(newChat); // Add to the beginning of the list
            draft.activeChat = newChat.id;
            draft.messages = []; // Clear messages for the new chat
            draft.stagedFiles = []; // Clear staged files for new chat
          }));
          return newChat.id;
        } catch (error) {
          console.error("Failed to create new chat:", error);
          throw error; // Re-throw to be handled by UI
        }
      },

      setActiveChat: async (chatId: string | null) => {
        if (chatId === get().activeChat && chatId !== null) return; // Avoid reloading if already active
        set({ stagedFiles: [] }); // Clear staged files when changing chat
        if (chatId) {
          try {
            const chat = await api.getChat(chatId);
            set(produce((draft: StoreState) => {
              draft.activeChat = chatId;
              draft.messages = chat?.messages || [];
            }));
          } catch (error) {
            console.error("Failed to fetch messages for chat:", chatId, error);
            set({ activeChat: chatId, messages: [] }); // Set active chat but with empty messages on error
          }
        } else {
          set({ activeChat: null, messages: [] }); // Clearing active chat
        }
      },

      deleteChat: async (chatId: string) => {
        try {
          await api.deleteChat(chatId);
          set(produce((draft: StoreState) => {
            const initialActiveChat = draft.activeChat;
            draft.chats = draft.chats.filter(c => c.id !== chatId);
            if (initialActiveChat === chatId) { // If the deleted chat was active
              // Set to initial page status instead of loading previous chat
              draft.activeChat = null;
              draft.messages = [];
            }
          }));
        } catch (error) {
          console.error("Failed to delete chat:", chatId, error);
        }
      },

      renameChat: async (chatId: string, newName: string) => {
        try {
          const updatedChat = await api.renameChat(chatId, newName);
          set(produce((draft: StoreState) => {
            const chat = draft.chats.find(c => c.id === chatId);
            if (chat) {
              chat.name = updatedChat.name || updatedChat.title || newName;
            }
          }));
        } catch (error) {
          console.error("Failed to rename chat:", chatId, error);
        }
      },
      updateChatNameOptimistically: (chatId: string, newName: string) => {
        set(produce((draft: StoreState) => {
          const chat = draft.chats.find(c => c.id === chatId);
          if (chat) {
            chat.name = newName;
          }
        }));
      },

      toggleSidebar: () => set(state => ({ isSidebarOpen: !state.isSidebarOpen })),
      
      stopGeneration: () => {
        get().generationAbortController?.abort();
        set({ isGenerating: false, isAnimating: false, generationAbortController: null, generationId: null });
      },

      addStagedFile: (file: File) => {
        const newStagedFile: StagedFile = { id: crypto.randomUUID(), file };
        set(produce((draft: StoreState) => {
          if (draft.stagedFiles.length < 5) { // Max 5 files check
            draft.stagedFiles.push(newStagedFile);
          } else {
            // Optionally, add a way to notify user from store, or handle in component
            console.warn("Maximum number of staged files reached.");
          }
        }));
      },
      removeStagedFile: (fileId: string) => {
        set(produce((draft: StoreState) => {
          draft.stagedFiles = draft.stagedFiles.filter(sf => sf.id !== fileId);
        }));
      },
      clearStagedFiles: () => set({ stagedFiles: [] }),

      loadChats: async () => {
        try {
          const chatsFromApi = await api.getChats();
          set(produce((draft: StoreState) => {
            draft.chats = chatsFromApi.map(c => ({
              id: c.id,
              name: c.name || (c as any).title || "Chat", // Prefer name from Chat type, fallback to title if API uses that
              messages: c.messages || [],
            }));
            // If no active chat and chats are loaded, set the first one as active
            // And load its messages
            if (!draft.activeChat && draft.chats.length > 0) {
              const firstChatId = draft.chats[0].id;
              draft.activeChat = firstChatId;
              // Trigger message loading for the new active chat
              // This requires setActiveChat to be callable here or duplicate logic
              // For now, messages might not be loaded here, setActiveChat should handle it.
            }
          }));
          // If an active chat is set after loading, fetch its messages
          const currentActiveChat = get().activeChat;
          if (currentActiveChat) {
            await get().setActiveChat(currentActiveChat); // This will load messages
          }

        } catch (error) {
          console.error("Failed to load chats:", error);
          set({ chats: [] }); // Clear chats on error
        }
      },
      
      setGenerationAbortController: (controller: AbortController | null) => set({ generationAbortController: controller }),
      setIsAnimating: (value: boolean) => set({ isAnimating: value }),

      // Implementations for missing actions
      regenerateMessage: async (chatId: string, messageId: string) => {
        console.warn("regenerateMessage action called but not fully implemented. Needs API integration.");
        // Placeholder: Find the message, set its content to 'Regenerating...' and trigger API call
        // This would likely involve calling an API endpoint similar to streamChatMessage
        const messageToRegenerate = get().messages.find(m => m.id === messageId);
        if (!messageToRegenerate || messageToRegenerate.role !== 'user') {
          console.error("Cannot regenerate: User message not found or not a user message.");
          return;
        }
        // Example: reuse streamChatMessage logic or a dedicated regeneration endpoint
        // For now, just log and perhaps set a loading state on the assistant's next message
      },
      editMessage: async (chatId: string, messageId: string, newContent: string) => {
        console.warn("editMessage action called but not fully implemented. Needs API integration.");
        // Placeholder: Update user message optimistically, then call backend to resubmit/get new AI response
        set(produce((draft: StoreState) => {
          const message = draft.messages.find(m => m.id === messageId && m.role === 'user');
          if (message) {
            message.content = newContent;
            // Potentially remove subsequent assistant messages and trigger a new response generation
          }
        }));
      },

    }),
    {
      name: "ai-math-chatbot-storage", // name of the item in the storage (must be unique)
      // partialize: (state) => ({ activeChat: state.activeChat, chats: state.chats }), // Persist only specific parts
      // For now, persist most things and handle migration/invalidation if structure changes drastically
    }
  )
)

// Helper to get the current active chat object
export const useActiveChat = () => {
  return useStore(state => state.chats.find(chat => chat.id === state.activeChat))
}

// Hook to manage message streaming and updates
// This is a conceptual hook, the actual implementation for streaming is more involved
// and likely happens within the component that triggers the generation (e.g., chat input or page)
