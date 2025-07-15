# TODO: Xây dựng hệ thống Authentication cho FastAPI

## 1. Cài đặt thư viện cần thiết

- [x] Thêm vào cuối file `backend/requirements.txt`:
  ```
  passlib[bcrypt]==1.7.4
  python-jose[cryptography]==3.3.0
  python-dotenv==0.21.0
  ```
- [x] Cài đặt:
  ```bash
  cd backend
  pip install -r requirements.txt
  ```

---

## 2. Cấu hình biến môi trường

- [x] Tạo file `.env` trong thư mục `backend`:
  ```
  SECRET_KEY="a-super-secret-key-that-you-must-change"
  ALGORITHM="HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES=60
  ```
- [x] Trong `backend/app/config.py`, thêm:
  ```python
  from dotenv import load_dotenv
  import os

  load_dotenv()

  SECRET_KEY = os.getenv("SECRET_KEY")
  ALGORITHM = os.getenv("ALGORITHM")
  ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
  ```

---

## 3. Đảm bảo model User

- [x] Trong `backend/app/models.py`:
  ```python
  from sqlalchemy import Column, Integer, String, DateTime, Boolean
  from datetime import datetime
  from .database import Base

  class User(Base):
      __tablename__ = "users"
      id = Column(Integer, primary_key=True, index=True)
      email = Column(String, unique=True, index=True, nullable=False)
      hashed_password = Column(String, nullable=False)
      created_at = Column(DateTime, default=datetime.utcnow)
      is_active = Column(Boolean, default=True)
  ```
- [x] Chạy migration:
  ```bash
  set PYTHONUTF8=1
  alembic revision --autogenerate -m "add user model"
  alembic upgrade head
  ```

---

## 4. Tạo schemas cho Auth

- [x] Trong `backend/app/schemas.py`:
  ```python
  from pydantic import BaseModel, EmailStr
  from datetime import datetime
  from typing import Optional

  class UserRegister(BaseModel):
      email: EmailStr
      password: str

  class UserLogin(BaseModel):
      email: EmailStr
      password: str

  class Token(BaseModel):
      access_token: str
      token_type: str

  class TokenData(BaseModel):
      email: Optional[str] = None

  class UserResponse(BaseModel):
      id: int
      email: EmailStr
      is_active: bool
      created_at: datetime

      class Config:
          from_attributes = True
  ```

---

## 5. CRUD cho User

- [x] Trong `backend/app/crud/auth_crud.py`:
  ```python
  from sqlalchemy.orm import Session
  from app.models import User
  from app.schemas import UserRegister

  def get_user_by_email(db: Session, email: str):
      return db.query(User).filter(User.email == email).first()

  def create_user(db: Session, user: UserRegister, hashed_password: str):
      db_user = User(email=user.email, hashed_password=hashed_password)
      db.add(db_user)
      db.commit()
      db.refresh(db_user)
      return db_user
  ```

---

## 6. Auth Service

- [x] Trong `backend/app/auth_service.py`:
  ```python
  from passlib.context import CryptContext
  from jose import jwt, JWTError
  from datetime import datetime, timedelta, timezone
  from sqlalchemy.orm import Session
  from app.crud import auth_crud
  from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
  from fastapi import Depends, HTTPException, status
  from fastapi.security import OAuth2PasswordBearer
  from app.database import get_db
  from app.schemas import TokenData

  pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
  oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

  def verify_password(plain_password, hashed_password):
      return pwd_context.verify(plain_password, hashed_password)

  def get_password_hash(password):
      return pwd_context.hash(password)

  def create_access_token(data: dict):
      to_encode = data.copy()
      expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
      to_encode.update({"exp": expire})
      return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

  def authenticate_user(db: Session, email: str, password: str):
      user = auth_crud.get_user_by_email(db, email)
      if not user or not verify_password(password, user.hashed_password):
          return None
      return user

  def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
      credentials_exception = HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Could not validate credentials",
          headers={"WWW-Authenticate": "Bearer"},
      )
      try:
          payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
          email: str = payload.get("sub")
          if email is None:
              raise credentials_exception
          token_data = TokenData(email=email)
      except JWTError:
          raise credentials_exception
      user = auth_crud.get_user_by_email(db, email=token_data.email)
      if user is None:
          raise credentials_exception
      return user
  ```

---

## 7. Auth Router

- [x] Trong `backend/app/routers/auth_router.py`:
  ```python
  from fastapi import APIRouter, Depends, HTTPException, status
  from sqlalchemy.orm import Session
  from app.schemas import UserRegister, UserLogin, Token, UserResponse
  from app.auth_service import get_password_hash, create_access_token, authenticate_user, get_current_user
  from app.crud import auth_crud
  from app.database import get_db
  from app.models import User

  router = APIRouter(
      prefix="/auth",
      tags=["Authentication"]
  )

  @router.post("/register", response_model=UserResponse)
  def register_user(user: UserRegister, db: Session = Depends(get_db)):
      db_user = auth_crud.get_user_by_email(db, email=user.email)
      if db_user:
          raise HTTPException(status_code=400, detail="Email đã được đăng ký")
      hashed_password = get_password_hash(user.password)
      new_user = auth_crud.create_user(db, user=user, hashed_password=hashed_password)
      return new_user

  @router.post("/login", response_model=Token)
  def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
      user = authenticate_user(db, email=form_data.email, password=form_data.password)
      if not user:
          raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="Email hoặc mật khẩu không chính xác",
              headers={"WWW-Authenticate": "Bearer"},
          )
      access_token = create_access_token(data={"sub": user.email})
      return {"access_token": access_token, "token_type": "bearer"}

  @router.get("/me", response_model=UserResponse)
  def read_users_me(current_user: User = Depends(get_current_user)):
      return current_user
  ```

