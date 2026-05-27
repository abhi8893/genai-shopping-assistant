-- First, clear existing data to avoid unique constraint errors
DELETE FROM cart_item;
DELETE FROM cart;
DELETE FROM product;
DELETE FROM "user";
DELETE FROM product_hierarchy;

-- Insert into product_hierarchy
INSERT INTO product_hierarchy (id, category_id, subcategory_id, category_name, subcategory_name) VALUES
(1, 1, 1, 'Electronics', 'Laptops'),
(2, 1, 2, 'Electronics', 'Smartphones'),
(3, 2, 1, 'Fashion', 'Men'),
(4, 2, 2, 'Fashion', 'Women'),
(5, 3, 1, 'Home & Kitchen', 'Furniture'),
(6, 3, 2, 'Home & Kitchen', 'Appliances');

-- Insert users
INSERT INTO "user" (id, first_name, last_name, role, created_at) VALUES
(1, 'John', 'Doe', 'user', CURRENT_TIMESTAMP),
(2, 'Jane', 'Smith', 'admin', CURRENT_TIMESTAMP),
(3, 'Bob', 'Johnson', 'user', CURRENT_TIMESTAMP),
(4, 'Alice', 'Williams', 'user', CURRENT_TIMESTAMP);

-- Insert products
INSERT INTO product (id, category_id, subcategory_id, name, description, price, created_at) VALUES
(1, 1, 1, 'MacBook Pro', '16-inch MacBook Pro with M2 Pro chip', 1999.99, CURRENT_TIMESTAMP),
(2, 1, 1, 'Dell XPS 15', '15.6-inch 4K UHD+ Touch Laptop', 1499.99, CURRENT_TIMESTAMP),
(3, 1, 2, 'iPhone 14 Pro', '6.1-inch Super Retina XDR display', 999.00, CURRENT_TIMESTAMP),
(4, 1, 2, 'Samsung Galaxy S23', '6.8-inch Dynamic AMOLED 2X', 1199.99, CURRENT_TIMESTAMP),
(5, 2, 1, 'Men''s Casual Shirt', 'Cotton casual shirt for men', 29.99, CURRENT_TIMESTAMP),
(6, 2, 2, 'Women''s Summer Dress', 'Floral summer dress', 39.99, CURRENT_TIMESTAMP),
(7, 3, 1, 'Leather Sofa', '3-seater genuine leather sofa', 899.99, CURRENT_TIMESTAMP),
(8, 3, 2, 'Air Fryer', '5.5L Digital Air Fryer', 89.99, CURRENT_TIMESTAMP);

-- Insert carts
INSERT INTO cart (id, user_id, amount, created_at) VALUES
(1, 1, 2999.99, CURRENT_TIMESTAMP),  -- John's cart
(2, 2, 149.97, CURRENT_TIMESTAMP),   -- Jane's cart
(3, 3, 0, CURRENT_TIMESTAMP);        -- Bob's empty cart

-- Insert cart items
INSERT INTO cart_item (id, cart_id, product_id, quantity, amount) VALUES
(1, 1, 1, 1, 1999.99),  -- John: MacBook Pro
(2, 1, 3, 1, 999.00),   -- John: iPhone 14 Pro
(3, 2, 5, 5, 149.97);   -- Jane: 5x Men's Casual Shirt