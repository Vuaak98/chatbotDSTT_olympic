"use client"

import { useState, useEffect, useMemo } from "react"
import { X, Edit2, Trash2, BookOpen, History, Search } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useStore } from "@/lib/store"
import { cn } from "@/lib/utils"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { useMediaQuery } from "@/hooks/use-media-query"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useToast } from "@/hooks/use-toast"

// Custom NewChatIcon component
const NewChatIcon = () => (
  <svg 
    width="24" 
    height="24" 
    viewBox="0 0 24 24" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg" 
    className="h-5 w-5"
  >
    <path 
      d="M11 2H9C4 2 2 4 2 9V15C2 20 4 22 9 22H15C20 22 22 20 22 15V13" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
    <path 
      d="M16.04 3.02001L8.16 10.9C7.86 11.2 7.56 11.79 7.5 12.22L7.07 15.23C6.91 16.32 7.68 17.08 8.77 16.93L11.78 16.5C12.2 16.44 12.79 16.14 13.1 15.84L20.98 7.96001C22.34 6.60001 22.98 5.02001 20.98 3.02001C18.98 1.02001 17.4 1.66001 16.04 3.02001Z" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeMiterlimit="10" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
    <path 
      d="M14.91 4.1499C15.58 6.5399 17.45 8.4099 19.85 9.0899" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeMiterlimit="10" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
  </svg>
)

// Custom SidebarIcon component
const SidebarIcon = () => (
  <svg 
    width="24" 
    height="24" 
    viewBox="0 0 24 24" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg" 
    className="h-5 w-5"
  >
    {/* Outer rounded rectangle */}
    <path 
      d="M6 5 L15 5 A3 3 0 0 1 18 8 L18 16 A3 3 0 0 1 15 19 L6 19 A3 3 0 0 1 3 16 L3 8 A3 3 0 0 1 6 5 Z" 
      stroke="currentColor" 
      strokeWidth="1.5" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
    
    {/* Vertical divider */}
    <path 
      d="M9 5 V 19" 
      stroke="currentColor" 
      strokeWidth="1.5" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
    
    {/* Left panel indicators (pill-shaped) */}
    <path 
      d="M5.5 8.5 H 6.5" 
      stroke="currentColor" 
      strokeWidth="1.5" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
    <path 
      d="M5.5 11.5 H 6.5" 
      stroke="currentColor" 
      strokeWidth="1.5" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
  </svg>
)

