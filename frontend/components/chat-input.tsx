"use client"

import type React from "react"
import { useState, useRef, useEffect, useCallback } from "react"
import { Paperclip, Mic, ArrowUp, X, StopCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useStore } from "@/lib/store"
import { cn, debounce } from "@/lib/utils"
import { useToast } from "@/hooks/use-toast"
import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { uploadFile, streamChatMessage } from "@/lib/api-service"
import { produce } from "immer"

const PLACEHOLDER_TEXTS = [
  "Ask anything",
  "What is the integral of arctan(x)?",
  "How do you factor x^3 - 1?",
  "What is the Taylor series for e^x?",
  "Explain the difference between permutation and combination.",
  "What is the sum of the first 100 natural numbers?",
  "How do you find the area under a curve?",
]

export default function ChatInput() {
  const [input, setInput] = useState("")
  const [placeholder, setPlaceholder] = useState(PLACEHOLDER_TEXTS[0])
  const [showRecordingModal, setShowRecordingModal] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const sendButtonRef = useRef<HTMLButtonElement>(null)
  const stopButtonRef = useRef<HTMLButtonElement>(null)
  const { toast } = useToast()
  const { 
    addMessage, 
    isGenerating, 
    isAnimating, 
    stopGeneration, 
    setIsAnimating, 
    messages, 
    activeChat,
    createNewChat, 
    generationId,
    stagedFiles,
    addStagedFile,
    removeStagedFile,
    clearStagedFiles
  } = useStore()
  const isCentered = messages.length === 0

  // Cycle through placeholder texts only when there are no messages
  useEffect(() => {
    if (isCentered) {
      const interval = setInterval(() => {
        setPlaceholder((prev) => {
          const currentIndex = PLACEHOLDER_TEXTS.indexOf(prev)
          const nextIndex = (currentIndex + 1) % PLACEHOLDER_TEXTS.length
          return PLACEHOLDER_TEXTS[nextIndex]
        })
      }, 5000)
      return () => clearInterval(interval)
    } else {
      setPlaceholder("Type your message...")
    }
  }, [isCentered])

  // Auto-resize textarea - debounced for performance
  const resizeTextarea = useCallback(
    () => {
      if (textareaRef.current) {
        const scrollPos = window.scrollY;
        
        // Save the current scroll position of the textarea
        const textareaScrollTop = textareaRef.current.scrollTop;

        // Reset height to auto to allow scrollHeight calculation
        textareaRef.current.style.height = 'auto';

        // Get the actual minimum height applied by CSS (min-h-[56px] + padding)
        const minHeight = textareaRef.current.clientHeight;

        // Calculate content height after resetting to auto
        const contentHeight = textareaRef.current.scrollHeight;

        // If content height exceeds the minimum height, set height to content height (capped at max height)
        if (contentHeight > minHeight) {
          const newHeight = Math.min(contentHeight, 184);
          textareaRef.current.style.height = `${newHeight}px`;
        } else {
          // If content height is less than or equal to minHeight, ensure the minHeight is applied
          textareaRef.current.style.height = `${minHeight}px`;
        }

        // Restore the textarea's scroll position
        textareaRef.current.scrollTop = textareaScrollTop;
        
        // Restore window scroll position
        window.scrollTo(0, scrollPos);
      }
    }, 
    [textareaRef]
  );

  // Focus textarea on mount and after generation completes
  useEffect(() => {
    textareaRef.current?.focus()
  }, [])
  useEffect(() => {
    if (!isGenerating && !showRecordingModal) {
      textareaRef.current?.focus()
    }
  }, [isGenerating, showRecordingModal])

  // Focus stop button when generation starts
  useEffect(() => {
    if (isGenerating) {
      stopButtonRef.current?.focus()
    }
  }, [isGenerating])

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || [])
    if (selectedFiles.length === 0) return

    // Validate and add files, up to 5
    const validTypes = [
      "application/pdf",
      "image/png",
      "image/jpeg",
      "image/webp",
      "image/heic",
      "image/heif",
      "text/plain",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]

    for (const selectedFile of selectedFiles) {
      if (stagedFiles.length >= 5) {
        toast({
          title: "Too many files",
          description: "Maximum 5 files per prompt.",
          variant: "destructive",
        })
        break
      }
      if (!validTypes.includes(selectedFile.type)) {
        toast({
          title: "Unsupported file type",
          description: "Please upload a PDF, image, text, or Word document.",
          variant: "destructive",
        })
        continue
      }
      if (selectedFile.size > 20 * 1024 * 1024) {
        toast({
          title: "File too large",
          description: "Maximum file size is 20MB for direct inclusion.",
          variant: "destructive",
        })
        continue
      }
      addStagedFile(selectedFile)
    }
    if (fileInputRef.current) {
        fileInputRef.current.value = "";
    }
    textareaRef.current?.focus()
  }

  const handleSubmit = async () => {
    if (isGenerating || isAnimating) return
    if (!input.trim() && stagedFiles.length === 0) return

    setIsAnimating(true)
    const currentInput = input.trim()
    const currentStagedFiles = [...stagedFiles]

    setInput("")

    const currentChatId = activeChat || await createNewChat()
    if (!currentChatId) {
      toast({
        title: "Error",
        description: "Could not create or find chat.",
        variant: "destructive",
      })
      setIsAnimating(false)
      return
    }

    const userMessageId = crypto.randomUUID()
    const aiMessageId = crypto.randomUUID()
    const localGenerationId = crypto.randomUUID() // Renamed to avoid confusion with store's generationId

    // Set generating states in the store before starting the API call
    const abortController = new AbortController();
    useStore.setState({ 
      isGenerating: true, 
      isAnimating: true, // Ensure animation state is also set to true from the start
      generationId: localGenerationId, 
      generationAbortController: abortController 
    });

    addMessage({
      id: userMessageId,
      role: "user",
      content: currentInput,
      files: currentStagedFiles.map(sf => ({
        file_id: sf.id,
        filename: sf.file.name,
        content_type: sf.file.type,
        size: sf.file.size,
      })),
    })

    // If this is a new chat and the chat name is still default, rename it to the first user message
    const chat = useStore.getState().chats.find(c => c.id === currentChatId);
    if (chat && (chat.name === "New Chat" || chat.name === "new chat")) {
      // Use up to 40 characters of the user's message as the chat name
      const newName = currentInput.slice(0, 40) + (currentInput.length > 40 ? "..." : "");
      useStore.getState().renameChat(currentChatId, newName);
    }

    // Add empty AI message placeholder
    addMessage({
      id: aiMessageId,
      role: "assistant",
      content: "Thinking...", // Show loading indicator
      files: [],
      isLoading: true,
      isAnimating: true, // Start animating for this message
    })

    try {
      const fileObjectsForApi = currentStagedFiles.map(sf => sf.file)

      // Define callbacks for streamChatMessage
      const handleChunk = (chunk: string) => {
        useStore.setState(produce((state: ReturnType<typeof useStore.getState>) => {
          const msgIndex = state.messages.findIndex(m => m.id === aiMessageId);
          if (msgIndex !== -1) {
            // Defensive: If chunk is JSON, extract text
            let textChunk = chunk;
            try {
              const parsed = JSON.parse(chunk);
              if (typeof parsed === 'object' && parsed.text) {
                textChunk = parsed.text;
              }
            } catch { /* not JSON, use as-is */ }

            if (state.messages[msgIndex].content === "Thinking...") {
              state.messages[msgIndex].content = textChunk;
              state.messages[msgIndex].isLoading = false;
            } else {
              state.messages[msgIndex].content += textChunk;
            }
            state.messages[msgIndex].isAnimating = true; // Animate this message
            // Ensure isGenerating and isAnimating both remain true during streaming
            state.isGenerating = true;
            state.isAnimating = true;
          }
        }));
      };

      const handleError = (error: Error) => {
        console.error("Streaming error callback:", error)
        useStore.setState(produce((state: ReturnType<typeof useStore.getState>) => {
          const msgIndex = state.messages.findIndex(m => m.id === aiMessageId);
          if (msgIndex !== -1) {
            state.messages[msgIndex].content = `Error: ${error.message || "An unknown error occurred"}`;
            state.messages[msgIndex].isLoading = false;
            state.messages[msgIndex].isError = true;
          }
          state.isGenerating = false;
          state.isAnimating = false; // Ensure animation stops on error
          state.generationId = null; 
          state.generationAbortController = null;
        }));
        toast({
          title: "Error generating response",
          description: error.message || "An unknown error occurred",
          variant: "destructive",
        })
      };

      const handleDone = () => {
        useStore.setState(produce((state: ReturnType<typeof useStore.getState>) => {
          const msgIndex = state.messages.findIndex(m => m.id === aiMessageId);
          if (msgIndex !== -1) {
            // Mark message as no longer loading - indicates streaming is complete
            state.messages[msgIndex].isLoading = false;
            
            // If animation has already completed (isAnimating is false), we can also reset generation state
            if (!state.isAnimating) {
              state.isGenerating = false;
              state.generationId = null;
              state.generationAbortController = null;
            }
            // Otherwise, animation completion will handle resetting isGenerating
            // when it detects streaming is complete (isLoading is false)
          }
        }));
        clearStagedFiles()
        if (textareaRef.current) { // Refocus and resize
          textareaRef.current.value = "";
          textareaRef.current.style.height = 'auto';
          resizeTextarea();
        }
      };
      
      await streamChatMessage(
        currentChatId,       // chatId: string
        currentInput,        // message: string (user's text content)
        fileObjectsForApi,   // files?: File[]
        handleChunk,         // onChunk?: (chunk: string) => void
        handleError,         // onError?: (error: Error) => void
        handleDone           // onDone?: () => void
      );

    } catch (error: any) { // Catch errors from the setup of streamChatMessage itself, if any
      console.error("Error setting up streamChatMessage:", error)
      useStore.setState(produce((state: ReturnType<typeof useStore.getState>) => {
        const msgIndex = state.messages.findIndex(m => m.id === aiMessageId);
        if (msgIndex !== -1 && state.messages[msgIndex].isLoading) {
            state.messages[msgIndex].content = `Error: ${error.message || "Failed to start stream"}`;
            state.messages[msgIndex].isLoading = false;
            state.messages[msgIndex].isError = true;
        }
        state.isGenerating = false;
        state.isAnimating = false;
        state.generationId = null; 
        state.generationAbortController = null; // Also clear controller here
      }));
      toast({
        title: "Error starting stream",
        description: error.message || "An unknown error occurred",
        variant: "destructive",
      });
      // Ensure textarea is cleared and focusable
      if (textareaRef.current) {
        textareaRef.current.value = "";
        textareaRef.current.style.height = 'auto';
        resizeTextarea();
      }
    }
  }

  const handleStop = async () => {
    if (!(isGenerating || isAnimating)) return
    // Stop both generation and animation
    useStore.setState({ 
      isGenerating: false,
      isAnimating: false 
    })
    try {
      await stopGeneration()
      // Update all currently animating messages to stop their animation
      useStore.setState(produce((state: ReturnType<typeof useStore.getState>) => {
        state.messages.forEach(msg => {
          if (msg.isAnimating) {
            msg.isAnimating = false;
          }
        });
      }));
    } catch (err: any) {
      toast({
        title: "Failed to stop generation",
        description: err?.message || "Could not stop the model response.",
        variant: "destructive",
      })
    } finally {
      textareaRef.current?.focus()
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      if (isGenerating) {
        handleStop()
      } else {
        handleSubmit()
      }
    }
  }

  return (
    <div className={cn("relative mx-auto w-full max-w-3xl", isCentered ? "mt-4" : "")}>
      <div className="relative flex flex-col rounded-3xl border border-neutral-300 dark:border-neutral-700 shadow-input-bar bg-background dark:bg-accent">
        {/* Text input - spans full width */}
        <div className="w-full overflow-hidden max-h-[184px]">
          {stagedFiles.length > 0 && (
            <div className="flex items-center px-3 pt-2">
              {stagedFiles.map((stagedFile) => (
                <Badge key={stagedFile.id} className="flex items-center gap-1 bg-primary/20 text-primary">
                  {stagedFile.file.name}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-4 w-4 p-0 hover:bg-primary/20"
                    onClick={() => removeStagedFile(stagedFile.id)}
                    aria-label={`Remove ${stagedFile.file.name}`}
                  >
                    <X className="h-3 w-3 text-opacity-100" />
                  </Button>
                </Badge>
              ))}
            </div>
          )}
          <div className="w-full overflow-y-auto max-h-[184px] chat-textarea-wrapper">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              resizeTextarea(); // Called directly on change
            }}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className="w-full resize-none border-0 bg-transparent px-4 py-3.5 focus-visible:ring-0 focus-visible:ring-offset-0 text-base custom-textarea rounded-3xl"
            rows={1}
            aria-label="Chat input"
            autoFocus
          />
          </div>
        </div>

        {/* Bottom toolbar with icons */}
        <div className="custom-input-bar flex items-center justify-between px-2 py-2 -mt-2">
          {/* Left side icons */}
          <div className="flex gap-2">
            {/* File upload button */}
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    className="h-10 w-10 rounded-full border border-neutral-300 dark:border-neutral-600 bg-background dark:bg-accent text-primary hover:text-primary"
                    onClick={() => fileInputRef.current?.click()}
                    aria-label="Attach file"
                    disabled={isGenerating || stagedFiles.length >= 5}
                  >
                    <Paperclip className="h-5 w-5" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Attach file (max 5)</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>

          {/* Right side - Send/Stop button */}
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  ref={isGenerating || isAnimating ? stopButtonRef : sendButtonRef}
                  type="button"
                  variant="outline"
                  size="icon"
                  className={cn(
                    "h-10 w-10 rounded-full border border-neutral-300 dark:border-neutral-600",
                    input.trim() || stagedFiles.length > 0
                      ? "bg-primary text-primary-foreground hover:bg-primary/90"
                      : "bg-background dark:bg-accent text-primary",
                    (isGenerating || isAnimating) && "bg-destructive text-destructive-foreground hover:bg-destructive/90",
                  )}
                  onClick={isGenerating || isAnimating ? handleStop : handleSubmit}
                  disabled={
                    ((!input.trim() && stagedFiles.length === 0) && !(isGenerating || isAnimating)) ||
                    (isGenerating && !generationId)
                  }
                  aria-label={(isGenerating || isAnimating) ? "Stop generating" : "Send message"}
                  tabIndex={0}
                >
                  {(isGenerating || isAnimating) ? (
                    <div className="flex !h-10 !w-10 items-center justify-center">
                      <svg
                        className="!h-10 !w-10 animate-spin"
                        viewBox="0 0 24 24"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                        stroke="currentColor"
                        strokeWidth={1}
                        aria-hidden="true"
                      >
                        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1" />
                        <rect x="8" y="8" width="8" height="8" rx="1.5" fill="currentColor" />
                      </svg>
                    </div>
                  ) : (
                    <ArrowUp className="h-5 w-5" />
                  )}
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{(isGenerating || isAnimating) ? "Stop generating" : "Send message"}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>

      {/* Visually hidden file input for uploads */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,image/*,.txt,.docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        className="hidden-file-input"
        onChange={handleFileChange}
        tabIndex={-1}
        aria-hidden="true"
      />
    </div>
  )
}
