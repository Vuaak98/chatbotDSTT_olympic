# Chatbot Toán AI

Một chatbot AI tiên tiến được thiết kế để giúp học sinh và người đi làm giải các bài toán từ số học cơ bản đến giải tích nâng cao, đại số tuyến tính, thống kê và nhiều hơn nữa. Dự án này thể hiện kỹ năng phát triển full-stack, tích hợp AI/LLM, xử lý đa phương thức đầu vào và các thực hành tốt nhất về kỹ thuật phần mềm.

## �� Điểm nổi bật của dự án

- **Giải toán từng bước** sử dụng Google Gemini LLM
- **Giải thích khái niệm toán học** với ví dụ thực tế
- **Hiển thị LaTeX** cho công thức toán đẹp mắt (KaTeX)
- **Hỗ trợ tải lên file** (ảnh, PDF, text, DOCX) với xử lý backend thông minh (**tối đa 5 file/lần**)
- **Phản hồi dạng streaming** với hiệu ứng gõ chữ thời gian thực
- **Quản lý lịch sử chat** với lưu trữ bền vững (SQLite + SQLAlchemy)
- **Xử lý lỗi mạnh mẽ** và hỗ trợ truy cập (A11y)
- **Giao diện giống ChatGPT** với các thành phần Shadcn UI
- **Thanh bên lịch sử chat** với tìm kiếm, đổi tên, xóa
- **Phản hồi của người dùng**: sao chép, tạo lại, chỉnh sửa
- **Phản hồi của AI**: sao chép, tạo lại
- **Quản lý ngữ cảnh**: lưu lịch sử chat nhiều lượt để hội thoại mạch lạc

## Ảnh demo

Một số ảnh minh họa chatbot toán AI:

- **Trang khởi đầu (Chế độ sáng):**
  ![Initial Page Light Mode](assets/Initial_page_light_mode.png)
- **Trang khởi đầu (Chế độ tối):**
  ![Initial Page Dark Mode](assets/Initial_page_dark_mode.png)
- **Demo tải file:**
  ![File Upload Demo](assets/file_upload_demo.png)
- **Demo chat:**
  ![Chat Demo](assets/demo.png)

## 🧠 Kỹ năng AI & Kỹ thuật thể hiện

- **Tích hợp Large Language Model (LLM):** Google Gemini Pro API cho giải toán nâng cao, giải thích từng bước, hiểu khái niệm
- **Prompt Engineering:** Tùy chỉnh hướng dẫn hệ thống để định nghĩa tính cách và khả năng chatbot
- **Đa phương thức đầu vào:** Backend hỗ trợ text, ảnh, PDF, DOCX; trích xuất và xử lý nội dung tối ưu cho LLM
- **Streaming & UX thời gian thực:** Phản hồi LLM dạng streaming cho cảm giác tức thì
- **Quản lý ngữ cảnh:** Lưu lịch sử chat nhiều lượt để hội thoại mạch lạc
- **Sử dụng File API:** Xử lý file lớn với Gemini File API, quản lý TTL
- **Xử lý lỗi:** Thông báo lỗi thân thiện, backend xử lý ngoại lệ và log mạnh mẽ
- **Truy cập & UX:** Đáp ứng chuẩn WCAG 2.1 AA, HTML ngữ nghĩa, điều hướng bàn phím, responsive
- **Full-stack hiện đại:** Backend FastAPI, frontend Next.js/React, Zustand, Tailwind CSS, Docker hóa

## ��️ Công nghệ sử dụng

### Backend
- Python 3.9+
- FastAPI
- Google Gen AI SDK (Gemini 2.5 Flash)
- SQLAlchemy với SQLite

### Frontend
- Next.js với TypeScript
- Tailwind CSS + Shadcn UI
- KaTeX cho hiển thị LaTeX
- Zustand quản lý trạng thái

## ��️ Cấu trúc dự án

Xem file [project-structure.md](project-structure.md) để biết chi tiết cấu trúc dự án.
- `backend/`: Ứng dụng FastAPI, API, logic nghiệp vụ, model DB, tích hợp Gemini
- `frontend/`: Ứng dụng Next.js/React, UI, quản lý trạng thái, dịch vụ API
- `docs/`: Tài liệu dự án, quy tắc, tham khảo
- `.env.example`: Mẫu biến môi trường (**nằm trong `backend/`**)
- `LICENSE`: Giấy phép MIT (xem [LICENSE](LICENSE))
- `docker-compose.yml`: Điều phối frontend & backend khi phát triển local

## 🧪 Kiểm thử

**Lưu ý:** Backend và frontend sẽ được bổ sung test ở giai đoạn sau. Dự án đã cấu trúc sẵn để dễ tích hợp test:

- **Backend:** `pytest` cho unit/integration test, `httpx` cho test API
- **Frontend:** `jest` và `react-testing-library` cho test component và tích hợp
- **E2E:** Playwright hoặc Cypress cho test luồng người dùng

## 📄 Giấy phép

Dự án này sử dụng giấy phép MIT. Xem file [LICENSE](LICENSE) để biết chi tiết.

## 🔮 Định hướng phát triển

- **Nâng cao năng lực toán:** Tích hợp tính toán ký hiệu (SymPy) cho đại số, giải phương trình
- **Đăng nhập người dùng:** Tùy chọn đăng nhập để lưu lịch sử chat, tuỳ chỉnh
- **Trang quản trị:** Thống kê, phân tích, công cụ kiểm duyệt
- **Đa ngôn ngữ:** Mở rộng hỗ trợ nhiều ngôn ngữ
- **Ứng dụng di động:** React Native hoặc Flutter cho mobile
- **A11y nâng cao:** Cải thiện hơn nữa cho trình đọc màn hình, người dùng đặc biệt
- **Triển khai cloud:** Một click lên GCP, AWS, Azure
- **Tự động kiểm thử:** CI/CD tích hợp test và deploy tự động
- **Hệ thống plugin:** Cho phép mở rộng tính năng chatbot bằng plugin
- **Máy tính:** Thêm máy tính cơ bản/khoa học vào chatbot
- **Đồ thị, biểu đồ:** Thêm khả năng vẽ đồ thị, biểu đồ từ dữ liệu
- **Vẽ canvas:** Cho phép vẽ biểu thức, hình học, đồ thị toán học
- **Kiểm thử unit/tích hợp/E2E:** Bổ sung test các cấp

## �� Liên hệ
Nếu có câu hỏi hoặc góp ý, vui lòng liên hệ:

- **GitHub:** [EvanGks](https://github.com/EvanGks)
- **X (Twitter):** [@Evan6471133782](https://x.com/Evan6471133782)
- **LinkedIn:** [Evangelos Gakias](https://www.linkedin.com/in/evangelos-gakias-346a9072)
- **Kaggle:** [evangelosgakias](https://www.kaggle.com/evangelosgakias)
- **Email:** [evangks88@gmail.com](mailto:evangks88@gmail.com)

---