# 🚀 RAG Integration TODO List (Chi tiết, tối ưu, từng bước kiểm thử)

## Mục tiêu
- Tích hợp RAG vào hệ thống chatbot hiện tại, cho phép chuyển đổi linh hoạt giữa pipeline thường (Gemini API) và pipeline RAG qua biến cấu hình.
- Đảm bảo tách biệt, dễ bảo trì, dễ rollback, dễ mở rộng, dễ kiểm thử từng phần.

---

## 1. CHUẨN BỊ & PHÂN TÍCH (**ĐÃ HOÀN THÀNH**)
- [x] Phân tích kiến trúc hiện tại, xác định rõ vị trí gọi Gemini API và luồng xử lý chat.
- [x] Đọc kỹ các module chính: routers, services, models, config.
- [x] Kiểm tra các điểm cần thay đổi/tích hợp để tránh ảnh hưởng pipeline cũ.
- [x] Xác định điểm tích hợp tối ưu là tầng services để điều phối pipeline.

> **Ghi chú:** Đã hoàn thành toàn bộ bước chuẩn bị & phân tích. Sẵn sàng chuyển sang bước 2.

---

## 2. TẠO THƯ MỤC RAG TÁCH BIỆT
- [x] Tạo thư mục `app/rag/` trong backend.
- [x] Copy toàn bộ orchestrator, tools, factories, schemas, config.yaml, ... từ project RAG mẫu vào đây.
- [x] Đảm bảo không ghi đè file cũ, đổi tên nếu trùng.
- [x] Tích hợp các package RAG vào chung file `requirements.txt` (không tách riêng `requirements-rag.txt`).
- [x] Test import các module RAG mới, fix lỗi import nếu có.

---

## 3. ÁP DỤNG STRATEGY PATTERN CHO PIPELINE
- [ ] Tạo abstract class `PipelineStrategy` (dùng abc.ABC) trong `services.py` hoặc `strategy.py`.
- [ ] Tạo các class con: `GeminiPipeline`, `RagPipeline` (và có thể thêm pipeline khác sau này).
- [ ] Hàm điều phối chỉ cần khởi tạo đúng pipeline và gọi `generate_response`.
- [ ] Test từng pipeline độc lập (Gemini/RAG), fix lỗi nếu có.

---

## 4. ĐIỀU PHỐI PIPELINE QUA BIẾN MÔI TRƯỜNG
- [ ] Thêm biến `USE_RAG` vào `.env` và đọc trong `config.py`.
- [ ] Đảm bảo có thể chuyển đổi pipeline chỉ bằng cách đổi biến môi trường và restart server.
- [ ] Test chuyển đổi pipeline, đảm bảo không breaking change.

---

## 5. CHUẨN HÓA RESPONSE
- [ ] Định nghĩa schema response chung (Pydantic) cho cả hai pipeline (ví dụ: `ChatResponse`, `Artifact`).
- [ ] Đảm bảo cả hai pipeline trả về cùng format, pipeline direct trả về artifacts rỗng.
- [ ] Test response ở cả backend và frontend, fix lỗi hiển thị nếu có.

---

## 6. API NẠP TÀI LIỆU VÀO VECTOR DB (RAG)
- [ ] Tạo endpoint upload tài liệu riêng (ví dụ: `/rag/documents/upload`).
- [ ] Bảo vệ endpoint bằng xác thực, phân quyền (chỉ admin hoặc user đặc biệt).
- [ ] Xử lý nặng (cắt nhỏ, vector hóa) bằng background task (FastAPI BackgroundTasks).
- [ ] Test upload tài liệu, kiểm tra dữ liệu vào vector DB, fix lỗi nếu có.

---

## 7. TÍCH HỢP VECTOR DB & NẠP TÀI LIỆU
- [ ] Sử dụng factory pattern để khởi tạo vector store (Qdrant, ChromaDB, ...).
- [ ] Xây dựng script hoặc API nhỏ để nạp tài liệu vào vector DB (có thể dùng lại logic từ history-chatbot).
- [ ] Test truy vấn tài liệu, đảm bảo pipeline RAG hoạt động đúng.

---

## 8. CẬP NHẬT REQUIREMENTS & DOCKERFILE
- [ ] Thêm các package cần thiết cho RAG vào `requirements-rag.txt`.
- [ ] Đảm bảo `requirements.txt` chính import file này.
- [ ] Cập nhật Dockerfile nếu cần.
- [ ] Test build docker, fix lỗi dependencies nếu có.

---

