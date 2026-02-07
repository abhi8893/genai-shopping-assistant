"""DTOs"""

from datetime import datetime

from pydantic import BaseModel

# TODO: Keeping the service layer schemas and API layer schemas same (for now).
# Need to add clear separation later (Add api/schemas.py => request/response objects)

# Input Schemas


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

    class Config:
        from_attributes = True


class CartCreate(BaseModel):
    cart_items: list[CartItemCreate]

    class Config:
        from_attributes = True


class CartUpdate(BaseModel):
    cart_items: list[CartItemCreate]

    class Config:
        from_attributes = True


# Output Schemas


class CartItemData(BaseModel):
    id: int
    product_id: int
    quantity: int
    amount: float

    class Config:
        from_attributes = True


class CartData(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    cart_items: list[CartItemData]

    class Config:
        from_attributes = True
