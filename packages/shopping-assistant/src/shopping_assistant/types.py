from pydantic import BaseModel, ConfigDict


class ProductVectorDBRecord(BaseModel):
    product_id: int
    name: str
    slug: str
    description: str
    category_name: str
    subcategory_name: str
    category_slug: str
    subcategory_slug: str
    price: float
    created_at: str


class CartItem(BaseModel):
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)
