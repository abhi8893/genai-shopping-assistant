from pydantic import BaseModel, model_validator


# Input Schemas

# TODO: Make slug creation server side logic (with optional override)
class ProductCreate(BaseModel):
    name: str
    slug: str
    description: str
    price: float
    category_id: int
    subcategory_id: int

    class Config:
        from_attributes = True

class ProductUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    price: float | None = None
    category_id: int | None = None
    subcategory_id: int | None = None

    class Config:
        from_attributes = True

    # validate that atleast one is not None
    @model_validator(mode="after")
    def check_at_least_one_field_provided(self):
        if not any(self.model_dump().values()):
            raise ValueError("At least one field must be provided for update")
        return self



# Output Schemas

class ProductData(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    price: float
    category_id: int
    subcategory_id: int

    class Config:
        from_attributes = True