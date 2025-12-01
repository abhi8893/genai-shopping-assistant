from domains.products.repository import SQLAlchemyProductRepository
from domains.products.schemas import ProductData

class ProductService:

    def __init__(self, repo: SQLAlchemyProductRepository):
        self.repo = repo

    def get(self, product_id: int) -> ProductData:
        return ProductData.model_validate(self.repo.get(product_id))