# Chatbot Toán AI - Frontend

Đây là **frontend** cho ứng dụng Chatbot Toán AI, xây dựng với Next.js, React, TypeScript và Tailwind CSS. Giao diện hiện đại, dễ truy cập, đáp ứng tốt cho việc tương tác với trợ lý toán học AI.

## 🌟 Tính năng nổi bật

- **Giao diện chat tương tác** với trợ lý toán học AI (phản hồi dạng streaming)
- **Tải lên file** (PDF, ảnh, file text, Word) với xem trước và xóa (**tối đa 5 file/lần**)
- **Quản lý lịch sử chat** (đa lượt, lưu trữ bền vững)
- **Thiết kế responsive** với chế độ sáng/tối
- **Giao diện dễ truy cập** (chuẩn WCAG 2.1 AA, HTML ngữ nghĩa, điều hướng bàn phím)
- **Hiển thị công thức toán (LaTeX/Math)** với KaTeX
- **Quản lý trạng thái** với Zustand

## 👨‍💻 Kỹ thuật & Thực hành hiện đại

- **TypeScript** đảm bảo an toàn kiểu dữ liệu, dễ bảo trì
- **Tailwind CSS** cho style tiện lợi, responsive
- **shadcn/ui** cho các thành phần UI dễ truy cập, dễ mở rộng
- **Zustand** quản lý trạng thái linh hoạt
- **Tích hợp API** với backend FastAPI (xem [README chính](../README.md))
- **A11y:** HTML ngữ nghĩa, ARIA, điều hướng bàn phím, tương phản màu sắc
- **Hiệu năng:** Tách code, tối ưu tài nguyên, giảm kích thước bundle

## 🚀 Bắt đầu sử dụng

### Yêu cầu

- Node.js 18 trở lên
- Backend API đã chạy (xem hướng dẫn backend ở [README chính](../README.md))

### Cài đặt

1. Cài đặt thư viện:

```bash
npm install
# hoặc
yarn install
# hoặc
pnpm install
```

2. Tạo file `.env.local` trong thư mục frontend:

```
# Địa chỉ API backend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

3. Chạy server phát triển:

```bash
npm run dev
# hoặc
yarn dev
# hoặc
pnpm dev
```

4. Mở [http://localhost:3000](http://localhost:3000) trên trình duyệt.

## 🔗 Kết nối với Backend

Frontend giao tiếp với backend qua các endpoint:

- `/chats`, `/chats/{chat_id}`: Quản lý lịch sử chat
- `/chats/{chat_id}/stream`: Nhận phản hồi chat dạng streaming
- `/upload-file`: Tải file (tối đa 5 file/lần)

Xem [project-structure.md](../project-structure.md) để biết chi tiết cấu trúc dự án.

## 🛠️ Kiến trúc & Tích hợp API

- `lib/api-service.ts`: Hàm API chính cho chat, tải file
- `lib/api-config.ts`: Cấu hình API
- `lib/store.ts`: Zustand store tích hợp backend
- `components/`: Các thành phần React (chat, sidebar, markdown, ...)
- `hooks/`: Custom hook cho UI và logic trạng thái

## 🧪 Kiểm thử

**Lưu ý:** Frontend sẽ được bổ sung test ở giai đoạn sau. Dự án đã cấu trúc sẵn để dễ tích hợp test:

- `jest` và `react-testing-library` cho test component và tích hợp
- Playwright hoặc Cypress cho test luồng người dùng

## 🏗️ Cấu trúc dự án

Xem [project-structure.md](../project-structure.md) để biết chi tiết frontend và toàn bộ dự án.

## 🏭 Build production

```bash
npm run build
# hoặc
yarn build
# hoặc
pnpm build
```

## 🚢 Triển khai

Frontend có thể triển khai lên Vercel, Netlify hoặc bất kỳ dịch vụ nào hỗ trợ Next.js.

- Đặt biến `NEXT_PUBLIC_API_BASE_URL` trỏ về API backend production.

## 🔮 Định hướng phát triển

- **Giao diện máy tính:** Thêm máy tính cơ bản/khoa học
- **Đồ thị, biểu đồ:** Vẽ đồ thị, biểu đồ tương tác từ dữ liệu người dùng
- **Vẽ canvas:** Vẽ, chú thích biểu thức toán, hình học, đồ thị
- **Ứng dụng di động:** React Native hoặc PWA cho mobile
- **A11y nâng cao:** Cải thiện hơn nữa cho trình đọc màn hình, người dùng đặc biệt
- **Đa ngôn ngữ:** Hỗ trợ nhiều ngôn ngữ
- **Hệ thống plugin:** Cho phép mở rộng chatbot bằng UI plugin
- **Kiểm thử tự động:** Bổ sung test unit/tích hợp/E2E

---

**Thể hiện kỹ năng frontend của bạn:** Dự án này hướng tới chất lượng portfolio, sẵn sàng production, là ví dụ điển hình về phát triển ứng dụng web AI hiện đại. Rất hoan nghênh đóng góp và phản hồi! 