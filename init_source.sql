-- ============================================
-- БАЗА ДАННЫХ-ИСТОЧНИК
-- ============================================

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Вставляем 10 пользователей
INSERT INTO users (name, email, status) VALUES 
    ('Alice Johnson', 'alice.johnson@example.com', 'active'),
    ('Bob Smith', 'bob.smith@example.com', 'active'),
    ('Carol Davis', 'carol.davis@example.com', 'active'),
    ('David Wilson', 'david.wilson@example.com', 'active'),
    ('Elena Brown', 'elena.brown@example.com', 'active'),
    ('Frank Miller', 'frank.miller@example.com', 'inactive'),
    ('Grace Lee', 'grace.lee@example.com', 'active'),
    ('Henry Clark', 'henry.clark@example.com', 'active'),
    ('Irina Petrova', 'irina.petrova@example.com', 'inactive'),
    ('John Doe', 'john.doe@example.com', 'active');

-- Таблица заказов
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount DECIMAL(10,2),
    order_date DATE DEFAULT CURRENT_DATE
);

-- Вставляем 20 заказов (разные пользователи, разные даты)
INSERT INTO orders (user_id, amount, order_date) VALUES 
    (1, 150.00, '2024-01-10'),
    (1, 75.50, '2024-01-15'),
    (1, 200.00, '2024-01-20'),
    (2, 300.00, '2024-01-12'),
    (2, 45.00, '2024-01-18'),
    (3, 120.00, '2024-01-14'),
    (3, 80.00, '2024-01-22'),
    (4, 500.00, '2024-01-16'),
    (4, 35.00, '2024-01-25'),
    (5, 250.00, '2024-01-19'),
    (6, 60.00, '2024-01-21'),
    (7, 180.00, '2024-01-23'),
    (8, 420.00, '2024-01-24'),
    (9, 90.00, '2024-01-26'),
    (10, 350.00, '2024-01-27'),
    (1, 110.00, '2024-02-01'),
    (3, 95.00, '2024-02-03'),
    (5, 670.00, '2024-02-05'),
    (7, 45.00, '2024-02-07'),
    (10, 230.00, '2024-02-10');

-- Таблица продуктов (для разнообразия)
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10,2),
    category VARCHAR(50)
);

INSERT INTO products (name, price, category) VALUES 
    ('Laptop', 1200.00, 'Electronics'),
    ('Mouse', 25.50, 'Accessories'),
    ('Keyboard', 75.00, 'Accessories'),
    ('Monitor', 350.00, 'Electronics'),
    ('Headphones', 89.99, 'Audio'),
    ('USB Cable', 12.99, 'Accessories'),
    ('Webcam', 149.99, 'Electronics'),
    ('Desk Mat', 29.99, 'Accessories'),
    ('Speakers', 199.99, 'Audio'),
    ('External SSD', 899.99, 'Storage');

-- Функция для автообновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_users 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Проверка
SELECT 'Source DB is ready!' as status;
SELECT COUNT(*) AS users_count FROM users;
SELECT COUNT(*) AS orders_count FROM orders;
SELECT COUNT(*) AS products_count FROM products;