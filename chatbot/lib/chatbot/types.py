from pydantic import BaseModel


class Product(BaseModel):
    product_id: int
    name: str
    description: str
    category: str
    subcategory: str
    price: float
