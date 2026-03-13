from fastapi import FastAPI, Response, status, Query
from pydantic import BaseModel

app = FastAPI()

# Temporary database
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook', 'price': 99, 'category': 'Stationery', 'in_stock': True},
    {'id': 3, 'name': 'USB Hub', 'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set', 'price': 49, 'category': 'Stationery', 'in_stock': True},
]


# Pydantic model for adding a new product
class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True


# Helper function
def find_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return product
    return None


# Home
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}


# Get all products
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}


# Add product
@app.post('/products')
def add_product(new_product: NewProduct, response: Response):
    # duplicate name check
    for product in products:
        if product['name'].lower() == new_product.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {'error': 'Product with this name already exists'}

    next_id = max(p['id'] for p in products) + 1 if products else 1

    product_dict = {
        'id': next_id,
        'name': new_product.name,
        'price': new_product.price,
        'category': new_product.category,
        'in_stock': new_product.in_stock
    }

    products.append(product_dict)
    response.status_code = status.HTTP_201_CREATED
    return {'message': 'Product added', 'product': product_dict}
#audit
@app.get('/products/audit')
def product_audit():
    in_stock_list = [p for p in products if p['in_stock']]
    out_stock_list = [p for p in products if not p['in_stock']]
    stock_value = sum(p['price'] * 10 for p in in_stock_list)
    priciest = max(products, key=lambda p: p['price'])

    return {
    'total_products': len(products),
    'in_stock_count': len(in_stock_list),
    'out_of_stock_names': [p['name'] for p in out_stock_list],
    'total_stock_value': stock_value,
    'most_expensive': {
        'name': priciest['name'],
        'price': priciest['price']
    }
}

#discount
@app.put('/products/discount')
def bulk_discount(
    category: str,
    discount_percent: int
):
    updated = []

    for p in products:
        if p['category'] == category:
            p['price'] = int(p['price'] * (1 - discount_percent / 100))
            updated.append(p)

    if not updated:
        return {'message': f'No products found in category: {category}'}

    return {
        'message': f'{discount_percent}% discount applied to {category}',
        'updated_count': len(updated),
        'updated_products': updated
    }
# Update product
@app.put('/products/{product_id}')
def update_product(
    product_id: int,
    response: Response,
    price: int | None = None,
    in_stock: bool | None = None
):
    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}

    if price is not None:
        product['price'] = price

    if in_stock is not None:
        product['in_stock'] = in_stock

    return {'message': 'Product updated', 'product': product}


# Delete product
@app.delete('/products/{product_id}')
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}

    products.remove(product)
    return {'message': f"Product '{product['name']}' deleted"}


# Q5: audit route
# IMPORTANT: keep this ABOVE /products/{product_id}
@app.get('/products/audit')
def product_audit():
    in_stock_list = [p for p in products if p['in_stock']]
    out_stock_list = [p for p in products if not p['in_stock']]
    stock_value = sum(p['price'] * 10 for p in in_stock_list)
    priciest = max(products, key=lambda p: p['price'])

    return {
        'total_products': len(products),
        'in_stock_count': len(in_stock_list),
        'out_of_stock_names': [p['name'] for p in out_stock_list],
        'total_stock_value': stock_value,
        'most_expensive': {
            'name': priciest['name'],
            'price': priciest['price']
        }
    }


# Bonus: discount route
# IMPORTANT: keep this ABOVE /products/{product_id}
@app.put('/products/discount')
def bulk_discount(
    category: str = Query(..., description='Category to discount'),
    discount_percent: int = Query(..., ge=1, le=99, description='Discount percentage')
):
    updated = []

    for p in products:
        if p['category'].lower() == category.lower():
            p['price'] = int(p['price'] * (1 - discount_percent / 100))
            updated.append(p)

    if not updated:
        return {'message': f'No products found in category: {category}'}

    return {
        'message': f'{discount_percent}% discount applied to {category}',
        'updated_count': len(updated),
        'updated_products': updated
    }


# Get single product
@app.get('/products/{product_id}')
def get_product(product_id: int, response: Response):
    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}

    return product
