# Đặc tả sản phẩm (PRD) - Chatbot Toán AI

## 1. Luồng trải nghiệm người dùng tổng quan

*   **Trạng thái ban đầu:** Người dùng truy cập ứng dụng, giao diện chính sạch sẽ, thanh input ở giữa màn hình, hiển thị lời chào ("Hãy hỏi tôi bất cứ điều gì về toán!"). Sidebar bên trái có nút "Chat mới" và danh sách lịch sử chat (ẩn trên mobile, thu gọn mặc định trên desktop).
*   **Luồng hỏi đáp bằng text:**
    1.  Người dùng nhập câu hỏi toán vào ô input. Input tự co giãn chiều cao, tối đa 200px, sau đó xuất hiện scrollbar.
    2.  Nhấn nút gửi hoặc Enter để gửi.
    3.  Nút gửi chuyển thành nút dừng, tin nhắn user hiển thị bên phải (bọc bong bóng).
    4.  AI hiển thị "Đang suy nghĩ..." bên trái.
    5.  Phản hồi AI stream từng token vào khung chat (bên trái, không bọc bong bóng, có render công thức KaTeX).
    6.  Có thể nhấn dừng để ngắt AI.
    7.  Khi xong, nút dừng trở lại thành nút gửi.
*   **Luồng hỏi đáp với file:**
    1.  Nhấn nút tải file (paperclip), chọn file PDF, ảnh, text, Word.
    2.  File hiển thị dạng chip trong input, có nút xóa.
    3.  Nhập câu hỏi liên quan file vào input.
    4.  Nhấn gửi.
    5.  Tin nhắn user hiển thị, AI xử lý file (trích text hoặc gửi Gemini), trả về kết quả.
    6.  Phản hồi AI stream vào chat.
*   **Quản lý lịch sử chat:**
    1.  Nhấn "Chat mới" để xóa khung chat, bắt đầu mới. Chat cũ lưu vào sidebar.
    2.  Nhấn vào chat cũ để xem lại lịch sử.
    3.  Đổi tên/xóa chat qua menu (hover hoặc click, xác nhận khi xóa).
*   **Xóa nhanh chat hiện tại:**
    1.  Nhấn icon thùng rác (góc trên phải).
    2.  Hiện dialog xác nhận.
    3.  Xác nhận sẽ xóa khung chat hiện tại (không lưu vào lịch sử).
*   **Responsive:**
    *   **Mobile:** Sidebar ẩn, truy cập qua menu hamburger. Input, chức năng vẫn đầy đủ.
    *   **Tablet/Desktop:** Sidebar hiện, có thể thu gọn.

## 2. Giao diện & style

*   **Tổng thể:** Tối giản, tập trung nội dung, giống ChatGPT (sáng/tối, font, spacing). **Không cần đăng nhập.**
*   **Thành phần:**
    *   **Khung chính:** Full màn hình.
    *   **Sidebar:**
        *   Cố định desktop (260px), thu gọn được. Off-canvas trên mobile.
        *   Có nút "Chat mới", danh sách lịch sử, chuyển theme, cài đặt.
    *   **Khu vực chat:**
        *   Header mỏng trên cùng (chuyển theme, thùng rác, tiêu đề chatbot).
        *   Khu vực chat cuộn được.
        *   Tin nhắn user: căn phải, bọc bong bóng.
        *   Tin nhắn AI: căn trái, không bọc bong bóng, text rộng hơn input.
        *   Input cố định dưới cùng, gồm: nút tải file, textarea, nút gửi/dừng.
*   **Chi tiết style:**
    *   **Màu sắc:**
        *   Sáng: nền trắng, bong bóng xám nhạt, text đen, input trắng.
        *   Tối: nền xám đậm, bong bóng xám, input xám, text trắng.
        *   Màu nhấn xanh lá/teal nhẹ cho nút, icon, link.
    *   **Font:** Sans-serif, đồng nhất kích thước.
    *   **Spacing:** Padding/margin theo lưới 8px, bong bóng chat rộng rãi.
    *   **Icon:** Bộ icon đồng nhất (Heroicons, Feather Icons).
    *   **Công thức toán:** KaTeX render LaTeX đẹp, tích hợp mượt trong chat.
    *   **Code block:** Font mono, highlight, nền riêng, nút copy.

