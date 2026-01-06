-- ============================================
-- MOCK DATA CHO TEST APIs
-- Chạy file này trong MySQL để có dữ liệu test
-- ============================================

-- 1. Tạo Type (Loại thuộc tính)
INSERT INTO types (id, name, created_at, updated_at) VALUES
('a1b2c3d4-1111-4000-8000-000000000001', 'Màu sắc', NOW(), NOW()),
('a1b2c3d4-1111-4000-8000-000000000002', 'Dung tích', NOW(), NOW());

-- 2. Tạo TypeValue (Giá trị cụ thể)
INSERT INTO type_values (id, name, type_id, created_at, updated_at) VALUES
('b2c3d4e5-2222-4000-8000-000000000001', 'Đỏ', 'a1b2c3d4-1111-4000-8000-000000000001', NOW(), NOW()),
('b2c3d4e5-2222-4000-8000-000000000002', 'Hồng', 'a1b2c3d4-1111-4000-8000-000000000001', NOW(), NOW()),
('b2c3d4e5-2222-4000-8000-000000000003', 'Cam', 'a1b2c3d4-1111-4000-8000-000000000001', NOW(), NOW()),
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

-- 5. Tạo Products (6 sản phẩm)
INSERT INTO products (id, name, description, thumbnail, is_active, brand_id, category_id, created_at, updated_at) VALUES
('e5f6a7b8-5555-4000-8000-000000000001', 'Son Môi Laneige Lip Sleeping Mask', 'Son dưỡng môi ban đêm', '/images/laneige-lip.jpg', 1, 'c3d4e5f6-3333-4000-8000-000000000001', 'd4e5f6a7-4444-4000-8000-000000000001', DATE_SUB(NOW(), INTERVAL 30 DAY), NOW()),
('e5f6a7b8-5555-4000-8000-000000000002', 'Kem Dưỡng Innisfree Green Tea', 'Kem dưỡng ẩm từ trà xanh', '/images/innisfree-cream.jpg', 1, 'c3d4e5f6-3333-4000-8000-000000000002', 'd4e5f6a7-4444-4000-8000-000000000002', DATE_SUB(NOW(), INTERVAL 25 DAY), NOW()),
('e5f6a7b8-5555-4000-8000-000000000003', 'Serum Vitamin C Laneige', 'Serum sáng da với vitamin C', '/images/laneige-serum.jpg', 1, 'c3d4e5f6-3333-4000-8000-000000000001', 'd4e5f6a7-4444-4000-8000-000000000002', DATE_SUB(NOW(), INTERVAL 5 DAY), NOW()),
('e5f6a7b8-5555-4000-8000-000000000004', 'Tẩy Trang Innisfree Apple', 'Nước tẩy trang từ táo xanh', '/images/innisfree-cleanser.jpg', 1, 'c3d4e5f6-3333-4000-8000-000000000002', 'd4e5f6a7-4444-4000-8000-000000000002', DATE_SUB(NOW(), INTERVAL 3 DAY), NOW()),
('e5f6a7b8-5555-4000-8000-000000000005', 'Mặt Nạ Innisfree Volcanic', 'Mặt nạ đất sét núi lửa', '/images/innisfree-mask.jpg', 1, 'c3d4e5f6-3333-4000-8000-000000000002', 'd4e5f6a7-4444-4000-8000-000000000002', DATE_SUB(NOW(), INTERVAL 1 DAY), NOW()),
('e5f6a7b8-5555-4000-8000-000000000006', 'Son Dưỡng Laneige Glowy', 'Son dưỡng bóng tự nhiên', '/images/laneige-glowy.jpg', 1, 'c3d4e5f6-3333-4000-8000-000000000001', 'd4e5f6a7-4444-4000-8000-000000000001', NOW(), NOW());

