from pydantic import BaseModel
from datetime import datetime


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

    class Config:
        from_attributes = True


class CartCreateBody(BaseModel):
    cart_items: list[CartItemCreate]

    class Config:
        from_attributes = True


class CartUpdateBody(BaseModel):
    cart_items: list[CartItemCreate]

    class Config:
        from_attributes = True


class CartItemData(BaseModel):
    id: int
    product_id: int
    quantity: int
    amount: float

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    cart_items: list[CartItemData]

    class Config:
        from_attributes = True
