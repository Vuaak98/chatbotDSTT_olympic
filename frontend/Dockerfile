# Dockerfile cho frontend Next.js (AI Math Chatbot)
FROM node:18-alpine

# Tạo thư mục làm việc
WORKDIR /app

# Copy file cấu hình package
COPY package.json package-lock.json* pnpm-lock.yaml* ./

# Cài đặt dependencies (ưu tiên dùng pnpm nếu có, fallback sang npm)
RUN if [ -f pnpm-lock.yaml ]; then npm install -g pnpm && pnpm install; else npm install; fi

# Copy toàn bộ mã nguồn
COPY . .

# Build production
RUN npm run build

# Mở cổng 3000
EXPOSE 3000

# Chạy ứng dụng Next.js ở chế độ production
CMD ["npm", "run", "start"] 