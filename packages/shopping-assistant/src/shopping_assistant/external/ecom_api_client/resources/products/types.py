from pydantic import BaseModel, ConfigDict


class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    price: float
    category_id: int
    subcategory_id: int

    model_config = ConfigDict(from_attributes=True)
