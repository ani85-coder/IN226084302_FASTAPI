from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()


# -----------------------------
# Temporary data (acts like DB)
# -----------------------------
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

cart = []
orders = []
next_order_id = 1


# -----------------------------
# Pydantic models
# -----------------------------
class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str


# -----------------------------
# Helper functions
# -----------------------------
def find_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def find_cart_item(product_id: int):
    for item in cart:
        if item["product_id"] == product_id:
            return item
    return None


def calculate_grand_total():
    return sum(item["subtotal"] for item in cart)


# -----------------------------
# Basic endpoints
# -----------------------------
@app.get("/")
def home():
    return {"message": "Welcome to our E-commerce API"}


@app.get("/products")
def get_all_products():
    return {"products": products, "total_products": len(products)}


# -----------------------------
# Cart endpoints
# -----------------------------
@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(
            status_code=400,
            detail=f'{product["name"]} is out of stock'
        )

    existing_item = find_cart_item(product_id)

    if existing_item:
        existing_item["quantity"] += quantity
        existing_item["subtotal"] = existing_item["quantity"] * existing_item["unit_price"]
        return {
            "message": "Cart updated",
            "cart_item": existing_item
        }

    cart_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": product["price"] * quantity
    }
    cart.append(cart_item)

    return {
        "message": "Added to cart",
        "cart_item": cart_item
    }


@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty"}

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": calculate_grand_total()
    }


@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {
                "message": f'{item["product_name"]} removed from cart',
                "cart": cart,
                "item_count": len(cart),
                "grand_total": calculate_grand_total()
            }

    raise HTTPException(status_code=404, detail="Item not found in cart")


# -----------------------------
# Checkout and orders
# -----------------------------
@app.post("/cart/checkout")
def checkout(order_data: CheckoutRequest):
    global next_order_id

    if not cart:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty — add items first"
        )

    grand_total = calculate_grand_total()
    orders_placed = []

    for item in cart:
        order = {
            "order_id": next_order_id,
            "customer_name": order_data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"],
            "delivery_address": order_data.delivery_address
        }
        orders.append(order)
        orders_placed.append(order)
        next_order_id += 1

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders_placed": orders_placed,
        "grand_total": grand_total
    }


@app.get("/orders")
def get_orders():
    return {
        "orders": orders,
        "total_orders": len(orders)
    }
