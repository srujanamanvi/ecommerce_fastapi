from fastapi import HTTPException, status


class InsufficientStockError(HTTPException):
    def __init__(self, product_id: int, available: int, requested: int):
        self.product_id = product_id
        self.available = available
        self.requested = requested
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock for product id {product_id}: {available} available, {requested} requested"
        )


class ProductNotFoundError(HTTPException):
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )


class OrderNotFoundError(HTTPException):
    def __init__(self, order_id: int):
        self.order_id = order_id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )
