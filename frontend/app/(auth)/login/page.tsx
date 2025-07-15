"use client";
import { login as apiLogin } from "@/lib/auth-api";
import { useAuth } from "@/lib/auth-context";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { formSchema } from "@/lib/validationSchemas";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useToast } from "@/hooks/use-toast";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    if (typeof window !== "undefined" && sessionStorage.getItem("showRegisterSuccess")) {
      toast({
        title: "Đăng ký thành công!",
        description: "Vui lòng đăng nhập.",
        variant: "success",
      });
      sessionStorage.removeItem("showRegisterSuccess");
    }
  }, [toast]);

  const { handleSubmit, control, register } = useForm<z.infer<typeof formSchema>>({
    defaultValues: {
      email: "",
      password: "",
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setError(null);
    try {
      // Sử dụng hàm apiLogin
      const tokenData = await apiLogin({
        email: values.email,
        password: values.password,
      });
      // Gọi hàm login từ context để lưu token
      await login(tokenData.access_token);
      if (typeof window !== "undefined") {
        sessionStorage.setItem("showWelcomeToast", "1");
      }
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Email hoặc mật khẩu không chính xác.");
      console.error(err);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle>Đăng nhập</CardTitle>
          <CardDescription>
            Đăng nhập để trải nghiệm các tính năng của ứng dụng.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                {...register("email", { required: "Email là bắt buộc" })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Mật khẩu</Label>
              <Input
                id="password"
                type="password"
                {...register("password", { required: "Mật khẩu là bắt buộc" })}
              />
            </div>
            {error && (
              <p className="text-red-500 text-sm">{error}</p>
            )}
            <Button type="submit" className="w-full">
              Đăng nhập
            </Button>
          </form>
        </CardContent>
        <CardFooter className="text-center">
          <p>
            Bạn chưa có tài khoản?{" "}
            <Link href="/register" className="text-blue-600 hover:underline">
              Đăng ký ngay
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
} 