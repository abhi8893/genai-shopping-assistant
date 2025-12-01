from domains.products.models import ProductDB
from sqlalchemy.orm import Session
from abc import ABC, abstractmethod
from core.exceptions import ResourceNotFoundException
import sqlalchemy
from sqlalchemy import func as sql_func


class ProductHierarchyFilter:
    category_id: int
    subcategory_id: int

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
    
    @abstractmethod
    def search(self, page: int, limit: int, category_id: int | None = None, subcategory_id: int | None = None, keywords: list[str] = None) -> list[ProductDB]:
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
        products = self.db.query(ProductDB).offset((page - 1) * limit).limit(limit).all()
        
        # TODO: A better exception type that tells that pages have been exhausted
        if not products:
            raise ResourceNotFoundException("No products found")
        return products

    def _get_hierarchy_filter(self, category_id: int | None = None, subcategory_id: int | None = None) -> sqlalchemy.sql.expression.BinaryExpression:
        hierarchy_filters = []
        if category_id is not None:
            hierarchy_filters.append(ProductDB.product_hierarchy.category_id == category_id)
        if subcategory_id is not None:
            hierarchy_filters.append(ProductDB.product_hierarchy.subcategory_id == subcategory_id)

        if hierarchy_filters:
            hierarchy_filter = sqlalchemy.and_(*hierarchy_filters)
        else:
            hierarchy_filter = sqlalchemy.true()
        return hierarchy_filter

    def _get_keyword_filter(self, keywords: list[str] = None) -> sqlalchemy.sql.expression.BinaryExpression:
        keyword_filters = []
        if keywords is not None:
            for keyword in keywords:
                keyword = keyword.lower()
                keyword_filters.append(sql_func.lower(ProductDB.name).contains(keyword))
                keyword_filters.append(sql_func.lower(ProductDB.description).contains(keyword))

        keyword_filter = sqlalchemy.or_(*keyword_filters)

        return keyword_filter

    def search(self, page: int, limit: int, category_id: int | None = None, subcategory_id: int | None = None, keywords: list[str] = None) -> list[ProductDB]:

        # Build hierarchy filters
        hierarchy_filter = self._get_hierarchy_filter(category_id, subcategory_id)

        # Build keyword filters
        keyword_filter = self._get_keyword_filter(keywords)
        
        products = (
            self.db.query(ProductDB)
            .filter(hierarchy_filter)
            .filter(keyword_filter)
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        
        # TODO: A better exception type that tells that pages have been exhausted
        if not products:
            raise ResourceNotFoundException("No products found")
        return products

    def create(self, product: ProductDB) -> ProductDB:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
        

    def update(self, product: ProductDB) -> ProductDB:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product_id: int) -> None:
        self.db.query(ProductDB).filter(ProductDB.id == product_id).delete()
        self.db.commit()
    
