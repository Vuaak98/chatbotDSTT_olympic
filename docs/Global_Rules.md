# Quy tắc Phát triển & Cấu hình Toàn cầu

Tài liệu này nêu rõ các quy tắc, tiêu chuẩn và thực hành tốt toàn cầu áp dụng cho các dự án được phát triển bằng Cursor AI IDE và Windsurf IDE. Nó phục vụ như một baseline cho chất lượng, tính nhất quán và khả năng bảo trì trên các dự án khác nhau, bao gồm Chatbot Toán AI. Các quy tắc cụ thể cho dự án có thể ghi đè hoặc mở rộng các hướng dẫn này như được ghi lại trong `project_rules.md` tương ứng.

## 1. Khả năng Truy cập (A11y) & Trải nghiệm Người dùng (UX)

*   **Tuân thủ:** Phấn đấu tuân thủ **WCAG 2.1 AA** trong tất cả UI dựa trên web.
*   **Semantic HTML:** Sử dụng các element HTML theo ý nghĩa ngữ nghĩa của chúng (`<nav>`, `<main>`, `<aside>`, `<button>`, `<article>`, v.v.). Tránh sử dụng `<div>` hoặc `<span>` cho các element tương tác; sử dụng `<button>` hoặc `<a>` thay thế.
*   **Điều hướng Bàn phím:** Tất cả element tương tác *phải* có thể điều hướng và hoạt động chỉ bằng bàn phím. Đảm bảo thứ tự tab logic. Sử dụng style `outline` cho focus indicators (không tắt mà không cung cấp alternative rõ ràng).
*   **Hỗ trợ Screen Reader:**
    *   Sử dụng ARIA attributes (`aria-label`, `aria-labelledby`, `aria-describedby`, `aria-live`, `aria-hidden`, roles) phù hợp để tăng cường hiểu biết của screen reader, đặc biệt cho dynamic content updates và custom controls.
    *   Đảm bảo hình ảnh có `alt` text mô tả hoặc được đánh dấu là decorative (`alt=""`).
    *   Đảm bảo form elements có labels liên kết.
*   **Tương phản Màu sắc:** Duy trì tỷ lệ tương phản màu sắc đủ cho text và UI elements theo hướng dẫn WCAG AA (4.5:1 cho text bình thường, 3:1 cho text lớn và graphical elements). Test trong cả light và dark themes nếu có thể.
*   **Text Có thể Thay đổi Kích thước:** Đảm bảo UI reflow đúng và vẫn sử dụng được khi kích thước text được tăng lên đến 200% qua cài đặt zoom của browser. Tránh fixed heights cắt text.
*   **Thiết kế Responsive:** Thiết kế UI responsive trên các kích thước màn hình khác nhau (mobile, tablet, desktop). Sử dụng mobile-first hoặc desktop-first approaches một cách nhất quán trong dự án. Tận dụng CSS media queries hoặc responsive frameworks (như Tailwind CSS breakpoints).
*   **Phản hồi Người dùng:** Cung cấp phản hồi trực quan rõ ràng cho hành động người dùng (ví dụ: button clicks, loading states, success/error notifications, progress indicators). Sử dụng patterns đã thiết lập như spinners, skeletons, toasts, và inline messages.
*   **Tính nhất quán:** Duy trì tính nhất quán trong UI elements, terminology, layout, navigation, và interaction patterns trong toàn bộ ứng dụng.

## 2. Xử lý Lỗi & Ghi Log

*   **Lỗi Hướng đến Người dùng:**
    *   Hiển thị lỗi theo cách thân thiện với người dùng. Tránh tiết lộ technical details hoặc stack traces trực tiếp cho người dùng.
    *   Cung cấp error messages rõ ràng, có thể hành động khi có thể (ví dụ: "Invalid email format" thay vì "Error code 5.2.1").
    *   Hiển thị lỗi theo ngữ cảnh (ví dụ: gần input field cho validation errors) hoặc toàn cục (ví dụ: toasts/banners cho API hoặc server errors).
