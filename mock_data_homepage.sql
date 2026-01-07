-- ============================================
-- THÊM DỮ LIỆU MỚI CHO HOMEPAGE APIs
-- Chạy file này SAU KHI đã có dữ liệu ban đầu
-- ============================================

-- 1. Thêm Users nếu chưa có
INSERT IGNORE INTO users (id, email, password_hash, first_name, last_name, phone_number, created_at, updated_at) VALUES
('b8c9d0e1-8888-4000-8000-000000000002', 'user2@example.com', '$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$hash2', 'Nguyễn', 'Văn A', '0901234568', NOW(), NOW()),
('b8c9d0e1-8888-4000-8000-000000000003', 'user3@example.com', '$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$hash3', 'Trần', 'Thị B', '0901234569', NOW(), NOW()),
('b8c9d0e1-8888-4000-8000-000000000004', 'user4@example.com', '$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$hash4', 'Lê', 'Văn C', '0901234570', NOW(), NOW());

-- 2. Thêm Products mới
INSERT IGNORE INTO products (id, name, description, thumbnail, is_active, brand_id, category_id, created_at, updated_at) VALUES
('e5f6a7b8-5555-4000-8000-000000000003', 'Serum Vitamin C Laneige', 'Serum sáng da với vitamin C', '/images/laneige-serum.jpg', 1, 'c3d4e5f6-3333-4000-8000-000000000001', 'd4e5f6a7-4444-4000-8000-000000000002', DATE_SUB(NOW(), INTERVAL 5 DAY), NOW()),
('e5f6a7b8-5555-4000-8000-000000000004', 'Tẩy Trang Innisfree Apple', 'Nước tẩy trang từ táo xanh', '/images/innisfree-cleanser.jpg', 1, 'c3d4e5f6-3333-4000-8000-000000000002', 'd4e5f6a7-4444-4000-8000-000000000002', DATE_SUB(NOW(), INTERVAL 3 DAY), NOW()),
('e5f6a7b8-5555-4000-8000-000000000005', 'Mặt Nạ Innisfree Volcanic', 'Mặt nạ đất sét núi lửa', '/images/innisfree-mask.jpg', 1, 'c3d4e5f6-3333-4000-8000-000000000002', 'd4e5f6a7-4444-4000-8000-000000000002', DATE_SUB(NOW(), INTERVAL 1 DAY), NOW()),
('e5f6a7b8-5555-4000-8000-000000000006', 'Son Dưỡng Laneige Glowy', 'Son dưỡng bóng tự nhiên', '/images/laneige-glowy.jpg', 1, 'c3d4e5f6-3333-4000-8000-000000000001', 'd4e5f6a7-4444-4000-8000-000000000001', NOW(), NOW());

-- 3. Thêm ProductTypes cho sản phẩm mới
INSERT IGNORE INTO product_types (id, product_id, type_value_id, price, discount_price, stock, image_path, volume, origin, skin_type, created_at, updated_at) VALUES
('f6a7b8c9-6666-4000-8000-000000000007', 'e5f6a7b8-5555-4000-8000-000000000003', NULL, 890000, 750000, 40, '/images/laneige-serum.jpg', '30ml', 'Hàn Quốc', 'Mọi loại da', NOW(), NOW()),
('f6a7b8c9-6666-4000-8000-000000000008', 'e5f6a7b8-5555-4000-8000-000000000004', NULL, 350000, 299000, 100, '/images/innisfree-cleanser.jpg', '200ml', 'Hàn Quốc', 'Mọi loại da', NOW(), NOW()),
('f6a7b8c9-6666-4000-8000-000000000009', 'e5f6a7b8-5555-4000-8000-000000000005', NULL, 150000, 120000, 200, '/images/innisfree-mask.jpg', '85g', 'Hàn Quốc', 'Da dầu', NOW(), NOW()),
('f6a7b8c9-6666-4000-8000-000000000010', 'e5f6a7b8-5555-4000-8000-000000000006', 'b2c3d4e5-2222-4000-8000-000000000001', 280000, 230000, 60, '/images/laneige-glowy-red.jpg', '10g', 'Hàn Quốc', 'Mọi loại da', NOW(), NOW()),
('f6a7b8c9-6666-4000-8000-000000000011', 'e5f6a7b8-5555-4000-8000-000000000006', 'b2c3d4e5-2222-4000-8000-000000000002', 280000, 230000, 45, '/images/laneige-glowy-pink.jpg', '10g', 'Hàn Quốc', 'Mọi loại da', NOW(), NOW());

