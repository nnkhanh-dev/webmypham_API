-- Migration: Add order_id to reviews table
-- Date: 2026-01-10

-- Add order_id column to reviews table
ALTER TABLE reviews 
ADD COLUMN order_id VARCHAR(36) NULL AFTER user_id,
ADD CONSTRAINT fk_reviews_order_id FOREIGN KEY (order_id) REFERENCES orders(id);

-- Create index for faster lookups
CREATE INDEX idx_reviews_order_id ON reviews(order_id);

-- Add unique constraint to prevent multiple reviews per order-product combination
ALTER TABLE reviews 
ADD CONSTRAINT unique_order_product_review UNIQUE (order_id, product_id);
