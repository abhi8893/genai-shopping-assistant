from domains.products.repository import SQLAlchemyProductRepository
from domains.products.schemas import ProductData, ProductCreate, ProductUpdate
from domains.products.models import ProductDB

class ProductService:

    def __init__(self, repo: SQLAlchemyProductRepository):
        self.repo = repo

    def get(self, product_id: int) -> ProductData:
        return ProductData.model_validate(self.repo.get(product_id))

    def get_all(self, page: int, limit: int) -> list[ProductData]:
        return [ProductData.model_validate(product_db) for product_db in self.repo.get_all(page, limit)]

    def search(self, page: int, limit: int, category_id: int | None = None, subcategory_id: int | None = None, keywords: list[str] | None = None) -> list[ProductData]:
        return [ProductData.model_validate(product_db) for product_db in self.repo.search(page, limit, category_id=category_id, subcategory_id=subcategory_id, keywords=keywords)]

    def create(self, product_create_data: ProductCreate)-> ProductData:
        product_db = ProductDB(**product_create_data.model_dump())
        product_db = self.repo.create(product_db)
        return ProductData.model_validate(product_db)

    def update(self, product_id: int, product_update_data: ProductUpdate)-> ProductData:
        product_db = self.repo.get(product_id)
        product_update_dict = product_update_data.model_dump(exclude_unset=True)

        for k, v in product_update_dict.items():
            setattr(product_db, k, v)
        
        product_db = self.repo.update(product_db)
        return ProductData.model_validate(product_db)

    def delete(self, product_id: int) -> None:
        self.repo.delete(product_id)

        
