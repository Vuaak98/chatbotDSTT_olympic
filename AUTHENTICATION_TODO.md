# 🔐 Authentication System TODO List (Simple Version)
## Đăng ký/đăng nhập tài khoản bằng Gmail + mật khẩu, lưu lịch sử chat theo user

---

## PHASE 1: Authentication Backend

### Task 1.1: Thêm Auth Dependencies
- [ ] Thêm vào `backend/requirements.txt`:
  ```
  passlib[bcrypt]==1.7.4
  python-jose[cryptography]==3.3.0
  python-multipart==0.0.9
  ```

### Task 1.2: Cập nhật Config
- [ ] Thêm vào `backend/app/config.py`:
  ```python
  SECRET_KEY: str = "your-secret-key-here"
  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
  ```

### Task 1.3: Tạo User Model
- [ ] Thêm vào `models.py` hoặc tạo `auth_models.py`:
  ```python
  class User(Base):
      __tablename__ = "users"
      id = Column(Integer, primary_key=True, index=True)
      email = Column(String, unique=True, index=True, nullable=False)
      hashed_password = Column(String, nullable=False)
      created_at = Column(DateTime, default=datetime.utcnow)
      is_active = Column(Boolean, default=True)
      chats = relationship("Chat", back_populates="user")
  ```

---

## PHASE 2: Auth Schemas

### Task 2.1: Tạo Auth Schemas
- [ ] Tạo file `auth_schemas.py`:
  ```python
  class UserRegister(BaseModel):
      email: str
      password: str

  class UserLogin(BaseModel):
      email: str
      password: str

  class Token(BaseModel):
      access_token: str
      token_type: str

  class UserResponse(BaseModel):
      id: int
      email: str
      is_active: bool
      created_at: datetime
  ```

---

## PHASE 3: Auth Services

### Task 3.1: Tạo Auth Service
- [ ] Tạo file `auth_service.py`:
  ```python
  class AuthService:
      def verify_password(self, plain_password: str, hashed_password: str)
      def get_password_hash(self, password: str)
      def create_access_token(self, data: dict)
      def verify_token(self, token: str)
      def authenticate_user(self, email: str, password: str)
      def register_user(self, email: str, password: str)
  ```

---

## PHASE 4: Auth Routers

### Task 4.1: Tạo Auth Router
- [ ] Tạo file `routers/auth_router.py`:
  ```python
  @router.post("/register/")
  @router.post("/login/")
  @router.get("/me/")
  ```

---

## PHASE 5: Auth CRUD

### Task 5.1: Tạo Auth CRUD
- [ ] Tạo file `crud/auth_crud.py`:
  ```python
  def create_user(db: Session, email: str, hashed_password: str)
  def get_user_by_email(db: Session, email: str)
  def get_user_by_id(db: Session, user_id: int)
  ```

---

## PHASE 6: Frontend Authentication

### Task 6.1: Tạo Auth Components
- [ ] Tạo file `frontend/components/auth/LoginForm.tsx`
- [ ] Tạo file `frontend/components/auth/RegisterForm.tsx`

### Task 6.2: Tạo Auth Context
- [ ] Tạo file `frontend/contexts/AuthContext.tsx`

### Task 6.3: Tạo Auth Hooks
- [ ] Tạo file `frontend/hooks/useAuth.ts`

---

## PHASE 7: Frontend UI Updates

### Task 7.1: Cập nhật Header
- [ ] Thêm login/register buttons cho guest
- [ ] Thêm user info cho authenticated users

### Task 7.2: Cập nhật Chat Interface
- [ ] Chỉ cho phép chat khi đã đăng nhập
- [ ] Lưu lịch sử chat theo user

---

## PHASE 8: Testing

### Task 8.1: Test Authentication Flow
- [ ] Test register với email hợp lệ (gmail)
- [ ] Test login với credentials đúng/sai
- [ ] Test logout và session clear

### Task 8.2: Test Chat Flow
- [ ] Test chat khi đã đăng nhập
- [ ] Test không chat được khi chưa đăng nhập
- [ ] Test lưu lịch sử chat theo user

---

## Lưu ý:
- Chỉ cho phép đăng ký email @gmail.com (nếu muốn).
- Không cần OAuth, không cần xác thực nâng cao.
- Có thể mở rộng thêm user_type, admin, guest, ... sau này nếu cần.

---

*Estimated Time: 1-2 ngày làm việc cho bản đơn giản*