-- ============================================
-- 4. ORDERS (CHO BEST-SELLING)
-- ============================================
INSERT INTO orders (id, user_id, status, total_amount, discount_amount, final_amount, created_at, updated_at) VALUES
('g1h2i3j4-dddd-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000001', 'completed', 600000, 0, 600000, NOW(), NOW()),
('g1h2i3j4-dddd-4000-8000-000000000002', 'b8c9d0e1-8888-4000-8000-000000000002', 'completed', 900000, 0, 900000, NOW(), NOW()),
('g1h2i3j4-dddd-4000-8000-000000000003', 'b8c9d0e1-8888-4000-8000-000000000003', 'delivered', 650000, 0, 650000, NOW(), NOW()),
('g1h2i3j4-dddd-4000-8000-000000000004', 'b8c9d0e1-8888-4000-8000-000000000004', 'completed', 1040000, 0, 1040000, NOW(), NOW()),
('g1h2i3j4-dddd-4000-8000-000000000005', 'b8c9d0e1-8888-4000-8000-000000000001', 'completed', 300000, 0, 300000, NOW(), NOW());

-- 5. ORDER DETAILS (TÍNH SỐ LƯỢNG BÁN)
INSERT INTO order_details (id, order_id, product_type_id, price, number, created_at, updated_at) VALUES
-- Mặt nạ: 5 + 3 + 4 + 3 = 15 cái (bán chạy nhất)
('h2i3j4k5-eeee-4000-8000-000000000001', 'g1h2i3j4-dddd-4000-8000-000000000001', 'f6a7b8c9-6666-4000-8000-000000000009', 120000, 5, NOW(), NOW()),
('h2i3j4k5-eeee-4000-8000-000000000002', 'g1h2i3j4-dddd-4000-8000-000000000002', 'f6a7b8c9-6666-4000-8000-000000000009', 120000, 3, NOW(), NOW()),
('h2i3j4k5-eeee-4000-8000-000000000006', 'g1h2i3j4-dddd-4000-8000-000000000004', 'f6a7b8c9-6666-4000-8000-000000000009', 120000, 4, NOW(), NOW()),
('h2i3j4k5-eeee-4000-8000-000000000008', 'g1h2i3j4-dddd-4000-8000-000000000005', 'f6a7b8c9-6666-4000-8000-000000000009', 120000, 3, NOW(), NOW()),
-- Kem 50ml: 2 cái
('h2i3j4k5-eeee-4000-8000-000000000003', 'g1h2i3j4-dddd-4000-8000-000000000002', 'f6a7b8c9-6666-4000-8000-000000000004', 399000, 2, NOW(), NOW()),
-- Son Đỏ: 1 cái
('h2i3j4k5-eeee-4000-8000-000000000004', 'g1h2i3j4-dddd-4000-8000-000000000003', 'f6a7b8c9-6666-4000-8000-000000000001', 299000, 1, NOW(), NOW()),
-- Tẩy trang: 2 cái
('h2i3j4k5-eeee-4000-8000-000000000005', 'g1h2i3j4-dddd-4000-8000-000000000003', 'f6a7b8c9-6666-4000-8000-000000000008', 299000, 2, NOW(), NOW()),
-- Serum: 1 cái
('h2i3j4k5-eeee-4000-8000-000000000007', 'g1h2i3j4-dddd-4000-8000-000000000004', 'f6a7b8c9-6666-4000-8000-000000000007', 750000, 1, NOW(), NOW());