-- 6. Tạo ProductTypes (biến thể)
INSERT INTO product_types (id, product_id, type_value_id, price, discount_price, stock, image_path, volume, origin, skin_type, created_at, updated_at) VALUES
-- Son Laneige Lip Sleeping Mask - 3 màu
('f6a7b8c9-6666-4000-8000-000000000001', 'e5f6a7b8-5555-4000-8000-000000000001', 'b2c3d4e5-2222-4000-8000-000000000001', 350000, 299000, 30, '/images/laneige-red.jpg', '8g', 'Hàn Quốc', 'Mọi loại da', NOW(), NOW()),
('f6a7b8c9-6666-4000-8000-000000000002', 'e5f6a7b8-5555-4000-8000-000000000001', 'b2c3d4e5-2222-4000-8000-000000000002', 350000, 299000, 25, '/images/laneige-pink.jpg', '8g', 'Hàn Quốc', 'Mọi loại da', NOW(), NOW()),
('f6a7b8c9-6666-4000-8000-000000000003', 'e5f6a7b8-5555-4000-8000-000000000001', 'b2c3d4e5-2222-4000-8000-000000000003', 350000, 299000, 0, '/images/laneige-orange.jpg', '8g', 'Hàn Quốc', 'Mọi loại da', NOW(), NOW()),
-- Kem Innisfree - 3 dung tích
('f6a7b8c9-6666-4000-8000-000000000004', 'e5f6a7b8-5555-4000-8000-000000000002', 'b2c3d4e5-2222-4000-8000-000000000004', 450000, 399000, 50, '/images/innisfree-50.jpg', '50ml', 'Hàn Quốc', 'Da khô', NOW(), NOW()),
('f6a7b8c9-6666-4000-8000-000000000005', 'e5f6a7b8-5555-4000-8000-000000000002', 'b2c3d4e5-2222-4000-8000-000000000005', 750000, 650000, 20, '/images/innisfree-100.jpg', '100ml', 'Hàn Quốc', 'Da khô', NOW(), NOW()),
('f6a7b8c9-6666-4000-8000-000000000006', 'e5f6a7b8-5555-4000-8000-000000000002', 'b2c3d4e5-2222-4000-8000-000000000006', 1200000, 999000, 10, '/images/innisfree-200.jpg', '200ml', 'Hàn Quốc', 'Da khô', NOW(), NOW()),
-- Serum, Tẩy trang, Mặt nạ, Son Glowy
('f6a7b8c9-6666-4000-8000-000000000007', 'e5f6a7b8-5555-4000-8000-000000000003', NULL, 890000, 750000, 40, '/images/laneige-serum.jpg', '30ml', 'Hàn Quốc', 'Mọi loại da', NOW(), NOW()),
('f6a7b8c9-6666-4000-8000-000000000008', 'e5f6a7b8-5555-4000-8000-000000000004', NULL, 350000, 299000, 100, '/images/innisfree-cleanser.jpg', '200ml', 'Hàn Quốc', 'Mọi loại da', NOW(), NOW()),
('f6a7b8c9-6666-4000-8000-000000000009', 'e5f6a7b8-5555-4000-8000-000000000005', NULL, 150000, 120000, 200, '/images/innisfree-mask.jpg', '85g', 'Hàn Quốc', 'Da dầu', NOW(), NOW()),
('f6a7b8c9-6666-4000-8000-000000000010', 'e5f6a7b8-5555-4000-8000-000000000006', 'b2c3d4e5-2222-4000-8000-000000000001', 280000, 230000, 60, '/images/laneige-glowy-red.jpg', '10g', 'Hàn Quốc', 'Mọi loại da', NOW(), NOW()),
('f6a7b8c9-6666-4000-8000-000000000011', 'e5f6a7b8-5555-4000-8000-000000000006', 'b2c3d4e5-2222-4000-8000-000000000002', 280000, 230000, 45, '/images/laneige-glowy-pink.jpg', '10g', 'Hàn Quốc', 'Mọi loại da', NOW(), NOW());

-- 7. Tạo Role
INSERT IGNORE INTO roles (id, name, created_at, updated_at) VALUES
('a7b8c9d0-7777-4000-8000-000000000001', 'CLIENT', NOW(), NOW());

