from abc import ABC, abstractmethod

import sqlalchemy
from core.exceptions import ResourceNotFoundException
from sqlalchemy import func as sql_func
from sqlalchemy.orm import Session

from domains.products.models import ProductDB
from domains.products.types import ProductHierarchyFilter


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
    def get_by_hierarchy(
        self, hierarchy_filter: ProductHierarchyFilter
    ) -> list[ProductDB]:
        pass

    @abstractmethod
    def search(
        self,
        page: int,
        limit: int,
        hierarchy_filter: ProductHierarchyFilter,
        keywords: list[str] | None = None,
    ) -> list[ProductDB]:
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
        products = (
            self.db.query(ProductDB).offset((page - 1) * limit).limit(limit).all()
        )

        # TODO: A better exception type that tells that pages have been exhausted
        if not products:
            raise ResourceNotFoundException("No products found")
        return products

    def _get_hierarchy_sql_filter(
        self, hierarchy_filter: ProductHierarchyFilter
    ) -> sqlalchemy.sql.expression.BinaryExpression:
        prod_table_fields = {
            "category_id": "category_id",
            "subcategory_id": "subcategory_id",
            "product_id": "id",
            "product_slug": "slug",
        }
        hier_table_fields = {
            "category_slug": "category_slug",
            "subcategory_slug": "subcategory_slug",
        }
        hierarchy_filters = []

        for filter_name, filter_value in hierarchy_filter.model_dump(
            exclude_unset=True
        ).items():
            if filter_value is not None:
                if filter_name in prod_table_fields:
                    f = getattr(ProductDB, prod_table_fields[filter_name])
                    hierarchy_filters.append(f == filter_value)
                elif filter_name in hier_table_fields:
                    kwargs = {hier_table_fields[filter_name]: filter_value}
                    hierarchy_filters.append(ProductDB.product_hierarchy.has(**kwargs))

        hierarchy_filter = sqlalchemy.and_(*hierarchy_filters)
        return hierarchy_filter

    def _get_keyword_filter(
        self, keywords: list[str] = None
    ) -> sqlalchemy.sql.expression.BinaryExpression:
        keyword_filters = []
        if keywords is not None:
            for keyword in keywords:
                keyword_lower = keyword.lower()
                keyword_filters.append(
                    sql_func.lower(ProductDB.name).contains(keyword_lower)
                )
                keyword_filters.append(
                    sql_func.lower(ProductDB.description).contains(keyword_lower)
                )

        keyword_filter = sqlalchemy.or_(*keyword_filters)

        return keyword_filter

    def get_by_hierarchy(
        self, hierarchy_filter: ProductHierarchyFilter, page: int, limit: int
    ) -> list[ProductDB]:
        hierarchy_filter = self._get_hierarchy_sql_filter(hierarchy_filter)
        products = (
            self.db.query(ProductDB)
            .filter(hierarchy_filter)
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        if not products:
            raise ResourceNotFoundException("No products found matching the criteria")

        return products

    def search(
        self,
        page: int,
        limit: int,
        hierarchy_filter: ProductHierarchyFilter | None = None,
        keywords: list[str] = None,
    ) -> list[ProductDB]:
        # Build hierarchy filters
        if hierarchy_filter is not None:
            hierarchy_filter = self._get_hierarchy_sql_filter(hierarchy_filter)
        else:
            hierarchy_filter = sqlalchemy.true()

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
