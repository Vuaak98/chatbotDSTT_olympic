# Các Hàm Tiện ích

Thư mục này chứa các hàm tiện ích được sử dụng trong toàn bộ backend Chatbot Toán AI.

## Tiện ích Làm sạch Dữ liệu

Module `sanitizer.py` cung cấp các hàm để làm sạch đầu vào của người dùng nhằm ngăn chặn các cuộc tấn công injection và các lỗ hổng bảo mật khác.

### Các hàm

#### `sanitize_text(text: str) -> str`

Làm sạch đầu vào text để ngăn chặn các cuộc tấn công injection.

- Escape HTML để ngăn chặn XSS
- Chuẩn hóa xuống dòng
- Loại bỏ các ký tự điều khiển

#### `sanitize_filename(filename: str) -> str`

Làm sạch tên file để ngăn chặn các cuộc tấn công path traversal.

- Loại bỏ các thành phần đường dẫn (/, \, :, v.v.)
- Loại bỏ dấu chấm và khoảng trắng ở đầu/cuối
- Đảm bảo tên file không rỗng sau khi làm sạch

#### `sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]`

Làm sạch đệ quy tất cả các giá trị string trong dictionary.

#### `sanitize_list(data: List[Any]) -> List[Any]`

Làm sạch đệ quy tất cả các giá trị string trong list.

#### `validate_mime_type(content_type: str, allowed_types: List[str]) -> bool`

Xác thực rằng MIME type có trong danh sách các loại được phép.

- Chuẩn hóa content type (chữ thường, loại bỏ tham số)
- Kiểm tra xem content type đã chuẩn hóa có trong danh sách được phép không

## Cách sử dụng

Các hàm tiện ích này được sử dụng trong toàn bộ ứng dụng để làm sạch đầu vào của người dùng trước khi xử lý hoặc lưu trữ. Ví dụ:

```python
from ..utils import sanitize_text, sanitize_filename

# Làm sạch đầu vào của người dùng
sanitized_message = sanitize_text(message)

# Làm sạch tên file
sanitized_filename = sanitize_filename(file.filename)
```