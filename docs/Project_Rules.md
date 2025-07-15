# Chatbot Toán AI - Quy tắc Dự án

Tài liệu này nêu rõ các quy tắc, tiêu chuẩn và quy trình cụ thể để phát triển dự án Chatbot Toán AI. Nó bổ sung cho file `global_rules.md` bằng cách cung cấp chi tiết cụ thể cho dự án. Tất cả việc phát triển phải tuân thủ các quy tắc này khi làm việc trong Cursor AI IDE hoặc Windsurf IDE.

**Tài liệu tham khảo:**

*   `AI-MATH-CHATBOT-PRD.md`: Tài liệu Yêu cầu Sản phẩm
*   `AI_ Math_Chatbot_Development_Roadmap.md`: Lộ trình Phát triển
*   `gemini_api_doc.md`: Tài liệu API Gemini
*   `global_rules.md`: Quy tắc Phát triển và Cấu hình Toàn cầu

## 1. Thiết lập Dự án & Cơ sở hạ tầng

*   **Khởi tạo:**
    *   Backend: Python 3.9+ với FastAPI.
    *   Frontend: React với TypeScript, khởi tạo bằng Vite hoặc Create React App.
*   **Cấu trúc Thư mục:** Duy trì sự phân tách rõ ràng giữa thư mục `frontend` và `backend` ở root của dự án. Cấu hình hoặc script chung có thể đặt ở cấp root.
*   **Dependencies:**
    *   Sử dụng `requirements.txt` (backend) và `package.json` (frontend) để quản lý dependencies.
    *   Thư viện Backend bắt buộc: `google-genai`, `fastapi`, `uvicorn`, `python-docx`, `pydantic`, `sqlite3` (thư viện chuẩn), `httpx` (để fetch file từ URLs), `python-dotenv`.
    *   Thư viện Frontend bắt buộc: `react`, `react-dom`, `typescript`, `tailwindcss`, `zustand`, `katex`, `heroicons` (hoặc `feather-icons`), có thể có markdown renderer (`react-markdown`) và syntax highlighter (`react-syntax-highlighter`).
    *   Giữ dependencies cập nhật, giải quyết các lỗ hổng bảo mật kịp thời.
*   **Biến Môi trường:**
    *   Định nghĩa tất cả key nhạy cảm (Gemini API Key) và cài đặt cấu hình (ví dụ: port backend, đường dẫn file database) trong file `.env` ở root của dự án.
    *   Sử dụng `python-dotenv` (backend) hoặc xử lý biến môi trường chuẩn (frontend build process) để load các biến này.
    *   **Không bao giờ commit file `.env` vào version control.** File `.env.example` *phải* được cung cấp liệt kê các biến bắt buộc.
*   **Containerization:**
    *   Phát triển `Dockerfile` cho cả frontend (multi-stage build để serve static files qua server nhẹ như Nginx) và backend (môi trường Python).
    *   Sử dụng `docker-compose.yml` để điều phối môi trường phát triển và test local cho cả hai service. Xem Mục 6 của Roadmap.

## 2. Tiêu chuẩn Phát triển

### 2.1 Backend (Python/FastAPI)

*   **Style Guide:** Tuân thủ PEP 8. Sử dụng linters (ví dụ: Flake8, Ruff) và formatters (ví dụ: Black) được cấu hình trong IDE.
*   **Typing:** Sử dụng Python type hints rộng rãi (module `typing`). FastAPI dựa nhiều vào type hints cho validation và documentation.
*   **API Design:** Tuân theo nguyên tắc RESTful cho endpoint design như nêu trong Mục 3.1 của Roadmap. Sử dụng quy ước đặt tên rõ ràng và nhất quán.
*   **Async:** Tận dụng `async`/`await` của FastAPI cho các thao tác I/O-bound (API calls, database interactions, file reads).
*   **Error Handling:** Triển khai xử lý lỗi mạnh mẽ bằng FastAPI exception handlers. Trả về HTTP status codes và error messages có ý nghĩa (tham khảo Mục 3.6 Roadmap, Mục 4 PRD). Ghi log lỗi ở server-side.
*   **Database:** Sử dụng SQLAlchemy Core hoặc ORM cho tương tác với database SQLite. Quản lý sessions phù hợp (ví dụ: sử dụng FastAPI dependencies). Schema được định nghĩa trong Mục 3.3 của Roadmap.
*   **Modularity:** Tổ chức code thành các module logic (ví dụ: `routers`, `services`, `models`, `crud`, `utils`).

