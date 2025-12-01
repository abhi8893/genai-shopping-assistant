from pydantic import BaseModel


# Output Schemas

class ProductData(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category_id: int
    subcategory_id: int

    class Config:
        from_attributes = True