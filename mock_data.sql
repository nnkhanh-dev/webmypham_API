-- ============================================
-- MOCK DATA CHO TEST API GIỎI HÀNG VÀ BIẾN THỂ
-- Chạy file này trong MySQL để có dữ liệu test
-- ============================================

-- 1. Tạo Type (Loại thuộc tính)
INSERT INTO types (id, name, created_at, updated_at) VALUES
('a1b2c3d4-1111-4000-8000-000000000001', 'Màu sắc', NOW(), NOW()),
('a1b2c3d4-1111-4000-8000-000000000002', 'Dung tích', NOW(), NOW());

-- 2. Tạo TypeValue (Giá trị cụ thể)
INSERT INTO type_values (id, name, type_id, created_at, updated_at) VALUES
-- Màu sắc
('b2c3d4e5-2222-4000-8000-000000000001', 'Đỏ', 'a1b2c3d4-1111-4000-8000-000000000001', NOW(), NOW()),
('b2c3d4e5-2222-4000-8000-000000000002', 'Hồng', 'a1b2c3d4-1111-4000-8000-000000000001', NOW(), NOW()),
('b2c3d4e5-2222-4000-8000-000000000003', 'Cam', 'a1b2c3d4-1111-4000-8000-000000000001', NOW(), NOW()),
-- Dung tích
('b2c3d4e5-2222-4000-8000-000000000004', '50ml', 'a1b2c3d4-1111-4000-8000-000000000002', NOW(), NOW()),
('b2c3d4e5-2222-4000-8000-000000000005', '100ml', 'a1b2c3d4-1111-4000-8000-000000000002', NOW(), NOW()),
('b2c3d4e5-2222-4000-8000-000000000006', '200ml', 'a1b2c3d4-1111-4000-8000-000000000002', NOW(), NOW());

-- 3. Tạo Brand
INSERT INTO brands (id, name, description, created_at, updated_at) VALUES
('c3d4e5f6-3333-4000-8000-000000000001', 'Laneige', 'Thương hiệu Hàn Quốc', NOW(), NOW()),
('c3d4e5f6-3333-4000-8000-000000000002', 'Innisfree', 'Thương hiệu thiên nhiên', NOW(), NOW());

-- 4. Tạo Category
INSERT INTO categories (id, name, description, created_at, updated_at) VALUES
('d4e5f6a7-4444-4000-8000-000000000001', 'Son môi', 'Các loại son môi', NOW(), NOW()),
('d4e5f6a7-4444-4000-8000-000000000002', 'Dưỡng da', 'Các sản phẩm chăm sóc da', NOW(), NOW());

-- 5. Tạo Product
INSERT INTO products (id, name, description, thumbnail, is_active, brand_id, category_id, created_at, updated_at) VALUES
('e5f6a7b8-5555-4000-8000-000000000001', 'Son Môi Laneige Lip Sleeping Mask', 'Son dưỡng môi ban đêm', '/images/laneige-lip.jpg', 1, 'c3d4e5f6-3333-4000-8000-000000000001', 'd4e5f6a7-4444-4000-8000-000000000001', NOW(), NOW()),
('e5f6a7b8-5555-4000-8000-000000000002', 'Kem Dưỡng Innisfree Green Tea', 'Kem dưỡng ẩm từ trà xanh', '/images/innisfree-cream.jpg', 1, 'c3d4e5f6-3333-4000-8000-000000000002', 'd4e5f6a7-4444-4000-8000-000000000002', NOW(), NOW());

-- 6. Tạo ProductType (Biến thể) - QUAN TRỌNG NHẤT
INSERT INTO product_types (id, product_id, type_value_id, price, discount_price, stock, image_path, volume, origin, skin_type, created_at, updated_at) VALUES
-- Son Laneige - 3 màu
('f6a7b8c9-6666-4000-8000-000000000001', 'e5f6a7b8-5555-4000-8000-000000000001', 'b2c3d4e5-2222-4000-8000-000000000001', 350000, 299000, 30, '/images/laneige-red.jpg', '8g', 'Hàn Quốc', 'Mọi loại da', NOW(), NOW()),
('f6a7b8c9-6666-4000-8000-000000000002', 'e5f6a7b8-5555-4000-8000-000000000001', 'b2c3d4e5-2222-4000-8000-000000000002', 350000, 299000, 25, '/images/laneige-pink.jpg', '8g', 'Hàn Quốc', 'Mọi loại da', NOW(), NOW()),
('f6a7b8c9-6666-4000-8000-000000000003', 'e5f6a7b8-5555-4000-8000-000000000001', 'b2c3d4e5-2222-4000-8000-000000000003', 350000, 299000, 0, '/images/laneige-orange.jpg', '8g', 'Hàn Quốc', 'Mọi loại da', NOW(), NOW()),  -- Hết hàng!