-- 8. Tạo Users (4 users)
INSERT INTO users (id, email, password_hash, first_name, last_name, phone_number, created_at, updated_at) VALUES
('b8c9d0e1-8888-4000-8000-000000000001', 'test@example.com', '$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$hash', 'Test', 'User', '0901234567', NOW(), NOW()),
('b8c9d0e1-8888-4000-8000-000000000002', 'user2@example.com', '$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$hash2', 'Nguyễn', 'Văn A', '0901234568', NOW(), NOW()),
('b8c9d0e1-8888-4000-8000-000000000003', 'user3@example.com', '$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$hash3', 'Trần', 'Thị B', '0901234569', NOW(), NOW()),
('b8c9d0e1-8888-4000-8000-000000000004', 'user4@example.com', '$argon2id$v=19$m=65536,t=3,p=4$c29tZXNhbHQ$hash4', 'Lê', 'Văn C', '0901234570', NOW(), NOW());

-- 9. Gán role cho users
INSERT INTO user_roles (user_id, role_id) VALUES
('b8c9d0e1-8888-4000-8000-000000000001', 'a7b8c9d0-7777-4000-8000-000000000001'),
('b8c9d0e1-8888-4000-8000-000000000002', 'a7b8c9d0-7777-4000-8000-000000000001'),
('b8c9d0e1-8888-4000-8000-000000000003', 'a7b8c9d0-7777-4000-8000-000000000001'),
('b8c9d0e1-8888-4000-8000-000000000004', 'a7b8c9d0-7777-4000-8000-000000000001');

-- 10. Tạo Cart
INSERT INTO carts (id, user_id, created_at, updated_at) VALUES
('c9d0e1f2-9999-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000001', NOW(), NOW());

-- 11. Tạo CartItems
INSERT INTO cart_items (id, cart_id, product_type_id, quantity, created_at, updated_at) VALUES
('d0e1f2a3-aaaa-4000-8000-000000000001', 'c9d0e1f2-9999-4000-8000-000000000001', 'f6a7b8c9-6666-4000-8000-000000000001', 2, NOW(), NOW()),
('d0e1f2a3-aaaa-4000-8000-000000000002', 'c9d0e1f2-9999-4000-8000-000000000001', 'f6a7b8c9-6666-4000-8000-000000000005', 1, NOW(), NOW());


-- ============================================
-- MOCK DATA CHO HOMEPAGE APIs
-- ============================================

-- 12. Tạo Orders (đơn hàng hoàn thành - cho Best Selling)
INSERT INTO orders (id, user_id, status, total_amount, discount_amount, final_amount, created_at, updated_at) VALUES
-- Đơn 1: User1 mua Mặt nạ (nhiều nhất)
('g1h2i3j4-dddd-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000001', 'completed', 600000, 0, 600000, NOW(), NOW()),
-- Đơn 2: User2 mua Mặt nạ + Kem
('g1h2i3j4-dddd-4000-8000-000000000002', 'b8c9d0e1-8888-4000-8000-000000000002', 'completed', 900000, 0, 900000, NOW(), NOW()),
-- Đơn 3: User3 mua Son + Tẩy trang
('g1h2i3j4-dddd-4000-8000-000000000003', 'b8c9d0e1-8888-4000-8000-000000000003', 'delivered', 650000, 0, 650000, NOW(), NOW()),
-- Đơn 4: User4 mua Mặt nạ + Serum
('g1h2i3j4-dddd-4000-8000-000000000004', 'b8c9d0e1-8888-4000-8000-000000000004', 'completed', 1040000, 0, 1040000, NOW(), NOW()),
-- Đơn 5: User1 mua thêm Mặt nạ
('g1h2i3j4-dddd-4000-8000-000000000005', 'b8c9d0e1-8888-4000-8000-000000000001', 'completed', 300000, 0, 300000, NOW(), NOW());