*   **Xử lý Lỗi Backend:**
    *   Triển khai centralized error handling (ví dụ: FastAPI middleware hoặc exception handlers).
    *   Bắt specific exceptions thay vì generic `Exception`.
    *   Map internal errors đến appropriate HTTP status codes (4xx cho client errors, 5xx cho server errors).
*   **Ghi Log:**
    *   Triển khai structured logging trên backend (ví dụ: sử dụng Python's `logging` module).
    *   Ghi log thông tin liên quan cho debugging: timestamps, severity levels (INFO, WARNING, ERROR, CRITICAL), request IDs, user context (nếu có), error messages, và stack traces cho critical errors.
    *   Tránh ghi log sensitive user data (passwords, API keys, PII).
    *   Cân nhắc ghi log key events hoặc application flow milestones ở INFO level cho monitoring.

## 3. Bảo mật

*   **Quản lý API Key:**
    *   **Không bao giờ hardcode API keys** hoặc secrets khác trong source code.
    *   Sử dụng environment variables (`.env` files locally, secure secrets management trong deployment) để lưu trữ credentials nhạy cảm.
    *   Đảm bảo `.env` files được liệt kê trong `.gitignore`. Cung cấp `.env.example` template.
*   **Làm sạch & Xác thực Đầu vào:**
    *   Validate và sanitize *tất cả* input từ users hoặc external systems trên **backend**. Điều này bao gồm text input, file uploads, API parameters, v.v.
    *   Bảo vệ chống lại các lỗ hổng phổ biến như Cross-Site Scripting (XSS), SQL Injection (sử dụng ORMs hoặc parameterized queries), và Prompt Injection (xử lý cẩn thận user input truyền cho LLMs).
*   **Bảo mật Dependencies:** Thường xuyên scan project dependencies cho known vulnerabilities bằng tools như `npm audit`, `pip-audit`, hoặc IDE integrations. Cập nhật vulnerable dependencies kịp thời.
*   **Giới hạn Tốc độ:** Triển khai basic rate limiting trên public-facing hoặc resource-intensive API endpoints để ngăn chặn lạm dụng.
*   **File Uploads:**
    *   Validate file types và sizes nghiêm ngặt trên backend (không chỉ dựa vào client-side validation hoặc `Content-Type` headers).
    *   Nếu lưu trữ/xử lý uploads, cân nhắc security scanning cho malware.
*   **Xác thực & Phân quyền (Nếu có):** Nếu thêm authentication, sử dụng methods chuẩn, bảo mật (ví dụ: OAuth 2.0, JWT với appropriate algorithms và expiry). Triển khai proper authorization checks cho accessing resources. (Lưu ý: AI Math Chatbot PRD chỉ định *không có authentication*).
*   **HTTPS:** Đảm bảo tất cả communication qua HTTPS trong production environments.

## 4. Hiệu năng & Tối ưu hóa

*   **Sử dụng API:**
    *   Chú ý đến API call costs và quotas (ví dụ: Gemini).
    *   Sử dụng streaming responses (`generate_content_stream`) khi phù hợp để cải thiện perceived performance.
    *   Cân nhắc `count_tokens` cho estimating costs hoặc validating input sizes.
    *   Khám phá context caching (`client.caches.create`) cho Gemini nếu large contexts thường xuyên được reuse, hiểu cost implications và TTL (Xem `gemini_api_doc.md`).
*   **Database Queries:** Tối ưu hóa database queries. Sử dụng indexing phù hợp. Tránh N+1 query problems. Select chỉ data cần thiết.
*   **Hiệu năng Frontend:**
    *   Tối ưu hóa bundle sizes (code splitting, tree shaking).
    *   Lazy load components hoặc routes khi phù hợp.
    *   Tối ưu hóa images (proper formats, compression, responsive sizes).
    *   Minimize unnecessary re-renders (sử dụng `React.memo`, `useCallback`, `useMemo` một cách thận trọng).
*   **Hiệu năng Backend:** Profile và tối ưu hóa slow backend endpoints hoặc processing steps. Sử dụng asynchronous operations cho I/O-bound tasks.

## 5. Hợp tác & Version Control

*   **Hệ thống Version Control:** **Git** là bắt buộc cho tất cả projects.
*   **Repository:** Sử dụng central Git repository (ví dụ: GitHub, GitLab, Bitbucket).
*   **Chiến lược Branching:**
    *   Sử dụng consistent branching strategy (ví dụ: simplified Gitflow: `main` cho production-ready code, `develop` cho integration, feature branches `feature/your-feature-name`).
    *   Tạo feature branches từ `develop`.
    *   **Không bao giờ commit trực tiếp vào `main` hoặc `develop`.**
*   **Commits:**
    *   Viết clear, concise commit messages theo conventional commit standards (ví dụ: `feat: add file upload button`, `fix: resolve streaming display issue`).
    *   Commit small, logical units of work thường xuyên.
*   **Code Reviews:**
    *   Tất cả code changes *phải* được review qua Pull Requests (PRs) trước khi merge vào `develop` (và sau đó `main`).
    *   Yêu cầu ít nhất một approval (hoặc project-specific number) cho PRs.
    *   Reviewers nên check cho correctness, adherence to standards (project & global), potential bugs, security issues, và clarity.
*   **Code Formatting & Linting:**
    *   Cấu hình và sử dụng automated formatters (ví dụ: Black, Prettier) và linters (ví dụ: Flake8, Ruff, ESLint) trong IDE.
    *   Đảm bảo consistent settings across team (ví dụ: qua configuration files như `pyproject.toml`, `.eslintrc.js`, `prettierrc.js` commit vào repository).
    *   Code phải pass linting checks trước khi merge.

## 6. Tài liệu

*   **README.md:** Mọi project repository *phải* có file `README.md` ở root chứa:
    *   Project title và brief description.
    *   Prerequisites cho setting up development environment.
    *   Step-by-step instructions cho local setup và running project (bao gồm environment variable setup).
    *   Instructions cho running tests.
    *   (Optional) Basic usage guide hoặc key features overview.
    *   (Optional) Deployment instructions.
*   **Code Comments:** Viết clear comments cho complex logic, non-obvious code sections, hoặc public APIs/functions. Tránh comment trên obvious code. Tập trung vào "why," không chỉ "what." Sử dụng standard docstring formats (ví dụ: Google style cho Python, JSDoc/TSDoc cho TypeScript).
*   **API Documentation:** Cho backend APIs, tận dụng frameworks như FastAPI auto-generate interactive documentation (Swagger UI/ReDoc) dựa trên code và type hints. Đảm bảo Pydantic models và endpoint definitions rõ ràng.

## 7. Cấu hình Toàn cầu & Thư viện

*   **UI Frameworks/Libraries:** Ưu tiên established, well-maintained libraries (ví dụ: React, FastAPI). Justify inclusion của new major dependencies.
*   **Styling:** Tailwind CSS là preferred utility-first CSS framework cho consistency, trừ khi project có specific needs justifying another approach.
*   **Icons:** Sử dụng consistent icon set across projects khi feasible (ví dụ: Heroicons, Feather Icons).
*   **Math Rendering:** Cho web projects yêu cầu math display, **KaTeX** là preferred library do performance và rendering quality.
*   **State Management (Frontend):** Mặc dù Zustand được chỉ định cho AI Math Chatbot, projects khác có thể chọn alternatives như Redux Toolkit hoặc Context API dựa trên complexity, nhưng choice nên được documented và justified.
*   **IDE Settings:** Khuyến khích team members tận dụng IDE features cho linting, formatting, và type checking dựa trên project configuration files (`.eslintrc.js`, `pyproject.toml`, `tsconfig.json`, v.v.) để đảm bảo consistency bất kể specific IDE (Cursor AI, Windsurf).

---