-- Kem Innisfree - 3 dung tích
('f6a7b8c9-6666-4000-8000-000000000004', 'e5f6a7b8-5555-4000-8000-000000000002', 'b2c3d4e5-2222-4000-8000-000000000004', 450000, 399000, 50, '/images/innisfree-50.jpg', '50ml', 'Hàn Quốc', 'Da khô', NOW(), NOW()),
('f6a7b8c9-6666-4000-8000-000000000005', 'e5f6a7b8-5555-4000-8000-000000000002', 'b2c3d4e5-2222-4000-8000-000000000005', 750000, 650000, 20, '/images/innisfree-100.jpg', '100ml', 'Hàn Quốc', 'Da khô', NOW(), NOW()),
('f6a7b8c9-6666-4000-8000-000000000006', 'e5f6a7b8-5555-4000-8000-000000000002', 'b2c3d4e5-2222-4000-8000-000000000006', 1200000, 999000, 10, '/images/innisfree-200.jpg', '200ml', 'Hàn Quốc', 'Da khô', NOW(), NOW());

-- 7. Tạo Role (nếu chưa có)
INSERT IGNORE INTO roles (id, name, created_at, updated_at) VALUES
('a7b8c9d0-7777-4000-8000-000000000001', 'CLIENT', NOW(), NOW());

-- 8. Tạo User test
INSERT INTO users (id, email, password_hash, first_name, last_name, phone_number, created_at, updated_at) VALUES
('b8c9d0e1-8888-4000-8000-000000000001', 'test@example.com', '$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$RdescudvJCsgt3ub+b+dWRWJTmaaJObG', 'Test', 'User', '0901234567', NOW(), NOW());

-- 9. Gán role cho user
INSERT INTO user_roles (user_id, role_id) VALUES
('b8c9d0e1-8888-4000-8000-000000000001', 'a7b8c9d0-7777-4000-8000-000000000001');

-- 10. Tạo Cart cho user
INSERT INTO carts (id, user_id, created_at, updated_at) VALUES
('c9d0e1f2-9999-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000001', NOW(), NOW());

-- 11. Tạo CartItem (sản phẩm trong giỏ)
INSERT INTO cart_items (id, cart_id, product_type_id, quantity, created_at, updated_at) VALUES
('d0e1f2a3-aaaa-4000-8000-000000000001', 'c9d0e1f2-9999-4000-8000-000000000001', 'f6a7b8c9-6666-4000-8000-000000000001', 2, NOW(), NOW()),      -- 2 son màu đỏ
('d0e1f2a3-aaaa-4000-8000-000000000002', 'c9d0e1f2-9999-4000-8000-000000000001', 'f6a7b8c9-6666-4000-8000-000000000005', 1, NOW(), NOW());    -- 1 kem 100ml


-- ============================================
-- CHEAT SHEET - Copy ID để test:
-- ============================================
-- Product Son:     e5f6a7b8-5555-4000-8000-000000000001
-- Product Kem:     e5f6a7b8-5555-4000-8000-000000000002
-- Variant Son Đỏ:  f6a7b8c9-6666-4000-8000-000000000001
-- Variant Son Hồng:f6a7b8c9-6666-4000-8000-000000000002
-- Variant Son Cam: f6a7b8c9-6666-4000-8000-000000000003 (hết hàng)
-- Cart:            c9d0e1f2-9999-4000-8000-000000000001
-- CartItem 1:      d0e1f2a3-aaaa-4000-8000-000000000001
-- CartItem 2:      d0e1f2a3-aaaa-4000-8000-000000000002
-- User:            b8c9d0e1-8888-4000-8000-000000000001

-- ============================================
-- TEST APIs:
-- 
-- 1. GET /api/v1/products/e5f6a7b8-5555-4000-8000-000000000001/variants
--    → Xem biến thể son (3 màu, 1 hết hàng)
--
-- 2. PUT /api/v1/carts/c9d0e1f2-9999-4000-8000-000000000001/items/d0e1f2a3-aaaa-4000-8000-000000000001
--    Body: {"product_type_id": "f6a7b8c9-6666-4000-8000-000000000002"}
--    → Đổi từ son đỏ sang son hồng
-- ============================================
