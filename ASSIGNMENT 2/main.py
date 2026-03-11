from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# Temporary data
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

orders = []
feedback = []


# Pydantic models
class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=20)


class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)


class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=100)
    contact_email: str = Field(..., min_length=5, max_length=100)
    items: List[OrderItem] = Field(..., min_length=1)


@app.get("/")
def home():
    return {"message": "Welcome to our E-commerce API"}


@app.get("/products")
def get_all_products():
    return {"products": products, "total": len(products)}


# Keep specific /products routes BEFORE /products/{product_id}
@app.get("/products/filter")
def filter_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    max_price: Optional[int] = Query(None, description="Maximum price"),
    min_price: Optional[int] = Query(None, description="Minimum price"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability")
):
    result = products

    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]

    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    return {"filtered_products": result, "count": len(result)}


@app.get("/products/summary")
def product_summary():
    in_stock_products = [p for p in products if p["in_stock"]]
    out_of_stock_products = [p for p in products if not p["in_stock"]]

    most_expensive = max(products, key=lambda p: p["price"])
    cheapest = min(products, key=lambda p: p["price"])
    categories = list(set(p["category"] for p in products))

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_products),
        "out_of_stock_count": len(out_of_stock_products),
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }


@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }
    return {"error": "Product not found"}


@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {"product": product}
    return {"error": "Product not found"}


@app.post("/orders")
def place_order(order: OrderRequest):
    product = next((p for p in products if p["id"] == order.product_id), None)

    if not product:
        return {"error": "Product not found"}

    if not product["in_stock"]:
        return {"error": f"{product['name']} is out of stock"}

    total_price = product["price"] * order.quantity
    order_id = len(orders) + 1

    new_order = {
        "order_id": order_id,
        "customer_name": order.customer_name,
        "product_id": order.product_id,
        "product_name": product["name"],
        "quantity": order.quantity,
        "total_price": total_price,
        "status": "pending"
    }

    orders.append(new_order)

    return {
        "message": "Order placed successfully",
        "order": new_order
    }


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            return {"order": order}
    return {"error": "Order not found"}


@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"
            return {
                "message": "Order confirmed",
                "order": order
            }
    return {"error": "Order not found"}


@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.model_dump())
    return {
        "message": "Feedback submitted successfully",
        "feedback": data.model_dump(),
        "total_feedback": len(feedback)
    }


@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
            continue

        subtotal = product["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }
