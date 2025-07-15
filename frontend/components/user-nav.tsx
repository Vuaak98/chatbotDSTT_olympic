"use client";

import { useAuth } from "@/lib/auth-context";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export function UserNav() {
  const { user, isLoading, logout } = useAuth();

  // Nếu đang tải thông tin, không hiển thị gì cả
  if (isLoading) {
    return null; // Hoặc một skeleton loader
  }

  // Nếu người dùng đã đăng nhập
  if (user) {
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="relative h-8 w-8 rounded-full">
            <Avatar className="h-8 w-8">
              {/* Bạn có thể thêm ảnh đại diện nếu có */}
              {/* <AvatarImage src="/avatars/01.png" alt="@shadcn" /> */}
              <AvatarFallback>
                {user.email.substring(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-56" align="end" forceMount>
          <DropdownMenuLabel className="font-normal">
            <div className="flex flex-col space-y-1">
              <p className="text-sm font-medium leading-none">Đã đăng nhập với</p>
              <p className="text-xs leading-none text-muted-foreground">
                {user.email}
              </p>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => logout()}>
            Đăng xuất
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    );
  }

  // Nếu người dùng chưa đăng nhập
  return (
    <div className="flex items-center space-x-2">
      <Button asChild variant="ghost">
        <Link href="/login">Đăng nhập</Link>
      </Button>
      <Button asChild>
        <Link href="/register">Đăng ký</Link>
      </Button>
    </div>
  );
} 