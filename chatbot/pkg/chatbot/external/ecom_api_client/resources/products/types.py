from pydantic import BaseModel

class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    price: float
    category_id: int
    subcategory_id: int

    class Config:
        from_attributes = True