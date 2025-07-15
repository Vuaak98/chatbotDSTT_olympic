# Lộ trình phát triển Chatbot Toán AI

Tài liệu này liệt kê các đầu việc cần thực hiện để xây dựng Chatbot Toán AI dựa trên PRD và tài liệu Gemini API.

## 1. Khởi tạo dự án & hạ tầng

- [x] Khởi tạo backend (Python/FastAPI)
- [x] Khởi tạo frontend (React + TypeScript)
- [x] Thiết lập cấu trúc dự án, cài dependencies (`google-genai`, `python-docx`, FastAPI, Uvicorn, SQLite driver, React, TypeScript, Tailwind CSS, Zustand, KaTeX)
- [x] Cấu hình biến môi trường cho API key (Gemini) và backend
- [x] Thiết lập Dockerfile, Docker Compose cho frontend và backend

## 2. Phát triển Frontend

### 2.1 Giao diện chat cơ bản

- [x] Thiết kế layout chính full màn hình
- [x] Header tĩnh (tiêu đề, chuyển theme, nút xóa)
- [x] Khu vực chat cuộn được
- [x] Trạng thái ban đầu: Hiển thị lời chào ("Hãy hỏi tôi bất cứ điều gì về toán!")
- [x] Vị trí input ban đầu: căn giữa trước khi gửi tin nhắn đầu tiên
- [x] Logic chuyển input xuống dưới sau khi có tin nhắn
- [x] Textarea đa dòng trong input
- [x] Nút gửi
- [x] Nút tải file (paperclip)
- [x] Tự động co giãn chiều cao textarea, có scrollbar khi vượt max
- [x] Placeholder động (ví dụ: "Giải thích định lý Pytago...")

### 2.2 Style & thẩm mỹ ChatGPT

- [x] Cấu hình Tailwind CSS
- [x] Phong cách tối giản, tập trung nội dung
- [x] Màu sáng: nền trắng, bong bóng xám nhạt, text đen, input trắng
- [x] Màu tối: nền xám đậm, bong bóng xám, text trắng
- [x] Nút chuyển theme
- [x] Font sans-serif, đồng nhất kích thước
- [x] Padding, margin theo lưới 8px, bong bóng chat rộng rãi
- [x] Bộ icon đồng nhất (Heroicons, Feather Icons)
- [x] Tin nhắn user: căn phải, bọc bong bóng màu riêng
- [x] Tin nhắn AI: căn trái, không bọc bong bóng, text rộng hơn input
- [x] Tích hợp KaTeX hiển thị công thức toán
- [x] Code block: font mono, highlight, nền riêng, nút copy
- [x] Input, sidebar style theo ChatGPT cho cả sáng/tối
- [x] Sidebar cố định desktop, thu gọn/off-canvas mobile

### 2.3 Hiển thị & tương tác tin nhắn

- [x] Hiển thị tin nhắn user
- [x] Hiển thị tin nhắn AI
- [x] Hỗ trợ markdown trong tin nhắn
- [x] Nút Copy/Edit/Regenerate cho user
- [x] Nút Copy/Regenerate cho AI
- [x] Copy bằng Clipboard API
- [x] Edit: chuyển nội dung lên input
- [x] Regenerate: gửi lại prompt

### 2.4 Input & phản hồi

- [x] Logic trạng thái nút gửi (chỉ bật khi có text/file)
- [x] Nút gửi chuyển thành nút dừng khi AI đang trả lời
- [x] Nút dừng gửi tín hiệu ngắt AI
- [x] Hiển thị "Đang suy nghĩ..." khi AI trả lời
- [x] Nút tải file mở file picker
- [x] Kiểm tra loại file, dung lượng phía client
- [x] Hiển thị file đã chọn dạng chip, có nút xóa
- [x] Logic xóa file khỏi input

### 2.5 Sidebar lịch sử chat

- [x] Sidebar thu gọn/off-canvas mobile
- [x] Nút toggle sidebar
- [x] Nút chat mới (clear view, lưu chat cũ, bắt đầu mới)
- [x] Danh sách lịch sử chat cuộn được
- [x] Hiển thị tiêu đề rút gọn (tin nhắn đầu tiên)
- [x] Highlight chat đang chọn
- [x] Click để load lại lịch sử
- [x] Đổi tên chat (hover/double click, gọi backend)
- [x] Xóa chat (hover, gọi backend)
- [x] Xác nhận khi xóa
- [x] Nút xóa nhanh chat hiện tại (header, xác nhận)

### 2.6 Responsive & Accessibility

- [x] Responsive (mobile: sidebar off-canvas, tablet/desktop: sidebar hiện)
- [x] HTML ngữ nghĩa cho A11y
- [x] Điều hướng bàn phím đầy đủ
- [x] Quản lý focus hợp lý khi tương tác
- [x] Thêm ARIA cho screen reader, KaTeX accessible
- [x] Kiểm tra tương phản màu sáng/tối
- [x] Test UI khi zoom 200%
- [x] Label cho form control

### 2.7 Phản hồi người dùng & lỗi

- [x] Hiển thị feedback khi copy (icon đổi, toast "Đã copy!")
- [x] Hiển thị lỗi input (file, text) gần input
- [x] Hiển thị lỗi API/toàn cục (toast hoặc AI message)
- [x] Thông báo lỗi thân thiện cho lỗi backend/API

## 3. Phát triển Backend

### 3.1 Khởi tạo server & routing

