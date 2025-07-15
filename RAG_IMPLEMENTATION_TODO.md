# 🚀 RAG Integration TODO List (Simple Version)
## Tích hợp RAG vào hệ thống chatbot hiện tại, cho phép chuyển đổi giữa pipeline thường và pipeline RAG qua cấu hình

---

## 1. PHASE 1: Chuẩn bị & Đánh giá
- [ ] Đọc kỹ các module chính trong backend_RAG:
  - `app/api/v1/router/chat.py`: Xử lý endpoint chat, streaming, tích hợp orchestrator RAG.
  - `app/orchestrator/graph_builder.py`, ...: Xây dựng pipeline RAG.
  - `app/services/`: Các service cho vector DB, ...
  - `app/schemas/`: Định nghĩa schema cho message, chunk, artifact, ...
- [ ] Đánh giá sự khác biệt với backend hiện tại (đặc biệt là flow chat, lưu lịch sử, xác thực user).

---

## 2. PHASE 2: Hướng dẫn tích hợp RAG vào backend chính

### **A. Xác định các module RAG cần “nhúng”**
- orchestrator/graph_builder.py, system_message_generator.py, prompts.py, ...
- services/ (vector db, retrieval, ...)
- schemas/ (chunk_message, artifact, ...)
- utils/ (nếu có)

### **B. Copy các module này vào backend chính**
- Tạo thư mục mới trong backend chính, ví dụ: `app/rag_orchestrator/`, `app/rag_services/`, ...
- Copy các file từ backend_RAG vào đây.
- Đảm bảo không ghi đè file cũ, đổi tên nếu trùng.

### **C. Import và sử dụng orchestrator RAG trong router backend chính**
- Trong router xử lý chat (ví dụ: `routers/chat_router.py`):
  ```python
  from app.rag_orchestrator.graph_builder import GraphBuilder
  from app.config import USE_RAG

  @router.post("/chat/stream")
  async def chat_stream(request: ChatRequest):
      if USE_RAG:
          generator = GraphBuilder()
          # Gọi event_stream hoặc logic RAG như backend_RAG
          ...
      else:
          # Gọi pipeline cũ
          ...
  ```

### **D. Đảm bảo các schema, service, utils được import đúng**
- Nếu có import chéo giữa các file, sửa lại đường dẫn import cho phù hợp với backend chính.

### **E. Thêm các dependency cần thiết vào requirements.txt**
- Thêm các package RAG (chromadb, langchain, ...).

---

## 3. PHASE 3: Thiết kế chuyển đổi pipeline
- [ ] Thêm biến cấu hình (env/config) để chọn pipeline: `USE_RAG=True/False` hoặc tương tự.
- [ ] Trong router xử lý chat, kiểm tra biến cấu hình này:
  - Nếu `USE_RAG=True` → gọi pipeline RAG (orchestrator, graph_builder, ...)
  - Nếu `USE_RAG=False` → gọi pipeline thường (giữ nguyên logic cũ)
- [ ] (Tùy chọn) Cho phép chuyển đổi pipeline qua endpoint hoặc qua file config mà không cần restart server.

---

## 4. PHASE 4: Lưu lịch sử chat & nguồn RAG
- [ ] Khi dùng pipeline RAG, lưu thêm thông tin nguồn (artifact, sources) vào lịch sử chat/message (nếu muốn).
- [ ] Đảm bảo lịch sử chat của pipeline thường không bị ảnh hưởng.
- [ ] (Tùy chọn) Thêm trường `pipeline` vào bảng chat/message để biết message này dùng pipeline nào.

---

## 5. PHASE 5: Cập nhật frontend (nếu cần)
- [ ] (Tùy chọn) Thêm nút/toggle trên frontend để chuyển đổi giữa pipeline thường và RAG (gửi kèm mode lên backend hoặc chỉ dùng cho test).
- [ ] Hiển thị nguồn (sources) khi có artifact trả về từ RAG.

---

## 6. PHASE 6: Testing & Backward Compatibility
- [ ] Test pipeline thường: chat bình thường, không RAG, không ảnh hưởng lịch sử.
- [ ] Test pipeline RAG: chat với RAG, nhận được nguồn, artifact, ...
- [ ] Đảm bảo 100% backward compatibility, không breaking change.

---

## 7. PHASE 7: Documentation & Triển khai
- [ ] Cập nhật README, API docs về chế độ RAG, hướng dẫn chuyển đổi pipeline.
- [ ] Hướng dẫn sử dụng, cấu hình, mở rộng RAG.
- [ ] Cập nhật Dockerfile, requirements.txt nếu cần.

---

## Checklist thành công
- [ ] Có thể chuyển đổi giữa pipeline thường và RAG qua cấu hình.
- [ ] Không breaking change, hệ thống cũ vẫn hoạt động.
- [ ] Có thể mở rộng thêm loại pipeline khác trong tương lai.

---

*Estimated Time: 1-2 ngày làm việc cho bản đơn giản* 