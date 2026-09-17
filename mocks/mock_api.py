"""
Mock API Service - FastAPI-based mock server for isolated testing.
Provides predictable responses for API tests without external dependencies.
"""
import base64
import re
import uuid
from datetime import datetime
from typing import Dict, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Mock E-Commerce API", version="1.0.0")

ORDERS: Dict[str, dict] = {}
IDEMPOTENCY: Dict[str, str] = {}
PRODUCTS: Dict[str, dict] = {
    "PROD-001": {"product_id": "PROD-001", "name": "Wireless Headphones", "price": 49.99, "stock": 150},
    "PROD-002": {"product_id": "PROD-002", "name": "USB-C Cable", "price": 12.99, "stock": 500},
    "PROD-003": {"product_id": "PROD-003", "name": "Laptop Stand", "price": 79.99, "stock": 75},
    "PROD-004": {"product_id": "PROD-004", "name": "Mechanical Keyboard", "price": 129.99, "stock": 200},
    "PROD-005": {"product_id": "PROD-005", "name": "Webcam HD", "price": 89.99, "stock": 100},
}
USERS: Dict[str, dict] = {}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class CreateOrderRequest(BaseModel):
    customer_id: str
    product_id: str
    quantity: int = Field(gt=0)
    idempotency_key: Optional[str] = None


class RegisterRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)
    full_name: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not EMAIL_RE.fullmatch(value):
            raise ValueError("Invalid email format")
        return value


class LoginRequest(BaseModel):
    email: str
    password: str


def issue_mock_jwt(email: str) -> str:
    def segment(value: str) -> str:
        return base64.urlsafe_b64encode(value.encode()).decode().rstrip("=")

    return f'{segment("{\"alg\":\"none\",\"typ\":\"JWT\"}")}.{segment(f"{{\"sub\":\"{email}\",\"type\":\"mock\"}}")}.{segment(uuid.uuid4().hex)}'


def require_auth(authorization: Optional[str] = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer ") or not authorization[7:].strip():
        raise HTTPException(status_code=401, detail="Authentication required")
    return authorization[7:].strip()


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "mock-api", "version": "1.0.0"}


@app.post("/api/v1/auth/register")
async def register(req: RegisterRequest):
    if req.email in USERS:
        raise HTTPException(status_code=409, detail="Email already registered")
    USERS[req.email] = {"email": req.email, "password": req.password, "full_name": req.full_name}
    return {"access_token": issue_mock_jwt(req.email), "token_type": "bearer"}


@app.post("/api/v1/auth/login")
async def login(req: LoginRequest):
    user = USERS.get(req.email)
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": issue_mock_jwt(req.email), "token_type": "bearer"}


@app.post("/api/v1/orders", status_code=201)
async def create_order(req: CreateOrderRequest, _: str = Depends(require_auth)):
    if req.idempotency_key and req.idempotency_key in IDEMPOTENCY:
        return ORDERS[IDEMPOTENCY[req.idempotency_key]]

    product = PRODUCTS.get(req.product_id)
    if not product:
        product = {
            "product_id": req.product_id,
            "name": "Test Product",
            "price": 10.0,
            "stock": 1000,
        }
        PRODUCTS[req.product_id] = product

    now = datetime.utcnow().isoformat()
    order_id = f"ORD-{uuid.uuid4().hex[:6].upper()}"
    order = {
        "order_id": order_id,
        "customer_id": req.customer_id,
        "product_id": req.product_id,
        "quantity": req.quantity,
        "total_amount": product["price"] * req.quantity,
        "status": "pending",
        "created_at": now,
        "updated_at": now,
    }
    ORDERS[order_id] = order
    if req.idempotency_key:
        IDEMPOTENCY[req.idempotency_key] = order_id
    return order


@app.get("/api/v1/orders/{order_id}")
async def get_order(order_id: str, _: str = Depends(require_auth)):
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.get("/api/v1/orders")
async def list_orders(
    page: int = 1,
    page_size: int = 20,
    customer_id: Optional[str] = None,
    _: str = Depends(require_auth),
):
    orders = list(ORDERS.values())
    if customer_id:
        orders = [o for o in orders if o["customer_id"] == customer_id]
    total = len(orders)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": orders[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@app.put("/api/v1/orders/{order_id}/cancel")
async def cancel_order(order_id: str, _: str = Depends(require_auth)):
    order = ORDERS.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order["status"] in ("cancelled", "delivered", "shipped"):
        raise HTTPException(status_code=400, detail=f"Cannot cancel order in '{order['status']}' status")
    order["status"] = "cancelled"
    order["updated_at"] = datetime.utcnow().isoformat()
    return {"order_id": order_id, "status": "cancelled"}


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
            {
                "product_id": p["product_id"],
                "product_name": p["name"],
                "quantity_available": p["stock"],
                "unit_price": p["price"],
            }
            for p in PRODUCTS.values()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
