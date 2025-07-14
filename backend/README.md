# Chatbot Toán AI - Backend

Đây là **backend** cho ứng dụng Chatbot Toán AI, xây dựng với FastAPI, SQLAlchemy và Google Gemini API. Backend cung cấp các API mạnh mẽ, bảo mật và mở rộng cho chat, tải file, chuyển giọng nói thành văn bản và quản lý lịch sử chat.

## 🌟 Tính năng nổi bật

- **RESTful API** cho chat, tải file và chuyển giọng nói thành văn bản
- **Phản hồi LLM dạng streaming** (Google Gemini 2.5 Flash)
- **Hỗ trợ đa phương thức đầu vào:** text, ảnh, PDF, DOCX
- **Lưu lịch sử chat bền vững** với SQLite + SQLAlchemy
- **Quản lý file** (xử lý trực tiếp và qua Gemini Files API, **tối đa 5 file/lần**)
- **Xử lý lỗi mạnh mẽ** và ghi log
- **Giới hạn tốc độ** và làm sạch đầu vào để bảo mật
- **Tự động bảo trì nền** (xóa file hết hạn, dọn dẹp tin nhắn)

## 👨‍💻 Kỹ thuật & Thực hành tốt

- **FastAPI** cho phát triển API hiệu năng cao, bất đồng bộ
- **SQLAlchemy ORM** cho truy cập cơ sở dữ liệu an toàn, hiệu quả
- **Alembic** cho quản lý migration database
- **Xử lý lỗi tập trung** với middleware và handler ngoại lệ tùy chỉnh
- **Ghi log có cấu trúc** để debug và giám sát
- **Cấu hình theo môi trường** (xem `.env.example`)
- **Bảo mật:**
  - Quản lý API key qua biến môi trường
  - Làm sạch đầu vào (text, tên file, MIME type)
  - Giới hạn tốc độ theo endpoint
  - Không ghi log hoặc trả về dữ liệu nhạy cảm
- **Kiến trúc module hóa:** routers, services, CRUD, middleware, utils

## 🏗️ Cấu trúc dự án

Xem [project-structure.md](../project-structure.md) để biết chi tiết backend và toàn bộ dự án.

## ⚙️ Quản lý cơ sở dữ liệu

- **SQLite** cho phát triển local (có thể cấu hình qua `DATABASE_URL`)
- **Schema:** Chats, Messages, GeminiFiles (xem `app/models.py`)
- **Script quản lý:** `db_manager.py` cho khởi tạo, seed, reset, backup, clean, check
- **Migration:** Alembic cho thay đổi schema

## 🛡️ Bảo mật & Xử lý lỗi

- **Xử lý lỗi tập trung:**
  - `ErrorHandlerMiddleware` bắt ngoại lệ toàn cục
  - Handler tùy chỉnh cho lỗi validate, HTTP, Gemini API
- **Giới hạn tốc độ:**
  - Middleware `RateLimiter` với cấu hình riêng cho từng endpoint
- **Làm sạch đầu vào:**
  - Kiểm tra và làm sạch text, tên file, MIME type
- **Quản lý API key:**
  - Tất cả secret lấy từ biến môi trường, không hardcode

## 🔗 Các endpoint API

- `POST /chats`: Tạo chat mới
- `GET /chats`: Lấy tất cả chat
- `GET /chats/{chat_id}`: Lấy chat cụ thể
- `PUT /chats/{chat_id}`: Cập nhật chat
- `DELETE /chats/{chat_id}`: Xóa chat
- `POST /chats/{chat_id}/messages/`: Gửi tin nhắn vào chat
- `GET /chats/{chat_id}/messages/`: Lấy tất cả tin nhắn trong chat
- `POST /chats/{chat_id}/stream`: Gửi tin nhắn và nhận phản hồi dạng streaming
- `POST /upload-file`: Tải tối đa 5 file (PDF, ảnh, DOCX, text) cùng lúc

## 🏃‍♂️ Chạy backend

```bash
# Cài đặt thư viện
pip install -r requirements.txt

# Khởi tạo database
python db_manager.py init

# Chạy server
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## 🧪 Kiểm thử

**Lưu ý:** Backend sẽ được bổ sung test ở giai đoạn sau. Dự án đã cấu trúc sẵn để dễ tích hợp test:

- `pytest` cho unit/integration test
- `httpx` hoặc FastAPI `TestClient` cho test API
- Mock API ngoài (Gemini, Whisper)

## 🗂️ Thông tin thêm

- Xem [README chính](../README.md) để biết hướng dẫn tổng thể, tính năng, triển khai
- Xem [project-structure.md](../project-structure.md) để biết chi tiết thư mục

## 🔍 Định hướng phát triển

- **Công cụ quản trị nâng cao:** Dashboard phân tích, thống kê, kiểm duyệt
- **Hệ thống plugin:** Cho phép mở rộng backend bằng plugin mới
- **Thêm phân tích:** Theo dõi sử dụng API, lỗi, hiệu năng
- **Giới hạn tốc độ nâng cao:** Theo người dùng, thích ứng, hoặc thuật toán token bucket
- **Hỗ trợ nhiều DB:** Thêm PostgreSQL hoặc MySQL
- **Tự động kiểm thử:** CI/CD tích hợp test và deploy tự động
- **Đa ngôn ngữ:** Backend hỗ trợ i18n cho lỗi và log
- **Quét file nâng cao:** Quét mã độc cho file upload
- **Đăng nhập người dùng:** Tùy chọn đăng nhập để lưu lịch sử chat, cá nhân hóa

---

**Thể hiện kỹ năng backend của bạn:** Dự án này hướng tới chất lượng portfolio, sẵn sàng production, là ví dụ điển hình về phát triển API AI hiện đại. Rất hoan nghênh đóng góp và phản hồi!