---

## 8. Đăng ký router vào main.py

- [x] Trong `backend/app/main.py`:
  ```python
  from app.routers import auth_router
  app.include_router(auth_router.router)
  ```

---

## 9. Test lại API

- [x] Chạy lại server:
  ```bash
  uvicorn app.main:app --reload
  ```
- [x] Truy cập http://localhost:8000/docs để test các endpoint `/auth/register`, `/auth/login`, `/auth/me`.

---

**Nếu gặp lỗi ở bước nào, hãy gửi log lỗi hoặc yêu cầu chi tiết, mình sẽ hỗ trợ ngay!**

---

## 2. Trang Đăng ký (register/page.tsx) & Đăng nhập (login/page.tsx) - Thiết kế giao diện hiện đại

### Phân tích dữ liệu giao diện
Dựa trên các file login_email.html, register_email.html, login_email.css, và register.css, các yếu tố giao diện chính bao gồm:
- Một form chứa trong một box (card) có bo góc và đổ bóng.
- Tiêu đề (Đăng nhập / Tạo tài khoản).
- Các ô nhập liệu cho Email và Mật khẩu, có nhãn (label) đi kèm.
- Một nút bấm để thực hiện hành động (Đăng nhập / Đăng ký).
- Một đường dẫn để chuyển đổi giữa hai form.

Chúng ta sẽ tái cấu trúc các yếu tố này bằng bộ thư viện component Shadcn UI đã có sẵn trong dự án để có một giao diện hiện đại và nhất quán.

### 1. Trang Đăng nhập (login/page.tsx)
Component này tái tạo lại giao diện từ login_email.html và login_email.css.

```tsx
"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api-service";

// Định nghĩa cấu trúc và validation cho form
const formSchema = z.object({
  email: z.string().email({ message: "Email không hợp lệ." }),
  password: z.string().min(1, { message: "Mật khẩu không được để trống." }),
});

export default function LoginPage() {
  const [error, setError] = useState<string | null>(null);
  const { login } = useAuth(); // Lấy hàm login từ context

  // Thiết lập hook form
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  // Hàm xử lý khi submit form
  async function onSubmit(values: z.infer<typeof formSchema>) {
    setError(null);
    try {
      const response = await api.post("/auth/login", {
        email: values.email,
        password: values.password,
      });
      // Gọi hàm login từ context để lưu token và thông tin user
      await login(response.data.access_token);
    } catch (err) {
      setError("Email hoặc mật khẩu không chính xác.");
      console.error(err);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 dark:bg-gray-950">
      <Card className="mx-auto w-full max-w-sm">
        <CardHeader>
          <CardTitle className="text-2xl">Đăng nhập</CardTitle>
          <CardDescription>
            Nhập email và mật khẩu để truy cập vào hệ thống
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && <p className="mb-4 text-center text-sm text-red-500">{error}</p>}
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="you@example.com"
                        {...field}
                        type="email"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Mật khẩu</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="••••••••"
                        {...field}
                        type="password"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full">
                Đăng nhập
              </Button>
            </form>
          </Form>
          <div className="mt-4 text-center text-sm">
            Bạn chưa có tài khoản?{" "}
            <Link href="/register" className="underline">
              Hãy đăng ký
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

### 2. Trang Đăng ký (register/page.tsx)
Component này tái tạo lại giao diện từ register_email.html và register.css.

```tsx
"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api-service";

// Định nghĩa cấu trúc và validation cho form
const formSchema = z.object({
  email: z.string().email({ message: "Email không hợp lệ." }),
  password: z
    .string()
    .min(8, { message: "Mật khẩu phải có ít nhất 8 ký tự." }),
});

