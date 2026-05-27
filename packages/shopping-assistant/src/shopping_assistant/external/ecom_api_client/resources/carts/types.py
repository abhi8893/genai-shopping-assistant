from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class CartCreateBody(BaseModel):
    cart_items: list[CartItemCreate]

    model_config = ConfigDict(from_attributes=True)


class CartUpdateBody(BaseModel):
    cart_items: list[CartItemCreate]

    model_config = ConfigDict(from_attributes=True)


class CartItemData(BaseModel):
    id: int
    product_id: int
    quantity: int
    amount: float

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    cart_items: list[CartItemData]

    model_config = ConfigDict(from_attributes=True)
