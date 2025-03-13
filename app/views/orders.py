from fastapi import Depends
from sqlalchemy.orm import Session
from typing import List

from app import schemas, exception
from app.settings.production import get_db
from app.models import Product, Order, OrderProduct
from sqlalchemy.orm import joinedload
from app.cache import order_cache


def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)) -> schemas.Order:
    """
    Create a new order with stock validation.
    # TODO: Move the logic to a service layer - ex: order_service
    """
    # Get products and validate they exist
    product_ids = [item.product_id for item in order.products]
    products_map = get_products_by_ids(db, product_ids)

    # Create order record
    db_order = create_order_record(db)

    # Process ordered items and calculate total
    total_price, order_products = process_order_items(db_order.id, order.products, products_map, db)

    # Update order with final price and commit
    finalize_order(db_order, total_price, db)

    # Return formatted response
    return format_order_response(db_order)


def get_products_by_ids(db: Session, product_ids: list[int]) -> dict:
    """Fetch products by IDs and validate all exist"""
    products_map = {
        p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()
    }

    # Check for missing products
    missing_ids = set(product_ids) - set(products_map.keys())
    if missing_ids:
        raise exception.ProductNotFoundError(list(missing_ids)[0])

    return products_map


def create_order_record(db: Session) -> Order:
    """Create initial order record"""
    db_order = Order(status="pending", total_price=0.0)
    db.add(db_order)
    db.flush()  # Get order ID
    return db_order


def process_order_items(order_id: int, items: list[schemas.OrderProductItem],
                        products_map: dict, db: Session) -> tuple[float, list]:
    """Process each ordered item, validate stock, and create order products"""
    total_price = 0.0
    order_products_objects = []

    for item in items:
        product = products_map[item.product_id]
        validate_product_stock(product, item.quantity)

        # Calculate price and update stock
        item_price = product.price * item.quantity
        total_price += item_price
        product.stock -= item.quantity

        # Create OrderProduct object
        order_product = OrderProduct(
            order_id=order_id,
            product_id=product.id,
            quantity=item.quantity
        )
        order_products_objects.append(order_product)

    # Bulk insert order products
    db.bulk_save_objects(order_products_objects)

    return total_price, order_products_objects


def validate_product_stock(product: Product, requested_quantity: int) -> None:
    """Validate product has sufficient stock"""
    if product.stock < requested_quantity:
        raise exception.InsufficientStockError(
            product_id=product.id,
            available=product.stock,
            requested=requested_quantity
        )


def finalize_order(order: Order, total_price: float, db: Session) -> None:
    """Update order with total price and commit transaction"""
    order.total_price = total_price
    db.commit()
    db.refresh(order)


def format_order_response(order: Order) -> schemas.Order:
    """Convert DB order to response schema"""
    return schemas.Order(
        id=order.id,
        total_price=order.total_price,
        status=order.status,
        products=[
            schemas.OrderProductItem(
                product_id=op.product_id,
                quantity=op.quantity
            )
            for op in order.order_products
        ]
    )

def get_orders(db: Session = Depends(get_db)) -> List[schemas.Order]:
    """
    Get all orders with their products.
    """
    # Try to get from cache first
    cache_key = "orders_list" # can we user specific based on the need
    cached_orders = order_cache.get(cache_key)

    if cached_orders:
        print("Returning from cache")
        return cached_orders

    print("fetching from database")
    # Fetch all orders with their order products in a single query
    orders = db.query(Order).options(
        joinedload(Order.order_products)
    ).all()

    # Convert to response schema
    result = [
        schemas.Order(
            id=order.id,
            total_price=order.total_price,
            status=order.status,
            products=[
                schemas.OrderProductItem(
                    product_id=op.product_id,
                    quantity=op.quantity
                )
                for op in order.order_products
            ]
        )
        for order in orders
    ]

    order_cache.set(cache_key, result)

    return result


def get_order(order_id: int, db: Session = Depends(get_db)) -> schemas.Order:
    """
    Get a specific order by ID with its products.
    """
    cache_key = f"order_{order_id}"
    cached_order = order_cache.get(cache_key)

    if cached_order:
        # Invalidate the cache if and when order_id is updated to avoid returning stale data
        return cached_order

    # Fetch the order with its order products in a single query
    order = db.query(Order).options(
        joinedload(Order.order_products)
    ).filter(Order.id == order_id).first()

    if not order:
        raise exception.OrderNotFoundError(order_id)

    # Convert to response schema
    result = schemas.Order(
        id=order.id,
        total_price=order.total_price,
        status=order.status,
        products=[
            schemas.OrderProductItem(
                product_id=op.product_id,
                quantity=op.quantity
            )
            for op in order.order_products
        ]
    )
    order_cache.set(cache_key, result)
    return result