-- 13. Tạo OrderDetails (chi tiết đơn hàng - tính số lượng bán)
INSERT INTO order_details (id, order_id, product_type_id, price, number, created_at, updated_at) VALUES
-- Đơn 1: 5 Mặt nạ
('h2i3j4k5-eeee-4000-8000-000000000001', 'g1h2i3j4-dddd-4000-8000-000000000001', 'f6a7b8c9-6666-4000-8000-000000000009', 120000, 5, NOW(), NOW()),
-- Đơn 2: 3 Mặt nạ + 2 Kem 50ml
('h2i3j4k5-eeee-4000-8000-000000000002', 'g1h2i3j4-dddd-4000-8000-000000000002', 'f6a7b8c9-6666-4000-8000-000000000009', 120000, 3, NOW(), NOW()),
('h2i3j4k5-eeee-4000-8000-000000000003', 'g1h2i3j4-dddd-4000-8000-000000000002', 'f6a7b8c9-6666-4000-8000-000000000004', 399000, 2, NOW(), NOW()),
-- Đơn 3: 1 Son Đỏ + 2 Tẩy trang
('h2i3j4k5-eeee-4000-8000-000000000004', 'g1h2i3j4-dddd-4000-8000-000000000003', 'f6a7b8c9-6666-4000-8000-000000000001', 299000, 1, NOW(), NOW()),
('h2i3j4k5-eeee-4000-8000-000000000005', 'g1h2i3j4-dddd-4000-8000-000000000003', 'f6a7b8c9-6666-4000-8000-000000000008', 299000, 2, NOW(), NOW()),
-- Đơn 4: 4 Mặt nạ + 1 Serum
('h2i3j4k5-eeee-4000-8000-000000000006', 'g1h2i3j4-dddd-4000-8000-000000000004', 'f6a7b8c9-6666-4000-8000-000000000009', 120000, 4, NOW(), NOW()),
('h2i3j4k5-eeee-4000-8000-000000000007', 'g1h2i3j4-dddd-4000-8000-000000000004', 'f6a7b8c9-6666-4000-8000-000000000007', 750000, 1, NOW(), NOW()),
-- Đơn 5: 3 Mặt nạ
('h2i3j4k5-eeee-4000-8000-000000000008', 'g1h2i3j4-dddd-4000-8000-000000000005', 'f6a7b8c9-6666-4000-8000-000000000009', 120000, 3, NOW(), NOW());

-- Tổng số bán: Mặt nạ = 15, Kem 50ml = 2, Son Đỏ = 1, Tẩy trang = 2, Serum = 1

-- 14. Tạo Reviews (cho Top Rated)
INSERT INTO reviews (id, product_id, user_id, rating, comment, created_at, updated_at) VALUES
-- Mặt nạ: avg = 5.0 (rating cao nhất)
('e1f2a3b4-bbbb-4000-8000-000000000001', 'e5f6a7b8-5555-4000-8000-000000000005', 'b8c9d0e1-8888-4000-8000-000000000001', 5, 'Mặt nạ tuyệt vời!', NOW(), NOW()),
('e1f2a3b4-bbbb-4000-8000-000000000002', 'e5f6a7b8-5555-4000-8000-000000000005', 'b8c9d0e1-8888-4000-8000-000000000002', 5, 'Da mịn hẳn sau khi dùng', NOW(), NOW()),
('e1f2a3b4-bbbb-4000-8000-000000000003', 'e5f6a7b8-5555-4000-8000-000000000005', 'b8c9d0e1-8888-4000-8000-000000000003', 5, 'Kiểm soát dầu rất tốt', NOW(), NOW()),
-- Son Laneige: avg = 4.75
('e1f2a3b4-bbbb-4000-8000-000000000004', 'e5f6a7b8-5555-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000001', 5, 'Son rất đẹp, màu lên chuẩn!', NOW(), NOW()),
('e1f2a3b4-bbbb-4000-8000-000000000005', 'e5f6a7b8-5555-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000002', 5, 'Dưỡng môi rất mềm mịn', NOW(), NOW()),
('e1f2a3b4-bbbb-4000-8000-000000000006', 'e5f6a7b8-5555-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000003', 4, 'Màu đẹp, hơi nhanh phai', NOW(), NOW()),
('e1f2a3b4-bbbb-4000-8000-000000000007', 'e5f6a7b8-5555-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000004', 5, 'Rất thích, sẽ mua lại!', NOW(), NOW()),
-- Serum: avg = 4.5
('e1f2a3b4-bbbb-4000-8000-000000000008', 'e5f6a7b8-5555-4000-8000-000000000003', 'b8c9d0e1-8888-4000-8000-000000000001', 5, 'Serum thấm nhanh, da sáng', NOW(), NOW()),
('e1f2a3b4-bbbb-4000-8000-000000000009', 'e5f6a7b8-5555-4000-8000-000000000003', 'b8c9d0e1-8888-4000-8000-000000000002', 4, 'Tốt nhưng hơi đắt', NOW(), NOW()),
-- Kem Innisfree: avg = 4.33
('e1f2a3b4-bbbb-4000-8000-000000000010', 'e5f6a7b8-5555-4000-8000-000000000002', 'b8c9d0e1-8888-4000-8000-000000000001', 4, 'Kem dưỡng tốt, thấm nhanh', NOW(), NOW()),
('e1f2a3b4-bbbb-4000-8000-000000000011', 'e5f6a7b8-5555-4000-8000-000000000002', 'b8c9d0e1-8888-4000-8000-000000000002', 5, 'Mùi trà xanh dễ chịu', NOW(), NOW()),
('e1f2a3b4-bbbb-4000-8000-000000000012', 'e5f6a7b8-5555-4000-8000-000000000002', 'b8c9d0e1-8888-4000-8000-000000000003', 4, 'Dùng tốt cho da khô', NOW(), NOW());

