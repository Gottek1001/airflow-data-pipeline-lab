from fastapi import FastAPI
import random
from datetime import datetime

app = FastAPI(title="Mock API for Airflow Lab")

PRODUCTS = ["Laptop", "Mouse", "Keyboard", "Monitor", "Headphones", "Webcam", "USB Cable"]
STATUSES = ["pending", "processing", "shipped", "delivered"]

@app.get("/")
def root():
    return {"message": "Mock API is running", "endpoints": ["/orders", "/health"]}

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/orders")
def get_orders(limit: int = 10):
    """Возвращает список заказов из API"""
    return {
        "source": "mock_api",
        "timestamp": datetime.now().isoformat(),
        "total": limit,
        "data": [
            {
                "order_id": random.randint(10000, 99999),
                "customer_id": random.randint(1000, 9999),
                "product": random.choice(PRODUCTS),
                "amount": round(random.uniform(10, 5000), 2),
                "quantity": random.randint(1, 5),
                "status": random.choice(STATUSES),
                "order_date": datetime.now().isoformat()
            }
            for _ in range(limit)
        ]
    }