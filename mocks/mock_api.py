"""
Mock API Service - FastAPI-based mock server for isolated testing.
Provides predictable responses for API tests without external dependencies.
"""
import random
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Header, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Mock E-Commerce API", version="1.0.0")

# ─── In-memory data store ───
ORDERS: Dict[str, dict] = {}
PRODUCTS = {
    "PROD-001": {"product_id": "PROD-001", "name": "Wireless Headphones", "price": 49.99, "stock": 150},
    "PROD-002": {"product_id": "PROD-002", "name": "USB-C Cable", "price": 12.99, "stock": 500},
    "PROD-003": {"product_id": "PROD-003", "name": "Laptop Stand", "price": 79.99, "stock": 75},
    "PROD-004": {"product_id": "PROD-004", "name": "Mechanical Keyboard", "price": 129.99, "stock": 200},
    "PROD-005": {"product_id": "PROD-005", "name": "Webcam HD", "price": 89.99, "stock": 100},
}
USERS: Dict[str, dict] = {}


class CreateOrderRequest(BaseModel):
    customer_id: str
    product_id: str
    quantity: int = Field(gt=0)
    idempotency_key: Optional[str] = None


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


# ─── Health ───
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "mock-api", "version": "1.0.0"}


# ─── Auth ───
@app.post("/api/v1/auth/register")
async def register(req: RegisterRequest):
    if req.email in USERS:
        raise HTTPException(status_code=409, detail="Email already registered")
    USERS[req.email] = {"email": req.email, "password": req.password, "full_name": req.full_name}
    return {"access_token": f"mock-token-{uuid.uuid4().hex[:8]}", "token_type": "bearer"}


@app.post("/api/v1/auth/login")
async def login(req: LoginRequest):
    user = USERS.get(req.email)
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": f"mock-token-{uuid.uuid4().hex[:8]}", "token_type": "bearer"}


# ─── Orders ───
@app.post("/api/v1/orders", status_code=201)
async def create_order(req: CreateOrderRequest):
    product = PRODUCTS.get(req.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    order_id = f"ORD-{uuid.uuid4().hex[:6].upper()}"
    order = {
        "order_id": order_id,
        "customer_id": req.customer_id,
        "product_id": req.product_id,
        "quantity": req.quantity,
        "total_amount": product["price"] * req.quantity,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    ORDERS[order_id] = order
    return order


@app.get("/api/v1/orders/{order_id}")
async def get_order(order_id: str):
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.get("/api/v1/orders")
async def list_orders(page: int = 1, page_size: int = 20, customer_id: Optional[str] = None):
    orders = list(ORDERS.values())
    if customer_id:
        orders = [o for o in orders if o["customer_id"] == customer_id]
    
    total = len(orders)
    start = (page - 1) * page_size
    end = start + page_size
    items = orders[start:end]
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@app.put("/api/v1/orders/{order_id}/cancel")
async def cancel_order(order_id: str):
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order["status"] in ("cancelled", "delivered", "shipped"):
        raise HTTPException(status_code=400, detail=f"Cannot cancel order in '{order['status']}' status")
    order["status"] = "cancelled"
    order["updated_at"] = datetime.utcnow().isoformat()
    return {"order_id": order_id, "status": "cancelled"}


# ─── Inventory ───
@app.get("/api/v1/inventory/{product_id}")
async def get_inventory(product_id: str):
    product = PRODUCTS.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "product_id": product["product_id"],
        "product_name": product["name"],
        "quantity_available": product["stock"],
        "unit_price": product["price"],
    }


@app.get("/api/v1/inventory")
async def list_inventory():
    return {
        "items": [
            {"product_id": p["product_id"], "product_name": p["name"], "quantity_available": p["stock"], "unit_price": p["price"]}
            for p in PRODUCTS.values()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
