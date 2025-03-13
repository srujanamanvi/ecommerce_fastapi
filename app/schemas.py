from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"


class ProductBase(BaseModel):
    name: str
    description: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class OrderProductItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    products: List[OrderProductItem]

    @field_validator("products")
    @classmethod
    def must_have_products(cls, v):
        if not v:
            raise ValueError('Order must contain at least one product')
        return v


class Order(BaseModel):
    id: int
    products: List[OrderProductItem]
    total_price: float
    status: OrderStatus

    model_config = ConfigDict(from_attributes=True)


class OrderProductBase(BaseModel):
    order_id: int
    product_id: int
    quantity: int


class OrderProductCreate(OrderProductBase):
    pass


class OrderProduct(OrderProductBase):
    model_config = ConfigDict(from_attributes=True)