-- ============================================
-- 6. REVIEWS (CHO TOP-RATED)
-- ============================================
INSERT INTO reviews (id, product_id, user_id, rating, comment, created_at, updated_at) VALUES
-- Mặt nạ: avg = 5.0 ⭐ (cao nhất)
('e1f2a3b4-bbbb-4000-8000-000000000001', 'e5f6a7b8-5555-4000-8000-000000000005', 'b8c9d0e1-8888-4000-8000-000000000001', 5, 'Mặt nạ tuyệt vời!', NOW(), NOW()),
('e1f2a3b4-bbbb-4000-8000-000000000002', 'e5f6a7b8-5555-4000-8000-000000000005', 'b8c9d0e1-8888-4000-8000-000000000002', 5, 'Da mịn hẳn sau khi dùng', NOW(), NOW()),
('e1f2a3b4-bbbb-4000-8000-000000000003', 'e5f6a7b8-5555-4000-8000-000000000005', 'b8c9d0e1-8888-4000-8000-000000000003', 5, 'Kiểm soát dầu rất tốt', NOW(), NOW()),
-- Son Laneige: avg = 4.75 ⭐
('e1f2a3b4-bbbb-4000-8000-000000000004', 'e5f6a7b8-5555-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000001', 5, 'Son rất đẹp!', NOW(), NOW()),
('e1f2a3b4-bbbb-4000-8000-000000000005', 'e5f6a7b8-5555-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000002', 5, 'Dưỡng môi mềm mịn', NOW(), NOW()),
('e1f2a3b4-bbbb-4000-8000-000000000006', 'e5f6a7b8-5555-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000003', 4, 'Màu đẹp, hơi nhanh phai', NOW(), NOW()),
('e1f2a3b4-bbbb-4000-8000-000000000007', 'e5f6a7b8-5555-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000004', 5, 'Sẽ mua lại!', NOW(), NOW()),
-- Serum: avg = 4.5 ⭐
('e1f2a3b4-bbbb-4000-8000-000000000008', 'e5f6a7b8-5555-4000-8000-000000000003', 'b8c9d0e1-8888-4000-8000-000000000001', 5, 'Serum thấm nhanh', NOW(), NOW()),
('e1f2a3b4-bbbb-4000-8000-000000000009', 'e5f6a7b8-5555-4000-8000-000000000003', 'b8c9d0e1-8888-4000-8000-000000000002', 4, 'Tốt nhưng hơi đắt', NOW(), NOW()),
-- Kem Innisfree: avg = 4.33 ⭐
('e1f2a3b4-bbbb-4000-8000-000000000010', 'e5f6a7b8-5555-4000-8000-000000000002', 'b8c9d0e1-8888-4000-8000-000000000001', 4, 'Kem dưỡng tốt', NOW(), NOW()),
('e1f2a3b4-bbbb-4000-8000-000000000011', 'e5f6a7b8-5555-4000-8000-000000000002', 'b8c9d0e1-8888-4000-8000-000000000002', 5, 'Mùi trà xanh dễ chịu', NOW(), NOW()),
('e1f2a3b4-bbbb-4000-8000-000000000012', 'e5f6a7b8-5555-4000-8000-000000000002', 'b8c9d0e1-8888-4000-8000-000000000003', 4, 'Dùng tốt cho da khô', NOW(), NOW());

-- ============================================
-- 7. WISHLISTS (CHO MOST-FAVORITE)
-- ============================================
INSERT INTO wishlists (id, product_id, user_id, created_at, updated_at) VALUES
-- Son Laneige: 4 ❤️
('f2a3b4c5-cccc-4000-8000-000000000001', 'e5f6a7b8-5555-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000001', NOW(), NOW()),
('f2a3b4c5-cccc-4000-8000-000000000002', 'e5f6a7b8-5555-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000002', NOW(), NOW()),
('f2a3b4c5-cccc-4000-8000-000000000003', 'e5f6a7b8-5555-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000003', NOW(), NOW()),
('f2a3b4c5-cccc-4000-8000-000000000004', 'e5f6a7b8-5555-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000004', NOW(), NOW()),
-- Mặt nạ: 3 ❤️
('f2a3b4c5-cccc-4000-8000-000000000005', 'e5f6a7b8-5555-4000-8000-000000000005', 'b8c9d0e1-8888-4000-8000-000000000001', NOW(), NOW()),
('f2a3b4c5-cccc-4000-8000-000000000006', 'e5f6a7b8-5555-4000-8000-000000000005', 'b8c9d0e1-8888-4000-8000-000000000002', NOW(), NOW()),
('f2a3b4c5-cccc-4000-8000-000000000007', 'e5f6a7b8-5555-4000-8000-000000000005', 'b8c9d0e1-8888-4000-8000-000000000003', NOW(), NOW()),
-- Kem Innisfree: 2 ❤️
('f2a3b4c5-cccc-4000-8000-000000000008', 'e5f6a7b8-5555-4000-8000-000000000002', 'b8c9d0e1-8888-4000-8000-000000000001', NOW(), NOW()),
('f2a3b4c5-cccc-4000-8000-000000000009', 'e5f6a7b8-5555-4000-8000-000000000002', 'b8c9d0e1-8888-4000-8000-000000000002', NOW(), NOW());

-- ============================================
-- XONG! Test các APIs:
-- GET /api/v1/products/homepage/best-selling
-- GET /api/v1/products/homepage/top-rated  
-- GET /api/v1/products/homepage/new-arrivals
-- GET /api/v1/products/homepage/most-favorite
-- ============================================
