-- PayPilot AI: Seed Data Script for PostgreSQL / SQLite
-- Note: All monetary amounts are in integer paise (1 INR = 100 paise)

-- 1. Merchants (Labelled clearly as DEMO)
INSERT INTO merchants (id, name, category, description, is_verified, is_active, created_at) VALUES
('m-0001-green-bowl-demo-0000', 'Green Bowl', 'Food', '[DEMO] Healthy vegetarian restaurant offering fresh, home-style meals.', TRUE, TRUE, CURRENT_TIMESTAMP),
('m-0002-daily-bites-demo-00', 'Daily Bites', 'Food', '[DEMO] Quick meals and snacks for every taste.', TRUE, TRUE, CURRENT_TIMESTAMP),
('m-0003-techzone-demo-00000', 'TechZone', 'Electronics', '[DEMO] Electronics accessories and gadgets at great prices.', TRUE, TRUE, CURRENT_TIMESTAMP),
('m-0004-urban-store-demo-00', 'Urban Store', 'Shopping', '[DEMO] Daily-use products and lifestyle items. [UNVERIFIED MERCHANT]', FALSE, TRUE, CURRENT_TIMESTAMP);

-- 2. Products
INSERT INTO products (id, merchant_id, name, description, price_paise, category, tags, is_available, created_at) VALUES
-- Green Bowl (Vegetarian)
('p-001', 'm-0001-green-bowl-demo-0000', 'Paneer Tikka Thali', 'Fresh paneer tikka with roti, rice, dal, and salad. Pure vegetarian.', 18000, 'Food', 'vegetarian,thali,paneer,lunch,dinner', TRUE, CURRENT_TIMESTAMP),
('p-002', 'm-0001-green-bowl-demo-0000', 'Veg Biryani Bowl', 'Fragrant vegetable biryani with raita and papad. Vegetarian.', 15000, 'Food', 'vegetarian,biryani,rice,lunch', TRUE, CURRENT_TIMESTAMP),
('p-003', 'm-0001-green-bowl-demo-0000', 'Garden Fresh Salad', 'Mixed greens with cherry tomatoes, cucumber, and house dressing. Vegan.', 12000, 'Food', 'vegan,salad,healthy,light', TRUE, CURRENT_TIMESTAMP),
('p-004', 'm-0001-green-bowl-demo-0000', 'Masala Dosa Combo', 'Crispy masala dosa with sambar and coconut chutney. Vegetarian.', 9000, 'Food', 'vegetarian,dosa,south-indian,breakfast', TRUE, CURRENT_TIMESTAMP),
('p-005', 'm-0001-green-bowl-demo-0000', 'Dal Makhani with Naan', 'Creamy black lentil dal served with butter naan. Vegetarian.', 16000, 'Food', 'vegetarian,dal,north-indian,dinner', TRUE, CURRENT_TIMESTAMP),

-- Daily Bites (Mixed)
('p-006', 'm-0002-daily-bites-demo-00', 'Chicken Biryani', 'Hyderabadi style chicken biryani with raita. Non-vegetarian.', 22000, 'Food', 'non-vegetarian,biryani,chicken,lunch', TRUE, CURRENT_TIMESTAMP),
('p-007', 'm-0002-daily-bites-demo-00', 'Veg Sandwich Meal', 'Grilled vegetable sandwich with fries and a drink. Vegetarian.', 8000, 'Food', 'vegetarian,sandwich,snack,light', TRUE, CURRENT_TIMESTAMP),
('p-008', 'm-0002-daily-bites-demo-00', 'Butter Chicken Thali', 'Rich butter chicken with naan, rice, and dessert. Non-vegetarian.', 25000, 'Food', 'non-vegetarian,chicken,thali,dinner', TRUE, CURRENT_TIMESTAMP),
('p-009', 'm-0002-daily-bites-demo-00', 'Mixed Fruit Smoothie', 'Fresh seasonal fruit smoothie. Vegan.', 11000, 'Food', 'vegan,smoothie,drink,healthy', TRUE, CURRENT_TIMESTAMP),
('p-010', 'm-0002-daily-bites-demo-00', 'Aloo Paratha Set', 'Two aloo parathas with curd and pickle. Vegetarian.', 7000, 'Food', 'vegetarian,paratha,breakfast,north-indian', TRUE, CURRENT_TIMESTAMP),

-- TechZone (Electronics)
('p-011', 'm-0003-techzone-demo-00000', 'Wireless Earbuds Pro', 'Bluetooth 5.3 wireless earbuds with 30-hour battery life and active noise cancellation. Great for music and calls.', 89900, 'Electronics', 'wireless,earphones,earbuds,bluetooth,battery,audio', TRUE, CURRENT_TIMESTAMP),
('p-012', 'm-0003-techzone-demo-00000', 'USB-C Fast Charger', '65W GaN fast charger, compatible with laptops and phones. Compact design.', 49900, 'Electronics', 'charger,usb-c,fast-charging,laptop,phone', TRUE, CURRENT_TIMESTAMP),
('p-013', 'm-0003-techzone-demo-00000', 'Laptop Stand', 'Adjustable aluminum laptop stand with ergonomic design. Fits 10-17 inch laptops.', 65000, 'Electronics', 'laptop,stand,ergonomic,aluminum', TRUE, CURRENT_TIMESTAMP),
('p-014', 'm-0003-techzone-demo-00000', 'Wireless Mouse', 'Silent click wireless mouse with USB receiver. 18-month battery life.', 35000, 'Electronics', 'mouse,wireless,silent,usb', TRUE, CURRENT_TIMESTAMP),
('p-015', 'm-0003-techzone-demo-00000', 'Phone Screen Protector', '9H tempered glass screen protector with anti-fingerprint coating. Easy installation.', 14900, 'Electronics', 'screen-protector,phone,tempered-glass', TRUE, CURRENT_TIMESTAMP),

-- Urban Store (Shopping, Unverified)
('p-016', 'm-0004-urban-store-demo-00', 'Bamboo Water Bottle', 'Eco-friendly bamboo water bottle, 500ml capacity. BPA-free and sustainable.', 29900, 'Shopping', 'bottle,eco-friendly,bamboo,sustainable', TRUE, CURRENT_TIMESTAMP),
('p-017', 'm-0004-urban-store-demo-00', 'Cotton Tote Bag', 'Organic cotton tote bag. Machine washable, perfect for daily use.', 19900, 'Shopping', 'bag,cotton,eco-friendly,tote', TRUE, CURRENT_TIMESTAMP),
('p-018', 'm-0004-urban-store-demo-00', 'LED Desk Lamp', 'Adjustable LED desk lamp with 3 brightness levels. USB powered.', 45000, 'Shopping', 'lamp,desk,led,usb', TRUE, CURRENT_TIMESTAMP),
('p-019', 'm-0004-urban-store-demo-00', 'Notebook Set (3-pack)', 'A5 ruled notebooks, 200 pages each. Premium quality paper.', 18000, 'Shopping', 'notebook,stationery,paper', TRUE, CURRENT_TIMESTAMP),
('p-020', 'm-0004-urban-store-demo-00', 'Stainless Steel Lunch Box', '3-compartment stainless steel lunch box with insulated bag.', 35000, 'Shopping', 'lunchbox,kitchen,stainless-steel', TRUE, CURRENT_TIMESTAMP);
