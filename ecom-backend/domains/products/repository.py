from domains.products.models import ProductDB
from sqlalchemy.orm import Session
from abc import ABC, abstractmethod
from core.exceptions import ResourceNotFoundException

class ProductRepository(ABC):

    @abstractmethod
    def get_all(self, page: int, limit: int) -> list[ProductDB]:
        pass
    
    @abstractmethod
    def get(self, product_id: int) -> ProductDB:
        pass

    @abstractmethod
    def create(self, product: ProductDB) -> ProductDB:
        pass

    @abstractmethod
    def update(self, product: ProductDB) -> ProductDB:
        pass

    @abstractmethod
    def delete(self, product_id: int) -> None:
        pass

class SQLAlchemyProductRepository(ProductRepository):

    def __init__(self, db: Session):
        self.db = db

    def get(self, product_id: int) -> ProductDB:

        product = self.db.query(ProductDB).filter(ProductDB.id == product_id).first()
        if not product:
            raise ResourceNotFoundException(f"Product with id {product_id} not found")
        return product

    def get_all(self, page: int, limit: int) -> list[ProductDB]:
        raise NotImplementedError()

    def create(self, product: ProductDB) -> ProductDB:
        raise NotImplementedError()

    def update(self, product: ProductDB) -> ProductDB:
        raise NotImplementedError()

    def delete(self, product_id: int) -> None:
        raise NotImplementedError()
    