- [x] Tạo app FastAPI
- [x] Định nghĩa endpoint:
    - `/chat/stream` (POST gửi tin nhắn, xử lý text/file, trả về streaming)
    - `/chat/history` (GET danh sách chat)
    - `/chat/history/{chat_id}` (GET lịch sử chat cụ thể)
    - `/chat/history` (POST tạo chat mới khi gửi tin đầu tiên)
    - `/chat/history/{chat_id}` (PUT đổi tên chat)
    - `/chat/history/{chat_id}` (DELETE xóa chat và tin nhắn)
    - `/interrupt` (POST ngắt AI nếu cần)

### 3.2 Logic chat chính

- [x] Nhận tin nhắn user (text, file)
- [x] Lưu lịch sử hội thoại theo chat_id
- [x] Tạo prompt gửi Gemini API (system instruction, history, user message, file context)
- [x] Gửi prompt tới Gemini API qua `google-genai` SDK
- [x] SSE trả về từng token cho frontend
- [x] Lưu hội thoại vào DB (user, AI, chat_id)
- [x] Xử lý tín hiệu ngắt từ frontend

### 3.3 Tích hợp DB (SQLite)

- [x] Thiết kế schema bảng `chats`, `messages`
- [x] Kết nối, quản lý session DB
- [x] CRUD chat (tạo, lấy, đổi tên, xóa)
- [x] CRUD message (thêm, lấy theo chat_id, sắp xếp theo thời gian)

### 3.4 Xử lý file

- [x] Xử lý file từ frontend (PDF/Image gửi Gemini, TXT/DOCX trích text)
- [x] Kiểm tra dung lượng file trước khi gửi Gemini
- [x] Đọc nội dung `.txt` trên backend
- [x] Trích text `.docx` bằng `python-docx`
- [x] Chuẩn bị dữ liệu gửi Gemini (bytes cho PDF/Image, text cho TXT/DOCX)

### 3.5 Xử lý lỗi & bảo mật

- [x] Xử lý lỗi backend (API, file, DB). Trả về mã lỗi và thông báo thân thiện
- [x] Ghi log lỗi chi tiết
- [x] Làm sạch input (text, file) chống injection
- [x] Giới hạn tốc độ các endpoint chính
- [x] Quản lý API key qua biến môi trường
- [x] Kiểm tra loại file trước khi xử lý

## 4. Tích hợp API Gemini

- [x] Khởi tạo `google.genai.Client` trong backend
- [x] Cấu hình dùng model `gemini-2.5-flash-preview-04-17`
- [x] Gửi prompt qua `client.models.generate_content_stream`
- [x] (Tùy chọn) Dùng chat object của SDK để quản lý lịch sử
- [x] Thêm system instruction vào config
- [x] Xử lý input đa phương thức (PDF/Image gửi trực tiếp, TXT/DOCX trích text)
- [x] Lưu ý TTL 48h của Files API
- [x] Xử lý lỗi Gemini API
- [x] (Tùy chọn) Đếm token trước khi gửi

## 5. Kiểm thử

- [ ] Viết unit test cho backend (hàm tiện ích, API, DB)
- [ ] Viết unit test cho frontend (component, store Zustand)
- [ ] Viết integration test cho frontend-backend (gửi tin, file, nhận SSE, lịch sử)
- [ ] Viết integration test cho backend-Gemini (mock API Gemini, test các loại input)
- [ ] Viết E2E test (Playwright/Cypress):
    - Gửi text -> nhận streaming
    - Upload file -> nhận phản hồi
    - Tạo chat mới, đổi tên, xóa, chuyển chat

---

**Lộ trình này có thể điều chỉnh tùy theo yêu cầu thực tế và phản hồi từ người dùng.**

## Gợi ý tối ưu hóa trình bày lời giải toán học (Markdown/LaTeX)

- Luôn trình bày lời giải từng bước, mỗi bước một dòng, sử dụng markdown heading (##, ###) và danh sách đánh số hoặc gạch đầu dòng.
- Sau mỗi công thức toán học, luôn xuống dòng (2 dấu xuống dòng hoặc 1 dòng trắng).
- Không viết dính toàn bộ lời giải thành một đoạn văn.
- Sử dụng block math ($$...$$) cho các phương trình quan trọng, và inline math ($...$) cho công thức trong dòng.
- Ví dụ trình bày tối ưu:

```
## Bước 1: Thiết lập phương trình
Gọi $x_i$ là lượng cocacola ban đầu của người thứ $i$ $(i=1,2,3,4,5)$. Tổng:
$$
x_1 + x_2 + x_3 + x_4 + x_5 = 40
$$

## Bước 2: Mô hình hóa quá trình chia sẻ
- Khi người $k$ chia sẻ, lượng của mỗi người thay đổi như sau:
  - $a_k^{(k)} = a_k^{(k-1)}/5$
  - $a_i^{(k)} = a_i^{(k-1)} + a_k^{(k-1)}/5$ với $i \neq k$

## Bước 3: Lần ngược quá trình
...

## Bước 4: Tính giá trị cụ thể
...

## Kết luận
Vậy, lượng cocacola ban đầu mỗi bạn nhận được là:
- $x_1 = \frac{40}{3}$ lít
- $x_2 = \frac{32}{3}$ lít
- $x_3 = 8$ lít
- $x_4 = \frac{16}{3}$ lít
- $x_5 = \frac{8}{3}$ lít
```

- Khi viết prompt cho AI, nên yêu cầu rõ: "Luôn trình bày từng bước, mỗi bước một heading hoặc dòng riêng, sử dụng markdown, không viết dính đoạn văn."