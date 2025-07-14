import { ApiConfig } from './types'

// Define API configuration with defaults that can be overridden
export const apiConfig: ApiConfig = {
  // Default to localhost:8000 in development, but use environment variables if available
  baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
}

// Helper to get the full URL for an API endpoint
export const getApiUrl = (path: string): string => {
  // Ensure path starts with / and remove duplicate slashes
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${apiConfig.baseUrl}${normalizedPath}`
} 