export default function RegisterPage() {
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Thiết lập hook form
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  // Hàm xử lý khi submit form
  async function onSubmit(values: z.infer<typeof formSchema>) {
    setError(null);
    try {
      await api.post("/auth/register", {
        email: values.email,
        password: values.password,
      });
      // Đăng ký thành công, chuyển hướng đến trang đăng nhập
      router.push("/login");
    } catch (err: any) {
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Đã có lỗi xảy ra. Vui lòng thử lại.");
      }
      console.error(err);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 dark:bg-gray-950">
      <Card className="mx-auto w-full max-w-sm">
        <CardHeader>
          <CardTitle className="text-2xl">Tạo một tài khoản</CardTitle>
          <CardDescription>
            Nhập email và mật khẩu của bạn để bắt đầu
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && <p className="mb-4 text-center text-sm text-red-500">{error}</p>}
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="you@example.com"
                        {...field}
                        type="email"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Mật khẩu</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="••••••••"
                        {...field}
                        type="password"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full">
                Đăng ký
              </Button>
            </form>
          </Form>
          <div className="mt-4 text-center text-sm">
            Bạn đã có tài khoản?{" "}
            <Link href="/login" className="underline">
              Hãy đăng nhập
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

#### Hướng dẫn tích hợp vào dự án

**Bước 1: Tạo cấu trúc thư mục**
Trong thư mục `frontend/app`, tạo một thư mục mới tên là `(auth)`. Dấu ngoặc đơn giúp Next.js nhóm các trang lại mà không thêm `(auth)` vào URL.

Bên trong `(auth)`, tạo hai thư mục con: `login` và `register`.

Cấu trúc cuối cùng sẽ như sau:

```
frontend/
└── app/
    ├── (auth)/
    │   ├── login/
    │   │   └── page.tsx  <-- File đăng nhập
    │   └── register/
    │       └── page.tsx  <-- File đăng ký
    └── ... (các thư mục và file khác của bạn)
```

**Bước 2: Dán code vào các file đã tạo**
- Mở thư mục `frontend/app/(auth)/login/`.
- Tạo file `page.tsx` và dán toàn bộ nội dung của code Trang Đăng nhập ở trên vào.
- Mở thư mục `frontend/app/(auth)/register/`.
- Tạo file `page.tsx` và dán toàn bộ nội dung của code Trang Đăng ký ở trên vào.

**Bước 3: Chạy và kiểm tra**
- Mở terminal, di chuyển vào thư mục `frontend`.
- Chạy lệnh `npm run dev` (hoặc `yarn dev`).
- Mở trình duyệt và truy cập vào các đường dẫn sau để xem kết quả:
  - Trang đăng nhập: http://localhost:3000/login
  - Trang đăng ký: http://localhost:3000/register

Bạn sẽ thấy các trang giao diện đăng nhập và đăng ký đã được xây dựng, sẵn sàng để kết nối với các logic và API mà chúng ta đã định nghĩa trong tài liệu hướng dẫn frontend-auth-integration-guide.

---

## Tóm tắt các bước đã hoàn thành (Authentication Frontend)

- [x] Tạo AuthContext để quản lý trạng thái đăng nhập (`frontend/lib/auth-context.tsx`)
- [x] Tạo hoặc cập nhật api-service.ts để quản lý gọi API và tự động thêm token (`frontend/lib/api-service.ts`)
- [x] Tích hợp AuthProvider vào layout.tsx để cung cấp trạng thái đăng nhập toàn app
- [x] Kết nối form Đăng nhập với API, lưu token và gọi login từ context (`frontend/app/(auth)/login/page.tsx`)
- [x] Kết nối form Đăng ký với API, chuyển hướng sang login khi thành công (`frontend/app/(auth)/register/page.tsx`)
- [x] Tạo ProtectedRoute component để bảo vệ các trang cần đăng nhập (`frontend/components/auth/protected-route.tsx`)
- [x] Bọc các trang chat hoặc trang cần bảo vệ bằng ProtectedRoute

**Kết quả:**
- Đăng ký/đăng nhập hoạt động ổn định, mỗi user có lịch sử chat riêng biệt.
- Giao diện luôn phản ánh đúng trạng thái đăng nhập/đăng xuất.
- Các API call luôn gửi token, bảo mật và đồng bộ dữ liệu.
- Sidebar và các component phụ thuộc luôn làm mới dữ liệu khi user thay đổi.

Bạn đã hoàn thành toàn bộ luồng xác thực frontend! 🚀

---

## Lỗi cần fix tiếp theo

- [ ] Fix lỗi chatbot thỉnh thoảng không trả lời hết câu, bị ngắt giữa chừng (kiểm tra lại logic xử lý stream và render markdown ở frontend)

---

## Hướng phát triển tiếp theo (gợi ý cho project sinh viên)

- Thêm chức năng đổi mật khẩu, quên mật khẩu (reset password qua email hoặc OTP đơn giản).
- Thêm xác thực email khi đăng ký (gửi mã xác nhận qua email, có thể dùng dịch vụ miễn phí như Gmail SMTP).
- Cho phép cập nhật thông tin cá nhân (avatar, tên hiển thị, v.v.).
- Thêm chức năng xóa tài khoản (self-delete account).
- Thêm phân quyền đơn giản: user thường, admin (admin có thể xem danh sách user, xóa user, v.v.).
- Thêm xác thực 2 lớp (2FA) bằng email hoặc mã OTP (nếu muốn nâng cao).
- Giao diện: Thêm loading, thông báo lỗi/thành công rõ ràng, UX thân thiện.
- Viết unit test cho các API đăng ký/đăng nhập.
- Đóng gói Docker, deploy lên dịch vụ miễn phí (Railway, Render, Vercel, v.v.).
- Viết tài liệu hướng dẫn sử dụng và cài đặt cho người mới.

**Các hướng này đều phù hợp với project sinh viên, vừa thực tế vừa dễ mở rộng!**
