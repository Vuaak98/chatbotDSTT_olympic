import { type ReactNode } from "react"

export interface Message {
  role: "user" | "assistant" | "model" | "system"
  content: string
  id?: string
  isLoading?: boolean
  isError?: boolean
  files?: FileInfo[]
  isAnimating?: boolean
}

export interface Chat {
  id: string
  name: string
  messages: Message[]
}

export interface FileInfo {
  file_id: string
  filename: string
  content_type: string
  size: number
  path?: string
  processing_method?: "inline" | "files_api"
}

export interface ApiConfig {
  baseUrl: string
  apiKey?: string
}
