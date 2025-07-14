"use client"

import { useState, useRef, useEffect } from "react"
import { Copy, Check, RotateCcw, Pencil } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { Message } from "@/lib/types"
import { useStore } from "@/lib/store"
import { useToast } from "@/hooks/use-toast"
import "katex/dist/katex.min.css"
import { cn } from "@/lib/utils"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import MarkdownRenderer from "./markdown-renderer"
import React from "react"
import { useAnimatedText } from "@/components/ui/animated-text"

interface ChatMessageProps {
  message: Message
}

// Typing indicator animation component
const SequentialThinking = () => {
  const [dots, setDots] = React.useState('');
  React.useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => (prev.length >= 3 ? '' : prev + '.'));
    }, 500);  // Adjust interval for speed
    return () => clearInterval(interval);
  }, []);
  return <div className="flex items-center space-x-2"> <div className="text-primary italic">Thinking{dots}</div> </div>;
}

export default React.memo(function ChatMessage({ message }: ChatMessageProps) {
  const { role, content, isLoading, isError } = message
  const { regenerateMessage, editMessage, setIsAnimating, isAnimating, activeChat } = useStore()
  const [lastAnimatedContent, setLastAnimatedContent] = useState("")
  // Prepare animated content and conditionally display based on animation state
  const rawAnimatedContent = useAnimatedText(content, {
    delimiter: "",
    charSpeed: 80,
    prevText: lastAnimatedContent,
    onFinish: () => {
      setLastAnimatedContent(content);
      if (message.id) {
        // Set isAnimating to false for this message only but keep isGenerating true
        // to maintain the stop button until user explicitly stops
        useStore.setState((state: any) => {
          const msgIndex = state.messages.findIndex((m: any) => m.id === message.id);
          if (msgIndex !== -1) {
            const newMessages = [...state.messages];
            newMessages[msgIndex] = { ...newMessages[msgIndex], isAnimating: false };
            
            // Check if streaming has also completed - if isLoading is false and the message is not "Thinking..."
            const isStreamingComplete = !newMessages[msgIndex].isLoading && newMessages[msgIndex].content !== "Thinking...";
            
            // Check if this is the latest message from the assistant
            const isLatestAssistantMessage = state.messages
              .filter((m: Message) => m.role === "assistant" || m.role === "model")
              .findIndex((m: Message) => m.id === message.id) === 
              state.messages.filter((m: Message) => m.role === "assistant" || m.role === "model").length - 1;
            
            // Only reset generation state if this is the latest message and streaming is complete
            if (isLatestAssistantMessage && isStreamingComplete) {
              return { 
                ...state, 
                messages: newMessages,
                isAnimating: false,
                isGenerating: false, // Reset generation state when streaming and animation are both complete
                generationId: null,
                generationAbortController: null
              };
            }
            
            // Otherwise just update the animation state for this message
            return { 
              ...state, 
              messages: newMessages,
              isAnimating: false
            };
          }
          return state;
        });
      }
    }
  });
  const animatedContent = message.isAnimating ? rawAnimatedContent : content
  const [copied, setCopied] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [editedContent, setEditedContent] = useState(content)
  const messageRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const { toast } = useToast()
  
  // Add visible cursor effect for streaming responses
  const [showCursor, setShowCursor] = useState(isLoading)
  
  // Show cursor during loading, hide when done
  useEffect(() => {
    if (isLoading) {
      setShowCursor(true)
    } else {
      // Keep cursor visible briefly after loading completes for a smooth transition
      const timer = setTimeout(() => {
        setShowCursor(false)
      }, 500)
      return () => clearTimeout(timer)
    }
  }, [isLoading])

  // Auto-resize textarea when editing
  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.style.height = "auto"
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
      textareaRef.current.focus()
    }
  }, [isEditing])

  // Auto-scroll to this message on content change only if user isn't scrolling up
  useEffect(() => {
    // Skip all auto-scrolling for user messages - they are handled separately
    if (role === "user") return;
    
    let isUserScrollingUp = false;
    let lastScrollTop = window.scrollY;
    const handleScroll = () => {
      const currentScrollTop = window.scrollY;
      if (currentScrollTop < lastScrollTop) {
        isUserScrollingUp = true;
      }
      lastScrollTop = currentScrollTop;
    };
    window.addEventListener('scroll', handleScroll);
    
    // Only auto-scroll for AI messages when appropriate
    if (messageRef.current && !isUserScrollingUp) {
      messageRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
    
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [animatedContent, isLoading, role]);

  const handleCopy = () => {
    navigator.clipboard.writeText(content)
    setCopied(true)
    toast({
      description: "Copied!",
      duration: 1500,
    })
    setTimeout(() => setCopied(false), 1500)
  }

  const handleRegenerate = () => {
    if (activeChat && message.id) {
      regenerateMessage(activeChat, message.id)
    } else {
      console.error("Cannot regenerate: activeChat or message.id is missing.")
      toast({
        title: "Error",
        description: "Could not regenerate message. Chat or Message ID missing.",
        variant: "destructive",
      })
    }
  }

  const handleEdit = () => {
    setIsEditing(true)
  }

  const handleSaveEdit = () => {
    if (activeChat && message.id) {
      editMessage(activeChat, message.id, editedContent)
      setIsEditing(false)
    } else {
      console.error("Cannot save edit: activeChat or message.id is missing.")
      toast({
        title: "Error",
        description: "Could not save edited message. Chat or Message ID missing.",
        variant: "destructive",
      })
    }
  }

  const handleCancelEdit = () => {
    setEditedContent(content)
    setIsEditing(false)
  }

  // Extract file names from content if present
  const fileMatches = Array.from(content.matchAll(/\[File: (.*?)\]/g))
  const fileNames = role === "user" ? fileMatches.map((m) => m[1]) : []
  const displayContent = content.replace(/\[File: (.*?)\]/g, "")

  // Modify the chat message component to adjust positioning and styling
  return (
    <div className={cn("mb-6 flex animate-fadeIn", role === "user" ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "relative",
          role === "user" ? "max-w-3xl" : "max-w-[calc(100%-2rem)] md:max-w-[calc(100%-4rem)] xl:max-w-4xl",
        )}
      >
        {/* User message */}
        {role === "user" && (
          <div className="group relative" data-message-id={message.id} data-message-role="user">
            <div className="rounded-3xl bg-primary/10 dark:bg-accent p-4 shadow-sm transition-all duration-200 hover:shadow-md">
              {isEditing ? (
                <div className="flex flex-col gap-2">
                  <textarea
                    aria-label="Edit message content"
                    ref={textareaRef}
                    value={editedContent}
                    onChange={(e) => setEditedContent(e.target.value)}
                    className="min-h-[24px] w-full resize-none rounded-md border bg-background p-1"
                    autoFocus
                  />
                  <div className="flex justify-end gap-2">
                    <Button variant="outline" size="sm" onClick={handleCancelEdit}>
                      Cancel
                    </Button>
                    <Button size="sm" onClick={handleSaveEdit}>
                      Save
                    </Button>
                  </div>
                </div>
              ) : (
                <>
                  <p className="text-base text-foreground">{displayContent}</p>
                  {fileNames.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-2">
                      {fileNames.map((name) => (
                        <span key={name} className="rounded-md bg-primary/20 px-2 py-1 text-xs font-medium text-primary">
                          File: {name}
                        </span>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
            {!isEditing && (
              <div className="mt-2 flex justify-end gap-1">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 rounded-full"
                        onClick={handleCopy}
                        aria-label="Copy message"
                      >
                        {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Copy message</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>

                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 rounded-full"
                        onClick={handleEdit}
                        aria-label="Edit message"
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Edit message</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>

                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 rounded-full"
                        onClick={handleRegenerate}
                        aria-label="Regenerate response"
                      >
                        <RotateCcw className="h-4 w-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Regenerate response</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            )}
          </div>
        )}

        {/* AI message */}
        {(role === "assistant" || role === "model") && (
          <div
            className={cn(
              "group relative p-4 transition-all duration-200"
            )}
            data-message-id={message.id}
            data-message-role="assistant"
            ref={messageRef}
          >
            {content === "Thinking..." ? (
              <SequentialThinking />
            ) : (
              <div className="relative">
                <MarkdownRenderer content={animatedContent} />
                {showCursor && (
                  <span className="cursor-blink" />
                )}
              </div>
            )}
            {!isLoading && (
              <div className="mt-2 flex justify-start gap-1">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 rounded-full"
                        onClick={handleCopy}
                        aria-label="Copy message"
                      >
                        {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Copy message</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>

                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 rounded-full"
                        onClick={handleRegenerate}
                        aria-label="Regenerate response"
                      >
                        <RotateCcw className="h-4 w-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Regenerate response</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
})
