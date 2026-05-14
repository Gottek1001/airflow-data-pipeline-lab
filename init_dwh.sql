-- ============================================
-- ХРАНИЛИЩЕ ДАННЫХ (DWH)
-- ============================================

-- Создаём пользователя для Airflow (если нет)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'airflow') THEN
        CREATE USER airflow WITH PASSWORD 'airflow';
    END IF;
END
$$;

ALTER USER airflow CREATEDB;

-- ============================================
-- СХЕМЫ ДЛЯ ДАННЫХ
-- ============================================

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS mart;

-- ============================================
-- ТАБЛИЦЫ ДЛЯ ЗАГРУЗКИ ИЗ API
-- ============================================
CREATE TABLE IF NOT EXISTS raw.api_orders (
    id SERIAL PRIMARY KEY,
    order_id INTEGER,
    customer_id INTEGER,
    product VARCHAR(200),
    amount DECIMAL(10,2),
    quantity INTEGER,
    status VARCHAR(50),
    order_date TIMESTAMP,
    load_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- ТАБЛИЦЫ ДЛЯ ИНКРЕМЕНТАЛЬНОЙ ЗАГРУЗКИ ИЗ PostgreSQL
-- ============================================
CREATE TABLE IF NOT EXISTS raw.pg_users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    status VARCHAR(20),
    source_updated_at TIMESTAMP,
    loaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw.pg_orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    amount DECIMAL(10,2),
    order_date DATE,
    loaded_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- ТАБЛИЦЫ ДЛЯ ЗАГРУЗКИ ИЗ MINIO (S3)
-- ============================================
CREATE TABLE IF NOT EXISTS raw.minio_products (
    id SERIAL PRIMARY KEY,
    product_id INTEGER,
    product_name VARCHAR(200),
    price DECIMAL(10,2),
    category VARCHAR(100),
    load_date DATE,
    loaded_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- ОБРАБОТАННЫЙ СЛОЙ (витрины)
-- ============================================
CREATE TABLE IF NOT EXISTS mart.orders_with_users (
    order_id INTEGER,
    user_name VARCHAR(100),
    email VARCHAR(100),
    amount DECIMAL(10,2),
    order_date DATE
);

-- Лог загрузок
CREATE TABLE IF NOT EXISTS mart.load_log (
    id SERIAL PRIMARY KEY,
    dag_name VARCHAR(100),
    source_name VARCHAR(50),
    rows_loaded INT,
    status VARCHAR(20),
    error_message TEXT,
    load_timestamp TIMESTAMP DEFAULT NOW()
);

-- Тестовая запись
INSERT INTO raw.api_orders (order_id, customer_id, product, amount, quantity, status, order_date, load_date)
VALUES (999, 999, 'test', 0, 0, 'test', NOW(), CURRENT_DATE);

SELECT 'DWH is ready!' as status;