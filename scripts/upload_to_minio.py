from minio import Minio
import pandas as pd

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Создаём бакет
if not client.bucket_exists("raw-data"):
    client.make_bucket("raw-data")

# Создаём тестовые данные
df = pd.DataFrame({
    'product_id': [1, 2, 3, 4, 5],
    'product_name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones'],
    'price': [1200.00, 25.50, 75.00, 350.00, 89.99],
    'category': ['Electronics', 'Accessories', 'Accessories', 'Electronics', 'Audio']
})

# Сохраняем в CSV
df.to_csv('products.csv', index=False)

# Загружаем в MinIO
client.fput_object("raw-data", "products.csv", "products.csv")
print("✅ products.csv загружен в MinIO")