export default function Sidebar() {
  const {
    chats,
    activeChat,
    setActiveChat,
    createNewChat,
    renameChat,
    deleteChat,
    isSidebarOpen,
    toggleSidebar,
    loadChats,
  } = useStore()
  const [chatToDelete, setChatToDelete] = useState<string | null>(null)
  const [isRenaming, setIsRenaming] = useState<string | null>(null)
  const [newName, setNewName] = useState("")
  const [searchQuery, setSearchQuery] = useState("")
  const [isSearchActive, setIsSearchActive] = useState(false)
  const isDesktop = useMediaQuery("(min-width: 768px)")
  const { toast } = useToast()

  // Load chat sessions when the sidebar is mounted
  useEffect(() => {
    let mounted = true;
    
    const initializeChats = async () => {
      try {
        await loadChats();
        
        // Only create a new chat if specifically requested,
        // not automatically on mount or reload
        // The loadChats function in the store handles setting 
        // the active chat from local storage or the most recent chat
      } catch (error) {
        console.error("Failed to load chats:", error);
        
        // Only attempt to create a new chat if loading failed AND we're still mounted
        if (mounted) {
          try {
            await createNewChat();
            toast({
              title: "Created New Chat",
              description: "Couldn't load existing chats, so we've created a new one for you.",
              variant: "default",
            });
          } catch (createError) {
            console.error("Failed to create fallback chat:", createError);
            toast({
              title: "Error",
              description: "Failed to load or create chats. Please refresh the page.",
              variant: "destructive",
            });
          }
        }
      }
    };
    
    initializeChats();
    
    // Cleanup function to prevent state updates after unmount
    return () => {
      mounted = false;
    };
    
  }, [loadChats, createNewChat, toast]);

  const handleNewChat = async () => {
    try {
      await createNewChat()
      setIsRenaming(null)
      if (!isDesktop && isSidebarOpen) {
        toggleSidebar()
      }
      toast({
        title: "New Chat Created",
        description: "Started a new conversation.",
        variant: "success",
        duration: 2000,
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create new chat. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleTitleClick = async () => {
    try {
      // Set to initial status page: no active chat, clear messages
      await setActiveChat(null);
      setIsRenaming(null);
      if (!isDesktop && isSidebarOpen) {
        toggleSidebar();
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Could not navigate to home. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleSelectChat = async (chatId: string) => {
    if (chatId === activeChat) {
      if (!isDesktop) {
        toggleSidebar()
      }
      return;
    }

    try {
      await setActiveChat(chatId)
      if (!isDesktop) {
        toggleSidebar()
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load chat. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleRenameSubmit = async (e: React.FormEvent, chatId: string, newName: string) => {
    e.preventDefault()
    if (newName.trim() === "") return
    
    try {
      await renameChat(chatId, newName.trim())
      setIsRenaming(null)
      toast({
        title: "Chat Renamed",
        description: "The chat has been renamed successfully.",
        variant: "success",
        duration: 2000,
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to rename chat. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleDeleteChat = async (chatId: string) => {
    try {
      await deleteChat(chatId)
      setChatToDelete(null)
      // Close sidebar on mobile if open
      if (!isDesktop && isSidebarOpen) {
        toggleSidebar()
      }
      toast({
        title: "Chat Deleted",
        description: "The chat has been deleted successfully.",
        variant: "success",
        duration: 2000,
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete chat. Please try again.",
        variant: "destructive",
      })
    }
  }

  // Filter chats based on search query
  const filteredChats = useMemo(() => {
    // First ensure chats are unique by ID
    const uniqueChatsMap = new Map();
    chats.forEach(chat => {
      uniqueChatsMap.set(chat.id, chat);
    });
    
    // Convert map back to array
    const uniqueChats = Array.from(uniqueChatsMap.values());
    
    // Filter by search query if needed
    if (searchQuery.trim() === "") {
      return uniqueChats;
    } else {
      return uniqueChats.filter(chat => 
        chat.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
  }, [chats, searchQuery]);

  // CONDITIONAL RENDERING FOR CLOSED SIDEBAR STATE
  if (!isSidebarOpen) {
    return (
      <div className="fixed top-0 left-0 h-16 flex items-center justify-between bg-background px-4 z-50">
        <div className="flex items-center">
          {/* Sidebar Toggle Button (to OPEN) */}
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 rounded-full mr-3"
                  onClick={toggleSidebar}
                  aria-label="Open sidebar"
                >
                  <span className="inline-flex items-center justify-center transform scale-[2.1]">
                    <SidebarIcon />
                  </span>
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Open sidebar</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          {/* New Chat Icon Button */}
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 rounded-full mr-3"
                  onClick={handleNewChat}
                  aria-label="New Chat"
                >
                  <span className="inline-flex items-center justify-center transform scale-[1.5]">
                    <NewChatIcon />
                  </span>
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>New chat</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          {/* Logo Icon */}
          <svg 
            version="1.0" 
            xmlns="http://www.w3.org/2000/svg" 
            viewBox="0 0 300.000000 300.000000" 
            preserveAspectRatio="xMidYMid meet"
            className="h-7 w-7 text-primary"
          >  
          <g transform="translate(0.000000,300.000000) scale(0.100000,-0.100000)" fill="currentColor" stroke="none"> 
            <path d="M995 2827 c-22 -8 -54 -21 -71 -30 -39 -20 -106 -93 -123 -133 -11 -28 -19 -33 -59 -39 -158 -22 -277 -151 -290 -311 -4 -59 -7 -66 -38 -84 -44 -28 -88 -80 -121 -143 -25 -47 -28 -62 -28 -157 0 -88 3 -112 22 -149 l22 -44 -31 -36 c-117 -133 -107 -351 20 -475 37 -35 39 -41 31 -69 -13 -47 -11 -127 6 -183 32 -107 115 -195 218 -230 46 -15 47 -17 47 -57 0 -54 38 -134 84 -180 38 -38 104 -77 130 -77 9 0 20 -8 25 -18 5 -10 34 -31 63 -48 46 -25 63 -29 133 -29 68 0 88 5 134 28 64 34 135 105 153 152 14 39 24 44 33 16 3 -10 28 -40 55 -65 47 -44 50 -50 50 -97 0 -82 58 -167 128 -187 15 -4 257 -7 537 -7 508 0 510 0 552 22 48 26 76 62 92 118 9 29 11 238 9 775 -3 835 2 785 -87 841 -44 29 -47 29 -192 29 l-146 0 -6 52 c-9 74 -50 151 -108 201 -42 36 -49 47 -49 78 0 51 -25 127 -60 182 -34 54 -101 101 -176 123 -47 13 -53 19 -68 58 -38 99 -138 174 -248 183 -112 11 -213 -43 -269 -143 l-32 -55 -17 38 c-22 49 -81 107 -136 134 -54 26 -137 33 -189 16z m721 -108 c40 -25 94 -101 94 -134 0 -34 28 -65 59 -65 50 0 120 -31 161 -72 50 -50 72 -119 64 -194 -7 -52 -6 -54 26 -71 80 -44 140 -127 140 -195 l0 -27 -343 -3 -344 -3 -36 -28 c-76 -58 -71 -17 -77 -742 l-5 -650 -30 60 -30 60 0 945 0 945 26 55 c29 61 78 116 124 137 41 19 126 10 171 -18z m-539 -15 c50 -40 89 -114 103 -194 8 -46 10 -330 8 -955 -3 -841 -4 -893 -22 -940 -39 -103 -110 -170 -203 -190 -46 -9 -113 12 -153 50 -19 18 -52 38 -73 45 -156 50 -203 257 -84 367 43 40 52 45 109 57 32 7 48 47 28 71 -31 38 -162 -4 -216 -68 -15 -18 -37 -53 -49 -79 l-21 -46 -41 18 c-102 46 -169 168 -149 274 6 33 9 35 32 26 61 -24 109 -4 102 41 -4 26 -16 33 -83 50 -63 16 -145 94 -163 155 -43 147 30 292 166 326 53 13 70 39 47 74 -18 27 -34 29 -88 9 l-39 -13 -20 45 c-16 35 -19 61 -16 112 5 78 28 131 82 185 l39 39 23 -45 c13 -25 44 -64 70 -86 42 -38 134 -82 170 -82 8 0 16 -6 18 -12 2 -7 9 -32 15 -56 15 -53 73 -119 126 -143 105 -48 285 5 273 82 -6 42 -33 47 -87 16 -101 -56 -199 -16 -232 94 -10 32 -9 46 5 83 10 25 15 54 11 65 -14 44 -77 34 -89 -14 -8 -32 -29 -32 -97 3 -191 97 -179 361 21 451 62 28 67 27 67 -21 0 -147 132 -288 269 -288 36 0 64 22 64 49 0 26 -18 37 -72 45 -157 23 -224 229 -117 359 48 58 92 78 166 74 52 -2 69 -8 100 -33z m164 -84 c9 0 24 9 34 20 26 29 27 21 5 -37 -10 -28 -22 -74 -26 -102 -9 -67 -20 -72 -28 -13 -6 41 -23 98 -51 167 -7 16 -2 15 22 -7 16 -16 36 -28 44 -28z m-506 -11 c-8 -23 -15 -50 -15 -60 0 -25 -8 -24 -37 2 l-22 22 42 38 c23 21 43 38 44 39 1 0 -4 -19 -12 -41z m1054 -47 c-15 -6 -39 19 -39 40 0 16 3 15 24 -9 14 -15 20 -30 15 -31z m-1379 -343 c6 -22 14 -47 17 -56 5 -12 -2 -10 -24 7 -35 25 -55 22 -95 -15 -51 -47 -29 -13 30 45 31 32 58 58 59 59 1 0 7 -17 13 -40z m1670 -13 c0 -4 -9 -2 -20 4 -11 6 -20 20 -20 32 0 20 1 19 20 -5 11 -14 20 -28 20 -31z m-1375 -223 l-6 -35 -25 23 -24 23 27 22 c32 25 38 18 28 -33z m1545 -67 c0 -3 -20 -6 -45 -6 -25 0 -45 2 -45 5 0 3 10 19 21 35 l22 28 23 -28 c13 -15 24 -31 24 -34z m283 -58 c48 -25 46 0 47 -789 l0 -746 -26 -27 -27 -26 -508 0 -508 0 -28 24 -28 24 0 752 0 752 28 24 28 24 500 0 c361 0 506 -3 522 -12z m-2257 -99 l35 -21 -23 -16 c-13 -8 -40 -31 -62 -51 l-39 -36 28 48 c21 37 26 55 21 85 -3 20 -3 32 0 25 3 -7 21 -22 40 -34z m24 -544 c17 -9 30 -18 30 -21 0 -3 -13 -19 -30 -34 l-30 -28 0 33 c0 23 -11 49 -37 82 l-37 48 37 -32 c21 -18 51 -40 67 -48z m252 -426 l-15 -60 -26 25 -26 26 24 17 c13 9 31 24 40 35 8 10 16 18 16 18 1 0 -5 -27 -13 -61z m702 -97 c8 -60 48 -142 78 -161 20 -12 24 -11 50 18 l28 31 0 -82 0 -82 -79 83 c-70 73 -82 81 -100 72 -11 -6 -23 -16 -26 -21 -3 -6 -10 -10 -15 -10 -4 0 0 26 10 58 10 32 21 79 25 105 9 58 20 53 29 -11z"/> 
            <path d="M1622 2458 c-16 -16 -15 -53 2 -68 8 -6 20 -27 26 -46 10 -29 9 -41 -9 -77 -11 -23 -37 -52 -56 -65 -37 -23 -46 -57 -23 -80 18 -18 46 -14 86 13 20 14 46 25 58 25 30 0 71 -35 94 -81 15 -28 27 -39 43 -39 94 0 37 148 -75 194 -35 15 -37 18 -27 44 15 40 2 105 -32 151 -30 42 -63 53 -87 29z m89 -220 c25 -31 24 -35 -13 -41 -18 -3 -41 -9 -51 -13 -15 -5 -13 1 10 34 15 23 30 41 31 42 2 0 12 -10 23 -22z"/> 
            <path d="M608 1534 c-56 -17 -85 -52 -69 -82 16 -29 38 -34 74 -15 77 39 180 3 223 -78 12 -23 11 -31 -6 -65 -22 -43 -26 -114 -8 -132 28 -28 78 2 78 47 0 55 71 132 139 151 79 21 64 113 -16 94 -16 -4 -45 -15 -65 -26 l-38 -18 -37 41 c-72 79 -183 113 -275 83z m333 -159 c19 6 16 0 -17 -38 l-39 -45 -5 41 c-3 23 -15 55 -25 72 l-20 30 42 -34 c31 -25 47 -31 64 -26z"/> 
            <path d="M1044 941 c-79 -36 -142 -122 -152 -207 -4 -35 -1 -44 19 -57 33 -24 59 -3 74 57 14 56 53 100 115 129 50 24 61 49 34 78 -21 24 -38 24 -90 0z"/> 
            <path d="M1662 1758 c-8 -8 -12 -60 -12 -168 0 -108 4 -160 12 -168 9 -9 125 -12 460 -12 432 0 448 1 458 19 5 11 10 84 10 165 0 118 -3 147 -16 160 -14 14 -69 16 -458 16 -330 0 -445 -3 -454 -12z m78 -36 c0 -5 -11 -19 -25 -32 l-25 -23 0 25 c0 15 6 29 13 31 19 8 37 8 37 -1z m798 -27 l4 -30 -26 24 c-27 25 -26 44 2 39 10 -2 18 -15 20 -33z m-38 -105 l0 -90 -380 0 -380 0 0 90 0 90 380 0 380 0 0 -90z m-765 -138 c-28 -6 -45 7 -45 35 l0 27 31 -30 c24 -23 27 -30 14 -32z m805 23 c0 -20 -5 -25 -27 -25 l-26 0 23 25 c13 14 25 25 27 25 2 0 3 -11 3 -25z"/> 
            <path d="M1662 1298 c-8 -8 -12 -48 -12 -114 0 -133 1 -134 124 -134 123 0 126 3 126 136 0 65 -4 104 -12 112 -8 8 -48 12 -113 12 -65 0 -105 -4 -113 -12z m78 -33 c0 -12 -33 -55 -41 -55 -14 0 -11 48 4 53 17 7 37 8 37 2z m110 -10 c6 -8 10 -22 8 -32 -3 -15 -6 -15 -26 7 -12 13 -22 27 -22 32 0 13 27 9 40 -7z m-40 -75 c0 -39 -1 -40 -35 -40 -34 0 -35 1 -35 40 0 39 1 40 35 40 34 0 35 -1 35 -40z m-80 -78 c-22 -8 -40 8 -40 35 l1 28 24 -30 c14 -16 20 -32 15 -33z m122 6 c-5 -5 -17 -8 -27 -6 -14 3 -13 6 7 28 21 22 23 23 26 6 2 -10 -1 -23 -6 -28z"/> 
            <path d="M2006 1294 c-12 -12 -16 -38 -16 -113 0 -127 4 -131 124 -131 127 0 126 -1 126 128 0 71 -4 112 -12 120 -19 19 -202 16 -222 -4z m77 -31 c8 -7 -31 -53 -45 -53 -4 0 -8 8 -8 18 0 31 35 54 53 35z m101 1 c9 -3 16 -18 16 -32 l0 -25 -25 23 c-36 34 -32 50 9 34z m-30 -84 c0 -33 -2 -35 -37 -38 l-37 -3 0 41 0 41 37 -3 c35 -3 37 -5 37 -38z m-92 -47 c24 -22 23 -35 -4 -31 -15 2 -24 11 -26 26 -4 26 5 28 30 5z m134 -18 c-3 -8 -15 -15 -27 -15 l-22 0 24 26 c23 24 37 19 25 -11z"/> 
            <path d="M2348 1293 c-11 -14 -14 -42 -13 -117 3 -124 5 -126 130 -126 121 0 125 4 125 133 0 126 -1 127 -129 127 -81 0 -100 -3 -113 -17z m76 -32 c3 -4 -6 -19 -19 -31 l-25 -23 0 25 c0 30 31 51 44 29z m100 3 c9 -3 16 -18 16 -32 l0 -25 -25 23 c-30 28 -25 47 9 34z m-24 -85 l0 -40 -37 3 c-36 3 -38 5 -41 41 l-3 37 40 0 41 0 0 -41z m-80 -71 c0 -4 -9 -8 -20 -8 -15 0 -20 7 -20 27 0 25 0 26 20 8 11 -10 20 -22 20 -27z m120 17 c0 -18 -5 -25 -20 -25 -24 0 -25 8 -3 32 21 23 23 23 23 -7z"/> 
            <path d="M1662 948 c-8 -8 -12 -48 -12 -113 0 -65 4 -105 12 -113 16 -16 210 -16 226 0 16 16 16 210 0 226 -16 16 -210 16 -226 0z m78 -36 c0 -5 -11 -19 -25 -32 l-25 -23 0 25 c0 13 3 28 7 31 9 10 43 9 43 -1z m118 -27 l4 -30 -26 24 c-32 30 -33 43 -3 39 16 -2 23 -11 25 -33z m-48 -50 c0 -33 -2 -35 -35 -35 -33 0 -35 2 -35 35 0 33 2 35 35 35 33 0 35 -2 35 -35z m-70 -77 c0 -5 -10 -8 -22 -6 -17 2 -24 11 -26 33 l-4 30 26 -24 c14 -14 26 -29 26 -33z m116 6 c-5 -14 -46 -20 -46 -7 0 4 10 18 23 31 18 20 23 21 25 7 2 -9 1 -23 -2 -31z"/> 
            <path d="M2002 948 c-18 -18 -17 -212 2 -227 9 -8 51 -11 122 -9 l109 3 0 120 0 120 -110 3 c-77 2 -114 -1 -123 -10z m66 -57 c-25 -33 -38 -38 -38 -17 0 30 13 46 37 46 l25 0 -24 -29z m130 2 c4 -27 -5 -29 -30 -6 -24 22 -23 35 5 31 14 -2 23 -11 25 -25z m-42 -58 c0 -34 -1 -35 -38 -35 -37 0 -38 1 -38 35 0 34 1 35 38 35 36 0 37 -1 38 -35z m-76 -77 c0 -5 -10 -8 -22 -6 -17 2 -24 11 -26 33 l-4 30 26 -24 c14 -14 26 -29 26 -33z m118 20 c-2 -15 -11 -24 -25 -26 -27 -4 -29 5 -6 30 22 24 35 23 31 -4z"/> 
            <path d="M2345 950 c-4 -6 -7 -135 -7 -287 0 -254 2 -278 18 -290 27 -19 183 -17 212 3 22 15 22 18 22 280 0 164 -4 273 -10 285 -10 17 -22 19 -120 19 -64 0 -111 -4 -115 -10z m85 -39 c0 -6 -10 -17 -22 -26 -24 -16 -35 -7 -24 20 6 16 46 21 46 6z m106 -6 c12 -30 -2 -35 -25 -11 l-24 26 22 0 c12 0 24 -7 27 -15z m-36 -243 l0 -209 -36 2 -36 2 -1 207 -2 206 38 0 37 0 0 -208z m-91 -224 l24 -28 -26 0 c-24 0 -27 4 -27 32 0 17 1 29 3 27 1 -2 13 -16 26 -31z m134 -8 c-3 -11 -14 -20 -24 -20 -23 0 -24 8 -3 31 20 22 34 16 27 -11z"/> 
            <path d="M1668 609 c-15 -8 -18 -25 -18 -114 0 -134 1 -135 125 -135 123 0 125 2 125 130 0 128 -2 130 -123 130 -51 0 -100 -5 -109 -11z m56 -64 c-19 -29 -34 -32 -34 -7 0 24 8 32 32 32 17 0 18 -1 2 -25z m132 10 c12 -30 -2 -35 -25 -11 l-24 26 22 0 c12 0 24 -7 27 -15z m-46 -63 c0 -37 -1 -38 -35 -38 -34 0 -35 1 -35 38 0 37 1 38 35 38 34 0 35 -1 35 -38z m-79 -80 c-23 -8 -41 8 -41 35 l1 28 26 -30 c16 -18 21 -31 14 -33z m125 12 c-3 -8 -15 -14 -26 -14 -21 0 -21 0 2 32 19 27 23 29 26 15 2 -10 1 -25 -2 -33z"/> 
            <path d="M2006 604 c-12 -12 -16 -38 -16 -114 0 -124 6 -130 128 -130 123 0 122 -1 122 130 0 132 2 130 -129 130 -68 0 -93 -4 -105 -16z m59 -64 c-10 -11 -22 -20 -27 -20 -15 0 -8 39 10 49 26 15 39 -5 17 -29z m131 15 c12 -30 -2 -35 -25 -11 l-24 26 22 0 c12 0 24 -7 27 -15z m-42 -65 c0 -33 -2 -34 -37 -36 -37 -1 -37 0 -37 38 0 39 0 39 37 36 35 -3 37 -5 37 -38z m-92 -47 c24 -22 23 -35 -4 -31 -15 2 -24 11 -26 26 -4 26 5 28 30 5z m138 -8 c0 -20 -5 -25 -27 -25 l-26 0 23 25 c13 14 25 25 27 25 2 0 3 -11 3 -25z"/> 
          </g>
        </svg>

                  {/* App Title */}
        <button
          onClick={handleTitleClick}
          className="text-xl font-bold ml-3 text-left hover:text-primary focus:outline-none"
          aria-label="Return to home"
        >
          AI Math Chatbot
        </button>
        </div>
        <div></div>
      </div>
    );
  }

  // EXISTING RETURN FOR OPEN SIDEBAR STATE
  return (
    <>
      <div
        className={cn(
          "fixed inset-0 z-40 bg-background/80 backdrop-blur-sm md:hidden transition-opacity duration-300 ease-in-out",
          isSidebarOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none",
        )}
        onClick={toggleSidebar}
      />

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-72 bg-muted/50 backdrop-blur-sm transition-transform duration-300 ease-in-out md:relative md:z-0",
          "dark:bg-black dark:backdrop-blur-none",
          !isSidebarOpen && "-translate-x-full md:translate-x-0",
        )}
      >
        <div className="flex h-16 items-center justify-between px-4">
          <div className="flex items-center">
            {!isDesktop && (
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 rounded-full mr-2 md:hidden"
                      onClick={toggleSidebar}
                      aria-label="Close sidebar"
                    >
                      <span className="inline-flex items-center justify-center transform scale-[2.1]">
                        <X className="h-4 w-4" />
                      </span>
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Close sidebar</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            )}
            {isDesktop && (
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 rounded-full mr-2"
                      onClick={toggleSidebar}
                      aria-label={isSidebarOpen ? "Close sidebar" : "Open sidebar"}
                    >
                      <span className="inline-flex items-center justify-center transform scale-[2.1]">
                        <SidebarIcon />
                      </span>
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{isSidebarOpen ? "Close sidebar" : "Open sidebar"}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            )}
          </div>
          <div className="flex items-center gap-2">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 rounded-full"
                    onClick={() => setIsSearchActive(!isSearchActive)}
                  >
                    <span className="inline-flex items-center justify-center transform scale-[1.5]">
                      <Search strokeWidth={2} className="h-4 w-4" />
                    </span>
                    <span className="sr-only">Search Chats</span>
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Search chats</p>
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
                    onClick={handleNewChat}
                  >
                    <span className="inline-flex items-center justify-center transform scale-[1.5]">
                      <NewChatIcon />
                    </span>   
                    <span className="sr-only">New Chat</span>
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>New chat</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>

        <div className="flex flex-col gap-1 p-3">
          <div className="flex items-center gap-2 px-2 py-1 text-sm font-medium text-muted-foreground">
            <History className="h-4 w-4" />
            <span>Chat History</span>
          </div>

          {/* Search Input - Only shown when search is active */}
          {isSearchActive && (
            <div className="mb-2 px-2 py-1">
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search chats..."
                className="h-8 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
              />
            </div>
          )}

          <div className={cn(
            "mt-2 space-y-1",
            filteredChats.length > 11 && "sidebar-chat-scrollbar sidebar-chat-scrollable"
          )}>
            {filteredChats.length === 0 ? (
              <div className="flex flex-col items-center justify-center rounded-md border border-dashed p-4 text-center">
                <BookOpen className="mb-2 h-8 w-8 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">{searchQuery ? "No matching chats" : "No chat history yet"}</p>
                <p className="text-xs text-muted-foreground">{searchQuery ? "Try a different search term" : "Start a new conversation to see it here"}</p>
              </div>
            ) : (
              filteredChats.map((chat) => (
                <div key={chat.id} className="relative">
                  {isRenaming === chat.id ? (
                    <div className="flex items-center gap-1 rounded-md border p-2">
                      <Input
                        value={newName}
                        onChange={(e) => setNewName(e.target.value)}
                        placeholder="Chat name"
                        className="h-8"
                        autoFocus
                        onKeyDown={(e) => {
                          if (e.key === "Enter") {
                            handleRenameSubmit(e, chat.id, newName)
                          } else if (e.key === "Escape") {
                            setIsRenaming(null)
                            setNewName("")
                          }
                        }}
                      />
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                        onClick={(e) => handleRenameSubmit(e, chat.id, newName)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <div
                      className={cn(
                        "group flex items-center justify-between rounded-md px-2 py-2 transition-colors",
                        activeChat === chat.id ? "bg-primary/15 text-primary" : "hover:bg-primary/10 dark:hover:bg-muted/80",
                      )}
                    >
                      <button
                        className="w-full overflow-hidden text-left"
                        onClick={() => {
                          if (chat.id) {
                            handleSelectChat(chat.id)
                          }
                        }}
                      >
                        <span className="line-clamp-1">{chat.name}</span>
                      </button>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 opacity-0 transition-opacity group-hover:opacity-100"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              width="24"
                              height="24"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              className="h-4 w-4"
                            >
                              <circle cx="12" cy="12" r="1" />
                              <circle cx="12" cy="5" r="1" />
                              <circle cx="12" cy="19" r="1" />
                            </svg>
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            onClick={(e) => {
                              e.preventDefault()
                              setIsRenaming(chat.id)
                              setNewName(chat.name)
                            }}
                          >
                            <Edit2 className="mr-2 h-4 w-4" />
                            Rename
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            className="text-destructive focus:text-destructive"
                            onClick={() => setChatToDelete(chat.id)}
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </aside>

      {/* Delete chat confirmation dialog */}
      <AlertDialog open={!!chatToDelete} onOpenChange={(open) => !open && setChatToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete chat?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this chat? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (chatToDelete) {
                  handleDeleteChat(chatToDelete)
                }
              }}
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
