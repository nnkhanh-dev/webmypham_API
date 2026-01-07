# Hướng dẫn sử dụng API Địa giới Hành chính Việt Nam

## Tải dữ liệu địa giới hành chính VN

API này sử dụng dữ liệu từ [hanhchinhvn](https://github.com/madnh/hanhchinhvn).

### Cách 1: Sử dụng script tự động (Khuyến nghị)

1. **Chạy script để download file JSON:**

```bash
cd webmypham_API
python scripts/download_hanhchinhvn.py
```

Script sẽ:
- Tải file JSON từ GitHub
- Lưu vào thư mục `data/hanhchinhvn_data.json`
- Kiểm tra và báo cáo kết quả

### Cách 2: Download thủ công

1. **Download file JSON:**
   - Truy cập: https://raw.githubusercontent.com/kenzouno1/DiaGioiHanhChinhVN/master/data.json
   - Lưu file vào: `webmypham_API/data/hanhchinhvn_data.json`

2. **Đảm bảo file có cấu trúc đúng:**
   - File JSON phải có key `"data"` ở root level
   - Key `"data"` chứa object với mã tỉnh/thành phố làm key

## Cách hoạt động

1. **Ưu tiên load từ file local:**
   - Service sẽ tìm file `data/hanhchinhvn_data.json` trước
   - Nếu có file local, sử dụng ngay (nhanh hơn)

2. **Fallback to URL:**
   - Nếu không có file local, service sẽ tự động tải từ GitHub
   - Sau khi tải, file sẽ được lưu vào local để dùng lần sau

3. **Cache:**
   - Dữ liệu được cache trong memory sau lần load đầu tiên
   - Không cần load lại mỗi lần request

## API Endpoints

- `GET /api/v1/administrative/provinces` - Lấy danh sách tỉnh/thành phố
- `GET /api/v1/administrative/districts?province_code={code}` - Lấy danh sách quận/huyện
- `GET /api/v1/administrative/wards?province_code={code}&district_code={code}` - Lấy danh sách phường/xã

## Lưu ý

- File JSON khá lớn (~5-10MB), nên commit vào git là không cần thiết
- File đã được thêm vào `.gitignore`
- Nên chạy script download trước khi deploy

