# WebMyPham (FastAPI)

Lightweight FastAPI backend scaffold for the WebMyPham project.

Quick start

1. Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
python -m pip install -r requirements.txt
```

2. Create a `.env` file in the project root with at least `DATABASE_URL`:

```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/webmypham
```

3. Run alembic create Database

```bash
alembic upgrade head
```

4. Start the dev server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API

- Main voucher endpoints live at `/vouchers` and return a standardized `BaseResponse` structure.

Notes

- Keep `.env` out of version control. Use `.gitignore` provided in the repo.
- If you need, I can add a `.env.example`, switch pagination to page-based params, or generate initial Alembic migrations.

5. Setup ngrok for dev:

   Install ngrok from https://ngrok.com/download
   Giải nén file zip và chạy .exe trong folder vừa giải nén.

```bash
ngrok http 8000
```

# GIẢI THÍCH CẤU TRÚC THƯ MỤC

## 1. Cấu trúc thư mục chính

- **app/core/**: Các cài đặt lõi (configuration, database, bảo mật, middleware, exception handling, ...). Đây là nơi cấu hình mọi thứ chung cho dự án.
- **app/db/**: Chứa migrations (tạo, thay đổi cấu trúc database bằng Alembic).
- **app/dependencies/**: Định nghĩa các dependency sử dụng với FastAPI's Depends như xác thực, phân trang, permission,... (xem phần dưới).
- **app/models/**: Định nghĩa ORM models dùng SQLAlchemy (các bảng trong DB).
- **app/repositories/**: Định nghĩa các repository để thao tác CRUD với DB (thường là các lớp kế thừa BaseRepository).
- **app/routers/**: Các endpoint API (routers) chia theo version hoặc domain cho clean architecture.
- **app/schemas/**: Định nghĩa các Pydantic schema để validate dữ liệu request/response (chia folder request/response).
- **app/services/**: Xử lý nghiệp vụ, thao tác logic chính giữa controller và repository.

## 2. Chi tiết các dependency (`app/dependencies/`)

- **auth.py**

  - `get_current_user(request: Request)`: Lấy user hiện tại từ request state (được set bởi AuthMiddleware). Ném lỗi HTTP 401 nếu chưa xác thực.

- **database.py**

  - `get_db()`: Generator tạo ra một SQLAlchemy session (`SessionLocal`) mỗi request, tự động đóng session sau khi request hoàn thành.

- **pagination.py**

  - `get_pagination(...)`: Dependency nhận query params như skip, limit, sort, filter,... và trả về dict để dùng cho truy vấn phân trang, lọc trong repository/service.

- **permission.py**
  - `require_roles(*roles)`: Dependency kiểm tra user hiện tại có đủ vai trò (role) được truyền chưa, nếu không đủ thì raise lỗi 403. Dùng để bảo vệ route chỉ cho phép các role cụ thể truy cập.

## 3. Middleware (`app/core/middleware.py`)

- **AuthMiddleware**

  - Được chạy ở tầng middleware để bắt mọi HTTP request.
  - Lấy JWT access token từ header Authorization → giải mã với `decode_access_token`.
  - Nếu hợp lệ, lấy thông tin user từ DB, nạp roles của user và attach user vào `request.state.user` (ở dạng detached object).
  - Cho phép các dependency/route tải được user từ request mà không query lại nhiều lần.

- **TraceIdMiddleware**
  - Đính kèm trace ID cho mỗi request (từ header `X-Trace-Id` hoặc tự sinh UUID mới).
  - Ghi log trace-id, API path, process time (tracking/monitor/debug).
  - Trả trace ID về client qua response header (`X-Trace-Id`).

---

### Tổng kết

- **dependencies** đóng vai trò nhỏ gọn, có thể inject vào route/service để dùng lại các logic chung như xác thực/phân trang/quyền hạn.
- **middleware** xử lý xuyên suốt mọi request vào app (auth, logging, trace...).
- Cấu trúc project này phù hợp cho API chuyên nghiệp, dễ mở rộng, bảo trì theo chiều sâu hoặc microservice.
