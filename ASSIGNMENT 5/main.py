from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# ---------------------------------------------------
# Temporary data (acts like a database)
# ---------------------------------------------------
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

orders = []


# ---------------------------------------------------
# Pydantic model for creating orders
# ---------------------------------------------------
class OrderCreate(BaseModel):
    customer_name: str
    product_id: int
    quantity: int


# ---------------------------------------------------
# Home endpoint
# ---------------------------------------------------
@app.get("/")
def home():
    return {"message": "Welcome to our E-commerce API"}


# ---------------------------------------------------
# Get all products
# ---------------------------------------------------
@app.get("/products")
def get_all_products():
    return {
        "products": products,
        "total": len(products)
    }


# ---------------------------------------------------
# Search products by keyword
# ---------------------------------------------------
@app.get("/products/search")
def search_products(keyword: str = Query(...)):
    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not results:
        return {"message": f"No products found for: {keyword}"}

    return {
        "keyword": keyword,
        "total_found": len(results),
        "products": results
    }


# ---------------------------------------------------
# Sort products
# ---------------------------------------------------
@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price"),
    order: str = Query("asc")
):
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    if order not in ["asc", "desc"]:
        return {"error": "order must be 'asc' or 'desc'"}

    sorted_products = sorted(
        products,
        key=lambda p: p[sort_by],
        reverse=(order == "desc")
    )

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }


# ---------------------------------------------------
# Pagination for products
# ---------------------------------------------------
@app.get("/products/page")
def get_products_page(
    page: int = Query(1, ge=1),
    limit: int = Query(2, ge=1)
):
    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total_products": len(products),
        "total_pages": -(-len(products) // limit),
        "products": products[start:end]
    }


# ---------------------------------------------------
# Q5 - Sort by category then price
# ---------------------------------------------------
@app.get("/products/sort-by-category")
def sort_by_category():
    result = sorted(products, key=lambda p: (p["category"], p["price"]))

    return {
        "products": result,
        "total": len(result)
    }


# ---------------------------------------------------
# Q6 - Search + Sort + Paginate in one endpoint
# ---------------------------------------------------
@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = Query(None),
    sort_by: str = Query("price"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=20)
):
    result = products

    # Step 1: Search
    if keyword:
        result = [
            p for p in result
            if keyword.lower() in p["name"].lower()
        ]

    # Step 2: Sort
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    if order not in ["asc", "desc"]:
        return {"error": "order must be 'asc' or 'desc'"}

    result = sorted(
        result,
        key=lambda p: p[sort_by],
        reverse=(order == "desc")
    )

    # Step 3: Pagination
    total = len(result)
    start = (page - 1) * limit
    paged = result[start:start + limit]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": -(-total // limit) if total > 0 else 0,
        "products": paged
    }


# ---------------------------------------------------
# Get product by ID
# Keep this below custom /products/... routes
# ---------------------------------------------------
@app.get("/products/{product_id}")
def get_product_by_id(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {"product": product}

    raise HTTPException(status_code=404, detail="Product not found")


# ---------------------------------------------------
# Place a new order
# ---------------------------------------------------
@app.post("/orders")
def create_order(order: OrderCreate):
    # Check if product exists
    selected_product = None
    for product in products:
        if product["id"] == order.product_id:
            selected_product = product
            break

    if not selected_product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_order = {
        "order_id": len(orders) + 1,
        "customer_name": order.customer_name,
        "product_id": order.product_id,
        "product_name": selected_product["name"],
        "quantity": order.quantity,
        "total_price": selected_product["price"] * order.quantity
    }

    orders.append(new_order)

    return {
        "message": "Order placed successfully",
        "order": new_order
    }


# ---------------------------------------------------
# Get all orders
# ---------------------------------------------------
@app.get("/orders")
def get_all_orders():
    return {
        "orders": orders,
        "total": len(orders)
    }


# ---------------------------------------------------
# Q4 - Search orders by customer name
# ---------------------------------------------------
@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):
    results = [
        o for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]

    if not results:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(results),
        "orders": results
    }


# ---------------------------------------------------
# Bonus - Paginate orders
# ---------------------------------------------------
@app.get("/orders/page")
def get_orders_paged(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20)
):
    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total": len(orders),
        "total_pages": -(-len(orders) // limit) if len(orders) > 0 else 0,
        "orders": orders[start:end]
    }
