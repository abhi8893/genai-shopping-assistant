from pydantic import BaseModel


class Product(BaseModel):
    product_id: int
    name: str
    description: str
    category: str
    subcategory: str
    price: float


class CartItem(BaseModel):
    product_id: int
    quantity: int

    class Config:
        from_attributes = True