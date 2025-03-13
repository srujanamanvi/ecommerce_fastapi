from fastapi import Depends
from sqlalchemy.orm import Session
from typing import List
import logging

from app import schemas, exception
from app.settings.production import get_db
from app.models import Product

logger = logging.getLogger(__name__)


def get_products(db: Session = Depends(get_db)) -> List[schemas.Product]:
    """
    Retrieve all products from the database.
    """
    return db.query(Product).all()


def get_product(product_id: int, db: Session = Depends(get_db)) -> schemas.Product:
    """
    Retrieve a specific product by ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise exception.ProductNotFoundError(product_id)
    return product


def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)) -> schemas.Product:
    """
    Create a new product.
    """
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product
