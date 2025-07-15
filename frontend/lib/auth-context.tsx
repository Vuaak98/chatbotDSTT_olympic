"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { getCurrentUser, login as apiLogin } from "@/lib/auth-api";
import { useStore } from "@/lib/store";

interface User {
  id: number;
  email: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  resetAppState: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const clearAllChats = useStore((state) => state.clearAllChats);

  useEffect(() => {
    const storedToken = localStorage.getItem("authToken");
    if (storedToken) {
      setToken(storedToken);
      fetchUserInfo(storedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  // Hàm resetAppState: phát sự kiện toàn cục
  const resetAppState = () => {
    if (typeof window !== "undefined") {
      window.dispatchEvent(new Event("app-reset"));
    }
  };

  const fetchUserInfo = async (token: string) => {
    try {
      // Sử dụng hàm getCurrentUser
      const userInfo = await getCurrentUser(token);
      setUser(userInfo);
    } catch (error) {
      console.error("Failed to fetch user info, logging out.", error);
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (token: string) => {
    localStorage.setItem("authToken", token);
    setToken(token);
    clearAllChats(); // Clear all chat state before loading user info
    await fetchUserInfo(token);
    resetAppState(); // Thông báo toàn app làm mới dữ liệu
    router.push("/"); // Chuyển hướng về trang chủ
  };

  const logout = () => {
    localStorage.removeItem("authToken");
    setUser(null);
    setToken(null);
    resetAppState(); // Thông báo toàn app làm mới dữ liệu
    router.push("/login"); // Chuyển hướng về trang đăng nhập
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading, resetAppState }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
} 