## 3. Tính năng & tương tác

*   **Input:**
    *   Textarea đa dòng.
    *   Placeholder động gợi ý ("Giải thích định lý Pytago", ...).
    *   Nút gửi bật khi có text/file.
    *   Shift+Enter xuống dòng, Enter gửi (nếu AI đang trả lời thì Enter ngắt).
    *   Hiển thị file chip khi upload.
*   **Nút tải file:**
    *   Mở file picker.
    *   Nhận `.pdf`, `.png`, `.jpg`, `.jpeg`, `.webp`, `.heic`, `.heif`, `.txt`, `.docx`.
    *   Hiển thị chip file, có nút xóa.
    *   Kiểm tra dung lượng, loại file phía client và server.
*   **Tin nhắn:**
    *   User: bọc bong bóng, căn phải, hover hiện nút Copy/Edit/Regenerate.
    *   AI: text block, căn trái, hover hiện Copy/Regenerate.
    *   Hỗ trợ markdown, KaTeX, code block có nút copy.
*   **Lịch sử chat:**
    *   Highlight chat đang chọn.
    *   Hiển thị tiêu đề rút gọn.
    *   Đổi tên/xóa chat (hover/click, xác nhận).
*   **Loading:** Hiện "Đang suy nghĩ..." khi AI trả lời.
*   **Copy:** Khi copy, icon đổi thành tick, hiện toast "Đã copy!".

## 4. Phản hồi & xử lý lỗi

*   **Feedback:**
    *   Gửi: nút gửi thành dừng.
    *   Loading: "Đang suy nghĩ...".
    *   AI trả lời: stream từng token.
    *   Tải file: chip file hiện trong input, lỗi hiển thị gần input.
    *   Copy: icon đổi, toast "Đã copy!".
    *   Ngắt: dừng AI, nút dừng về gửi.
*   **Xử lý lỗi:**
    *   Lỗi mạng: thông báo rõ, có nút thử lại.
    *   Lỗi backend/API: thông báo thân thiện, log server. Lỗi Gemini trả về rõ ràng.
    *   Lỗi file: "File quá lớn", "Loại file không hỗ trợ", "Tải file thất bại", "Không trích xuất được text Word".
    *   Lỗi input: disable gửi nếu không có text/file. Kiểm tra prompt quá dài.
    *   Vị trí hiển thị: lỗi input gần input, lỗi chung là toast hoặc AI message.

## 5. Accessibility (A11y)

*   **HTML ngữ nghĩa:** Dùng `<nav>`, `<main>`, `<aside>`, `<button>`, `<input>`, `textarea`, heading hợp lý.
*   **Điều hướng bàn phím:** Tất cả thành phần đều focus, tab hợp lý, Enter/Space kích hoạt nút.
*   **Quản lý focus:** Focus vào input khi load, chuyển focus hợp lý khi thao tác.
*   **Screen reader:** ARIA, thông báo message, loading, lỗi. KaTeX accessible.
*   **Tương phản màu:** Đảm bảo đủ sáng/tối.
*   **Text co giãn:** UI không vỡ khi zoom 200%.
*   **Form:** Label đầy đủ cho input.

## 6. Công nghệ sử dụng

*   **Frontend:**
    *   **React (TypeScript)**
    *   **Tailwind CSS**
    *   **Zustand**
    *   **KaTeX**
    *   **Heroicons/Feather Icons**
    *   **fetch API** (chuẩn, hỗ trợ streaming SSE)
*   **Backend:**
    *   **Python / FastAPI**
    *   **google-genai SDK**
    *   **Gemini 2.5 Flash** (xử lý toán, đa phương thức, context dài)
    *   **python-docx** (trích text Word)
    *   **SQLite** (lưu lịch sử chat)
    *   **Files API** (xử lý file lớn, TTL 48h)
*   **Triển khai:**
    *   **Docker & Docker Compose**

**Lưu ý:**
- Bảo mật: Làm sạch mọi input, bảo vệ prompt injection, quản lý API key qua biến môi trường, kiểm tra loại/dung lượng file, giới hạn tốc độ backend.
- Không tập trung mở rộng, tối ưu chi phí, xác thực người dùng.
- Nên bổ sung test unit, tích hợp, E2E cho các luồng chính.