### 2.2 Frontend (React/TypeScript)

*   **Style Guide:** Tuân theo thực hành tốt chuẩn React/TypeScript. Sử dụng linters (ví dụ: ESLint) và formatters (ví dụ: Prettier) được cấu hình trong IDE.
*   **Typing:** Sử dụng TypeScript cho strong typing trên components, state, và props. Tránh `any` khi có thể.
*   **Component Structure:** Chia nhỏ UI thành các functional components có thể tái sử dụng. Tuân theo quy ước đặt tên (`PascalCase`) và tổ chức file (ví dụ: `src/components`, `src/hooks`, `src/store`, `src/services`).
*   **State Management:** Sử dụng Zustand cho global state management (chat history, active chat, theme, v.v.) như được chỉ định trong PRD. Sử dụng `useState` / `useReducer` cho local component state.
*   **Styling:** Sử dụng Tailwind CSS utility classes cho styling. Duy trì tính nhất quán với design được mô tả trong Mục 2 của PRD (minimalist, light/dark themes).
*   **API Communication:**
    *   Sử dụng native `fetch` API cho các request chuẩn đến backend.
    *   Triển khai xử lý Server-Sent Events (SSE) bằng `fetch` và `ReadableStream` cho streaming AI responses từ `/chat/stream`.
    *   Tập trung logic API call (ví dụ: trong thư mục `src/services`).
*   **Accessibility (A11y):** Triển khai các tính năng A11y cụ thể được nêu trong Mục 5 của PRD và `global_rules.md`. Sử dụng semantic HTML và ARIA attributes một cách cẩn thận.

### 2.3 Tích hợp API (Gemini)

*   **Gemini (`google-genai` SDK):**
    *   Khởi tạo client bằng API key từ biến môi trường.
    *   Target Model: `gemini-2.5-flash-preview-04-17` (xem Roadmap Mục 4, PRD Mục 6).
    *   Triển khai `generate_content_stream` hoặc `chat.send_message_stream` cho streaming responses (Roadmap Mục 4).
    *   Triển khai multi-turn chat history management bằng `client.chats` (Roadmap Mục 4).
    *   Set System Instructions qua `GenerateContentConfig` (Roadmap Mục 4).
    *   Xử lý multimodal input:
        *   Inline (`types.Part.from_bytes`): Cho file < ~20MB total request size (PDF, Images). Xem Roadmap Mục 3.4 & 4, PRD Mục 6, `gemini_api_doc.md`.
        *   Files API (`client.files.upload`): Cho file > ~20MB (lên đến 2GB). Truyền `File` object kết quả. Thừa nhận TTL 48 giờ. Xem Roadmap Mục 3.4 & 4, PRD Mục 6, `gemini_api_doc.md`.
    *   Xử lý text extraction từ `.txt` và `.docx` (bằng `python-docx`) *trước khi* gửi đến Gemini (Roadmap Mục 3.4).
    *   Cấu trúc `contents` đúng bằng `types.Content` và `types.Part` (Roadmap Mục 4, `gemini_api_doc.md`).
    *   Triển khai xử lý lỗi mạnh mẽ cho `google.genai.errors.APIError` (Roadmap Mục 4).

## 3. Xử lý File

