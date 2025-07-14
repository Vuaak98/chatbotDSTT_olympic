# Middleware Xử lý Lỗi & Bảo mật

Thư mục này chứa các thành phần middleware cho xử lý lỗi, giới hạn tốc độ và các tính năng bảo mật khác cho backend Chatbot Toán AI. Các thành phần này được thiết kế để modular, dễ bảo trì và bảo vệ API mạnh mẽ.

## 🛡️ Các thành phần

### Middleware Xử lý Lỗi

`ErrorHandlerMiddleware` cung cấp xử lý lỗi tập trung cho ứng dụng. Nó bắt các ngoại lệ phát sinh trong quá trình xử lý yêu cầu, ghi log phù hợp và trả về phản hồi lỗi chuẩn hóa cho client.

Tính năng chính:
- Xử lý các loại ngoại lệ khác nhau (lỗi validate, HTTP exceptions, lỗi Gemini API, lỗi không mong đợi)
- Cung cấp thông báo lỗi thân thiện với người dùng
- Ghi log thông tin lỗi chi tiết để debug
- Ngăn chặn việc tiết lộ thông tin nhạy cảm trong phản hồi lỗi

### Giới hạn Tốc độ

Middleware `RateLimiter` ngăn chặn việc lạm dụng API bằng cách giới hạn số lượng yêu cầu có thể thực hiện trong một khoảng thời gian. Nó theo dõi yêu cầu theo địa chỉ IP và endpoint, và trả về phản hồi 429 Too Many Requests khi vượt quá giới hạn.

Tính năng chính:
- Giới hạn tốc độ có thể cấu hình cho từng endpoint
- Theo dõi dựa trên IP
- Hỗ trợ header X-Forwarded-For cho client đằng sau proxy

### Xử lý Ngoại lệ

Module `exception_handlers.py` cung cấp FastAPI exception handlers cho các loại ngoại lệ cụ thể:
- `request_validation_exception_handler`: Xử lý lỗi validate từ dữ liệu yêu cầu
- `http_exception_handler`: Xử lý HTTP exceptions
- `gemini_api_exception_handler`: Xử lý lỗi Gemini API

## 🚀 Cách sử dụng

Các thành phần middleware này được đăng ký trong instance ứng dụng FastAPI chính trong `main.py`. Middleware được thực thi theo thứ tự ngược (thêm cuối, thực thi đầu), vì vậy thứ tự đăng ký rất quan trọng.

```python
# Thêm middleware
# Lưu ý: Middleware được thực thi theo thứ tự ngược (thêm cuối, thực thi đầu)

# Thêm middleware giới hạn tốc độ
app.add_middleware(RateLimiter)

# Thêm middleware xử lý lỗi
app.add_middleware(ErrorHandlerMiddleware)
```

Exception handlers được đăng ký bằng phương thức `add_exception_handler` của FastAPI:

```python
# Đăng ký exception handlers
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(google.genai.errors.APIError, gemini_api_exception_handler)
```

## 📚 Thông tin thêm

- Xem [README backend](../../README.md) để biết kiến trúc tổng thể, bảo mật và thực hành tốt.
- Middleware và xử lý ngoại lệ là chìa khóa cho thiết kế API mạnh mẽ, sẵn sàng production.

## 🔮 Định hướng tương lai

- **JWT Authentication Middleware:** Thêm hỗ trợ xác thực và phân quyền người dùng
- **CORS Middleware:** Kiểm soát chi tiết các yêu cầu cross-origin
- **Advanced Logging:** Ghi log có cấu trúc, externalized hoặc distributed logging
- **Request/Response Compression:** Cải thiện hiệu năng cho payload lớn
- **Custom Metrics Middleware:** Theo dõi sử dụng API, độ trễ và tỷ lệ lỗi
- **IP Blacklisting/Whitelisting:** Kiểm soát bảo mật bổ sung
- **Tracing/Correlation IDs:** Cho distributed tracing và debug

---

**Thể hiện kỹ năng backend engineering của bạn:** Lớp middleware này thể hiện thực hành tốt trong xử lý lỗi, bảo mật và thiết kế API modular cho ứng dụng web Python hiện đại.