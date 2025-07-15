// frontend/lib/auth-api.ts

// Định nghĩa các kiểu dữ liệu cho request và response để code an toàn hơn
import { LoginCredentials, RegisterCredentials, User, Token } from "./types"; // Giả sử bạn có file types.ts

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Xử lý các lỗi từ API và trả về một đối tượng Error chuẩn hóa.
 * @param response - Đối tượng Response từ fetch
 * @returns Promise<Error>
 */
async function handleApiError(response: Response): Promise<Error> {
  let errorMessage = `Lỗi máy chủ: ${response.status} ${response.statusText}`;
  try {
    const errorData = await response.json();
    // Ưu tiên thông báo lỗi chi tiết từ backend
    errorMessage = errorData.detail || JSON.stringify(errorData);
  } catch (e) {
    // Bỏ qua nếu không thể parse JSON
  }
  return new Error(errorMessage);
}

/**
 * Gửi yêu cầu đăng ký đến backend.
 * @param credentials - Email và mật khẩu của người dùng.
 * @returns Thông tin người dùng đã được tạo.
 */
export async function register(credentials: RegisterCredentials): Promise<User> {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    throw await handleApiError(response);
  }

  return response.json();
}

/**
 * Gửi yêu cầu đăng nhập đến backend.
 * @param credentials - Email và mật khẩu của người dùng.
 * @returns Access token và token type.
 */
export async function login(credentials: LoginCredentials): Promise<Token> {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: credentials.email,
      password: credentials.password,
    }),
  });

  if (!response.ok) {
    throw await handleApiError(response);
  }

  return response.json();
}

/**
 * Lấy thông tin người dùng hiện tại từ backend bằng token.
 * @param token - JWT token của người dùng.
 * @returns Thông tin chi tiết của người dùng.
 */
export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch(`${API_URL}/auth/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw await handleApiError(response);
  }

  return response.json();
} 