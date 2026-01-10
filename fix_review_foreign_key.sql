-- Fix: Change reviews.product_id to reference product_types instead of products

-- 1. Drop existing foreign key constraint
ALTER TABLE reviews DROP FOREIGN KEY reviews_ibfk_1;

-- 2. Add new foreign key pointing to product_types
ALTER TABLE reviews 
ADD CONSTRAINT fk_reviews_product_type_id 
FOREIGN KEY (product_id) REFERENCES product_types(id) ON DELETE CASCADE;
