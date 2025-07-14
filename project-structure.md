# Cấu trúc dự án Chatbot Toán AI

Tài liệu này mô tả cấu trúc dự án Chatbot Toán AI – một ứng dụng full-stack chất lượng portfolio, trình diễn kỹ năng AI và hỗ trợ toán học qua giao diện chat hiện đại.

## Tổng quan dự án

Dự án gồm 2 thành phần chính:
1. **Backend**: API server Python (FastAPI), tích hợp Google Gemini LLM
2. **Frontend**: Web app React (Next.js), UI responsive, dễ truy cập

## Sơ đồ thư mục
AI_MATH_CHATBOT/
├── .gitignore # Quy tắc ignore Git
├── LICENSE # Giấy phép MIT
├── README.md # Tài liệu dự án
├── project-structure.md # Tài liệu cấu trúc dự án
├── aichatbot.db # CSDL SQLite
├── docker-compose.yml # Cấu hình Docker Compose
├── docs/ # Tài liệu, quy tắc, tham khảo
│ ├── gemini_api_doc.md
│ ├── AI_ Math_Chatbot_Development_Roadmap.md
│ ├── AI-MATH-CHATBOT-PRD.md
│ ├── Global_Rules.md
│ └── Project_Rules.md
├── assets/ # Ảnh demo, screenshot
│ ├── demo.png
│ ├── file_upload_demo.png
│ ├── Initial_page_dark_mode.png
│ └── Initial_page_light_mode.png
├── backend/ # Backend
│ ├── .gitignore
│ ├── Dockerfile
│ ├── README.md
│ ├── alembic.ini
│ ├── aichatbot.db
│ ├── db_manager.py
│ ├── migrate.py
│ ├── requirements.txt
│ ├── .env.example # Mẫu biến môi trường
│ └── app/ # Code chính
│ ├── init.py
│ ├── cleanup_tasks.py
│ ├── config.py
│ ├── database.py
│ ├── main.py # Entry point
│ ├── models.py
│ ├── schemas.py
│ ├── seed_db.py
│ ├── services.py
│ ├── tasks.py
│ ├── crud/ # CRUD DB
│ │ ├── init.py
│ │ ├── chat_crud.py
│ │ └── file_crud.py
│ ├── middleware/ # Middleware
│ │ ├── init.py
│ │ ├── error_handler.py
│ │ ├── exception_handlers.py
│ │ ├── error_utils.py
│ │ ├── rate_limiter.py
│ │ └── README.md
│ ├── routers/ # API route
│ │ ├── chat_router.py
│ │ ├── file_router.py
│ │ ├── message_router.py
│ │ ├── streaming_router.py
│ │ └── README_FILE_UPLOAD.md
│ ├── utils/ # Tiện ích
│ │ ├── init.py
│ │ ├── sanitizer.py
│ │ └── README.md
│ ├── tests/ # (Chưa triển khai) Test
│ └── migrations/ # Migration DB
│ ├── env.py
│ ├── script.py.mako
│ ├── README
│ └── versions/
├── frontend/ # Frontend
├── .gitignore
├── Dockerfile
├── README.md
├── package.json
├── package-lock.json
├── pnpm-lock.yaml
├── next.config.mjs
├── next-env.d.ts
├── postcss.config.mjs
├── tailwind.config.ts
├── tsconfig.json
├── .env.local # Biến môi trường frontend
├── .env.example # Mẫu biến môi trường
├── app/ # Next.js app
│ ├── globals.css
│ ├── layout.tsx
│ └── page.tsx
├── components/ # React component
│ ├── chat-input.tsx
│ ├── chat-message.tsx
│ ├── markdown-renderer.tsx
│ ├── mode-toggle.tsx
│ ├── sidebar.tsx
│ ├── theme-provider.tsx
│ └── ui/ # UI subcomponents
├── hooks/ # Custom hook
│ ├── use-toast.ts
│ ├── use-media-query.ts
│ └── use-mobile.tsx
├── lib/ # API, store, utils
│ ├── api-config.ts
│ ├── api-service.ts
│ ├── store.ts
│ ├── types.ts
│ └── utils.ts
├── public/ # Ảnh tĩnh
│ ├── placeholder.jpg
│ ├── placeholder.svg
│ ├── placeholder-user.jpg
│ ├── placeholder-logo.svg
│ └── placeholder-logo.png
├── styles/ # CSS
└── globals.css
# Cấu trúc dự án Chatbot Toán AI

Tài liệu này mô tả cấu trúc dự án Chatbot Toán AI – một ứng dụng full-stack chất lượng portfolio, trình diễn kỹ năng AI và hỗ trợ toán học qua giao diện chat hiện đại.

## Tổng quan dự án

Dự án gồm 2 thành phần chính:
1. **Backend**: API server Python (FastAPI), tích hợp Google Gemini LLM
2. **Frontend**: Web app React (Next.js), UI responsive, dễ truy cập

## Sơ đồ thư mục
