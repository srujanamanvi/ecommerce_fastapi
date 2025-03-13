from fastapi import APIRouter, status
from typing import List

from app import schemas
from app import views

router = APIRouter()

# ------------------ Products Routes ------------------

router.add_api_route("/products/", views.products.get_products, methods=["GET"], response_model=List[schemas.Product])
router.add_api_route("/products/{product_id}", views.products.get_product, methods=["GET"], response_model=schemas.Product)
router.add_api_route("/products/", views.products.create_product, methods=["POST"], response_model=schemas.Product, status_code=status.HTTP_201_CREATED)

# ------------------ Orders Routes ------------------

router.add_api_route("/orders/", views.orders.get_orders, methods=["GET"], response_model=List[schemas.Order])
router.add_api_route("/orders/{order_id}", views.orders.get_order, methods=["GET"], response_model=schemas.Order)
router.add_api_route("/orders/", views.orders.create_order, methods=["POST"], response_model=schemas.Order, status_code=status.HTTP_201_CREATED)