-- 15. Tạo Wishlists (cho Most Favorite)
INSERT INTO wishlists (id, product_id, user_id, created_at, updated_at) VALUES
-- Son Laneige: 4 người yêu thích
('f2a3b4c5-cccc-4000-8000-000000000001', 'e5f6a7b8-5555-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000001', NOW(), NOW()),
('f2a3b4c5-cccc-4000-8000-000000000002', 'e5f6a7b8-5555-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000002', NOW(), NOW()),
('f2a3b4c5-cccc-4000-8000-000000000003', 'e5f6a7b8-5555-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000003', NOW(), NOW()),
('f2a3b4c5-cccc-4000-8000-000000000004', 'e5f6a7b8-5555-4000-8000-000000000001', 'b8c9d0e1-8888-4000-8000-000000000004', NOW(), NOW()),
-- Mặt nạ: 3 người yêu thích
('f2a3b4c5-cccc-4000-8000-000000000005', 'e5f6a7b8-5555-4000-8000-000000000005', 'b8c9d0e1-8888-4000-8000-000000000001', NOW(), NOW()),
('f2a3b4c5-cccc-4000-8000-000000000006', 'e5f6a7b8-5555-4000-8000-000000000005', 'b8c9d0e1-8888-4000-8000-000000000002', NOW(), NOW()),
('f2a3b4c5-cccc-4000-8000-000000000007', 'e5f6a7b8-5555-4000-8000-000000000005', 'b8c9d0e1-8888-4000-8000-000000000003', NOW(), NOW()),
-- Kem Innisfree: 2 người yêu thích
('f2a3b4c5-cccc-4000-8000-000000000008', 'e5f6a7b8-5555-4000-8000-000000000002', 'b8c9d0e1-8888-4000-8000-000000000001', NOW(), NOW()),
('f2a3b4c5-cccc-4000-8000-000000000009', 'e5f6a7b8-5555-4000-8000-000000000002', 'b8c9d0e1-8888-4000-8000-000000000002', NOW(), NOW());


-- ============================================
-- KẾT QUẢ MONG ĐỢI
-- ============================================
-- 
-- GET /api/v1/products/homepage/best-selling
-- → Mặt nạ (15) > Kem (2) = Tẩy trang (2) > Son (1) > Serum (1)
--
-- GET /api/v1/products/homepage/top-rated
-- → Mặt nạ (5.0) > Son (4.75) > Serum (4.5) > Kem (4.33)
--
-- GET /api/v1/products/homepage/new-arrivals
-- → Son Glowy > Mặt nạ > Tẩy trang > Serum > Kem > Son Laneige
--
-- GET /api/v1/products/homepage/most-favorite
-- → Son (4) > Mặt nạ (3) > Kem (2)
--
-- ============================================