## 9. TEST & TÀI LIỆU HÓA
- [ ] Test từng pipeline (bật/tắt RAG), test upload tài liệu, test response frontend.
- [ ] Viết tài liệu hướng dẫn cách bật/tắt, nạp tài liệu, mở rộng pipeline, rollback.
- [ ] Checklist test từng phần, ghi chú lỗi và cách fix nếu gặp.

---

## 10. NÂNG CẤP KIỂM CHỨNG VÀ QUẢN LÝ PIPELINE (RECOMMENDED UPGRADE TODO)
- [ ] Trả về context/tài liệu đã sử dụng (artifacts) trong response API để frontend hiển thị nguồn tham khảo, giúp kiểm chứng RAG hoạt động đúng.
- [ ] Log rõ ràng context lấy từ vector store (Qdrant) và pipeline đang sử dụng (Gemini hay RAG GPT) trong backend để dễ debug, kiểm thử.
- [ ] Thêm chức năng hiển thị context/tài liệu đã dùng trên giao diện chat (frontend), giúp người dùng biết câu trả lời dựa vào đâu.
- [ ] Test chuyển đổi pipeline Gemini/RAG GPT end-to-end từ frontend đến backend, đảm bảo phân biệt rõ ràng và không bị lẫn lộn.
- [ ] Viết tài liệu hướng dẫn kiểm thử, xác minh RAG hoạt động đúng (so sánh câu trả lời khi có/không có context).

---

## Checklist thành công
- [ ] Có thể chuyển đổi giữa pipeline thường và RAG qua biến cấu hình.
- [ ] Không breaking change, hệ thống cũ vẫn hoạt động.
- [ ] Tách biệt module RAG, dễ bảo trì, dễ rollback.
- [ ] Có thể mở rộng thêm pipeline khác trong tương lai.
- [ ] Có tài liệu hướng dẫn rõ ràng.
- [ ] Test từng phần đều pass, dễ xác định lỗi khi tích hợp.

---

*Estimated Time: 1-2 tuần cho sinh viên năm 3 với bản tối ưu, từng bước kiểm thử, dễ bảo trì* 

---

# LỘ TRÌNH TÍCH HỢP RAG AN TOÀN VÀ HIỆU QUẢ (RECOMMENDED STRATEGY)

## Giai đoạn 1: Giữ nguyên OpenAI/Azure để kiểm thử 🎯
**Mục tiêu:** Đảm bảo pipeline RAG (orchestrator, retriever, prompt, schema, ...) hoạt động ổn định trong dự án của bạn.

**Lợi ích:** Nếu có lỗi, bạn biết chắc là do tích hợp (import, config, data flow), không phải do sự khác biệt API LLM.

**Hành động:**
- Giữ nguyên các hàm factory, config, key OpenAI/Azure như dự án mẫu.
- Test toàn bộ pipeline RAG với OpenAI/Azure.
- Sửa lỗi import, config, schema cho đến khi mọi thứ chạy ổn.

---

## Giai đoạn 2: Chuyển đổi sang Gemini khi đã ổn định 🔄
**Mục tiêu:** Đồng bộ hóa backend về một nhà cung cấp LLM duy nhất (Gemini).

**Lợi ích:**
- Đảm bảo hệ thống nhất quán, dễ bảo trì, dễ quản lý chi phí.
- Việc chuyển đổi lúc này chỉ tập trung vào factory, API call, không ảnh hưởng logic RAG.

**Hành động:**
- Viết lại factory/hàm khởi tạo Gemini model.
- Sửa các lệnh gọi model trong factories, orchestrator để dùng Gemini.
- Test lại pipeline RAG với Gemini.

---

## Giai đoạn 3: Dọn dẹp và hoàn thiện ✨
**Mục tiêu:** Loại bỏ code thừa, chuẩn hóa tài liệu, đảm bảo codebase sạch sẽ.

**Lợi ích:**
- Dễ bảo trì, dễ mở rộng, dễ cho người mới tham gia.

**Hành động:**
- Xóa các phần chỉ dùng cho OpenAI/Azure nếu không còn cần thiết.
- Chuẩn hóa lại config, doc, hướng dẫn sử dụng.
- Viết tài liệu hướng dẫn tích hợp, chuyển đổi, mở rộng.

---

**Lưu ý:**
- Lộ trình này giúp kiểm soát rủi ro, dễ debug, dễ bảo trì, và dễ mở rộng về sau.
- Khi đã ổn định với OpenAI/Azure, việc chuyển sang Gemini sẽ rất nhẹ nhàng. 