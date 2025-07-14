# Tài liệu API Tải File

## Tổng quan

API endpoint Tải File cho phép Chatbot Toán AI nhận và xử lý file tải lên từ người dùng. Hỗ trợ các file bao gồm hình ảnh, PDF, file text và tài liệu Word, có thể được sử dụng như một phần của cuộc trò chuyện hoặc câu hỏi cho trợ lý AI. **Bạn có thể tải lên tối đa 5 file cùng lúc mỗi lần yêu cầu.**

## Endpoint

```
POST /upload-file
```

## Định dạng Yêu cầu

Yêu cầu phải là `multipart/form-data` với một hoặc nhiều file đính kèm (tối đa 5 file mỗi lần yêu cầu).

### Tham số

- `file`: File cần tải lên (bắt buộc; hỗ trợ nhiều file bằng cách gửi tối đa 5 trường `file`)

### Các loại file được hỗ trợ

- **PDF:** `application/pdf`
- **Hình ảnh:**
  - `image/jpeg`
  - `image/png`
  - `image/webp`
  - `image/heic`
  - `image/heif`
- **Text:** `text/plain`
- **Word:** `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (.docx)

### Giới hạn kích thước

- **Xử lý trực tiếp:** File < ~20MB được xử lý trong bộ nhớ và gửi trực tiếp đến Gemini
- **File lớn:** File lên đến 2GB được tải lên qua Gemini Files API (TTL 48 giờ)
- **Giới hạn server:** Kích thước file tối đa là 2GB, nhưng có thể cấu hình bằng biến môi trường `MAX_FILE_SIZE`
- **Giới hạn số lượng file:** Tối đa 5 file mỗi lần yêu cầu

## Định dạng Phản hồi

### Phản hồi Thành công (200 OK)

```json
[
  {
    "file_id": "unique_file_id_1",
    "filename": "uploaded_filename1.pdf",
    "mime_type": "application/pdf",
    "size": 123456,
    "status": "uploaded"
  },
  {
    "file_id": "unique_file_id_2",
    "filename": "uploaded_filename2.png",
    "mime_type": "image/png",
    "size": 654321,
    "status": "uploaded"
  }
  // ... tối đa 5 file
]
```

### Phản hồi Lỗi

- **415 Unsupported Media Type:** Loại file không được hỗ trợ
- **413 Request Entity Too Large:** File vượt quá kích thước tối đa cho phép
- **400 Bad Request:** Không có file được cung cấp, yêu cầu không hợp lệ, hoặc tải lên hơn 5 file
- **500 Internal Server Error:** Lỗi xử lý phía server

## Ví dụ Sử dụng

### cURL

```bash
curl -X POST \
  -F "file=@example1.pdf" \
  -F "file=@example2.png" \
  http://localhost:8000/upload-file
```

### JavaScript (Frontend)

```javascript
async function uploadFiles(files) {
  const formData = new FormData();
  Array.from(files).slice(0, 5).forEach(file => formData.append('file', file));

  try {
    const response = await fetch('http://localhost:8000/upload-file', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error uploading files:', error);
    throw error;
  }
}
```

## Cấu hình

Chức năng tải file có thể được cấu hình bằng các biến môi trường:

```
UPLOAD_DIR=/path/to/upload/directory
MAX_FILE_SIZE=2097152000  # 2GB tính bằng bytes
ALLOWED_FILE_TYPES=application/pdf,image/jpeg,image/png,image/webp,image/heic,image/heif,text/plain,application/vnd.openxmlformats-officedocument.wordprocessingml.document
```

## Bảo mật & Xác thực

- **Xác thực MIME type:** Chỉ chấp nhận các loại file được phép
- **Làm sạch tên file:** Ngăn chặn path traversal và tên file không an toàn
- **Xác thực kích thước:** File vượt quá giới hạn kích thước cấu hình sẽ bị từ chối
- **Xác thực số lượng file:** Yêu cầu với hơn 5 file sẽ bị từ chối
- **Lưu trữ tạm thời:** File được lưu trữ tạm thời và xóa sau khi xử lý hoặc hết hạn
- **Không lưu trữ lâu dài:** File không được lưu trữ dài hạn ngoài TTL 48 giờ của Gemini

## Ghi chú

- File tải lên được xử lý và, nếu cần thiết, gửi đến Gemini API để phân tích thêm
- Để có kết quả tốt nhất, đảm bảo file rõ ràng, dễ đọc và trong giới hạn kích thước và loại được hỗ trợ
- Phản hồi bao gồm ID file duy nhất để theo dõi và tham chiếu tải lên trong các tin nhắn chat tiếp theo 