from pydantic import BaseModel, model_validator


class EmptyProductHierarchyFilterError(Exception):
    pass


class MultipleProductHierarchyFilterError(Exception):
    pass


class ProductHierarchyFilter(BaseModel):
    category_id: int | None = None
    subcategory_id: int | None = None
    product_id: int | None = None

    category_slug: str | None = None
    subcategory_slug: str | None = None
    product_slug: str | None = None

    @model_validator(mode="after")
    def check_only_one_field_provided(self):
        if not any(self.model_dump().values()):
            raise EmptyProductHierarchyFilterError(
                "At least one field must be provided for filter"
            )
        if len([v for v in self.model_dump().values() if v is not None]) > 1:
            raise MultipleProductHierarchyFilterError(
                "Only one field can be provided for filter"
            )
        return self