*   **Các loại được hỗ trợ (Client & Server Validation):**
    *   PDF: `application/pdf`
    *   Images: `image/jpeg`, `image/png`, `image/webp`, `image/heic`, `image/heif`
    *   Text: `text/plain`
    *   Word: `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (.docx)
    *   Xem PRD Mục 1 & 3.
*   **Giới hạn Kích thước (Client & Server Validation):**
    *   Client-side check (ước tính) dựa trên giới hạn inline ~19MB từ PRD/Gemini Docs.
    *   Server-side check: Route đến inline processing (`types.Part.from_bytes`) hoặc Gemini Files API (`client.files.upload`) dựa trên kích thước so với giới hạn request 20MB và giới hạn file 2GB. Xem Roadmap Mục 3.4 & 4, PRD Mục 6, `gemini_api_doc.md`.
*   **Xử lý:**
    *   Backend extract text từ `.txt` và `.docx` trước khi truyền đến Gemini.
    *   PDF và Images được truyền trực tiếp đến Gemini (hoặc inline hoặc qua Files API).
*   **Frontend Display:** Hiển thị file đã stage như chips bên trong input bar với chức năng xóa ('x') (PRD Mục 1 & 3).
*   **Backend Storage:** Không có kế hoạch lưu trữ lâu dài cho file upload ngoài TTL 48 giờ của Gemini Files API. File upload cho inline processing được xử lý trong memory hoặc temporary storage trong lifecycle của request.

## 4. Kiểm thử

*   **Unit Tests:**
    *   Backend: Sử dụng `pytest`. Test các function/class riêng lẻ cho database operations, file processing logic, API payload construction, utility functions. Mock external dependencies (Gemini API, DB calls).
    *   Frontend: Sử dụng `jest` và `react-testing-library`. Test các component riêng lẻ (rendering, state changes, event handlers), utility functions, và state logic (Zustand stores).
*   **Integration Tests:**
    *   Backend: Test API endpoints bằng `pytest` và `httpx` (hoặc FastAPI's `TestClient`). Test tương tác giữa các component (ví dụ: router -> service -> crud). Test tương tác với test database. Mock external APIs (Gemini).
    *   Frontend-Backend: Test luồng dữ liệu giữa frontend và backend API endpoints (ví dụ: gửi message, nhận stream, upload file).
*   **End-to-End (E2E) Tests:**
    *   Sử dụng tools như Playwright hoặc Cypress.
    *   Mô phỏng các user flow chính được mô tả trong PRD: basic text chat, file upload interaction, chat history management (new, load, rename, delete).
    *   Cover streaming response display và interruption.
*   **Coverage:** Hướng tới test coverage hợp lý, tập trung vào critical paths và business logic.
*   **CI/CD:** Tích hợp tests vào Continuous Integration pipeline (nếu có) để chạy tự động trên commits/PRs.

## 5. Triển khai

*   **Phương pháp:** Chủ yếu qua Docker Compose cho local setup và có thể cho các deployment đơn giản.
*   **Artifacts:** Đảm bảo Dockerfiles và `docker-compose.yml` hoạt động và được tối ưu (ví dụ: multi-stage builds, minimal base images).
*   **Cấu hình:** Deployment configuration (ports, volumes, environment variables) phải được định nghĩa rõ ràng trong `docker-compose.yml` hoặc platform-specific configuration files.
*   **Documentation:** Cung cấp hướng dẫn rõ ràng, từng bước trong `README.md` chính để build và chạy ứng dụng bằng Docker Compose.
*   **Platform:** Mặc dù không được chỉ định, đảm bảo Dockerized setup đủ platform-agnostic để deploy trên các cloud platform phổ biến (ví dụ: Cloud Run, AWS ECS, Azure Container Apps) với thay đổi tối thiểu.

## 6. Cột mốc Dự án

Phát triển phải tiến triển theo các cột mốc được định nghĩa trong `AI_ Math_Chatbot_Development_Roadmap.md`:

*   **Milestone 1:** Basic Text Chat (Core UI, Backend API, Gemini Text, Streaming, DB History)
*   **Milestone 2:** File Uploads (File UI, Backend Processing, Gemini Multimodal/Files API)
*   **Milestone 3:** Chat History Management (Sidebar UI, CRUD Operations)
*   **Milestone 4:** Refinement (Error Handling, A11y, Responsiveness, Dockerization Finalization)

Theo dõi tiến độ so với các cột mốc này bằng project management tools hoặc issue tracking.

---