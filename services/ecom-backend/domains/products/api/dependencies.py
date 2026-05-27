from core.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

from domains.products.repository import SQLAlchemyProductRepository
from domains.products.service import ProductService


def get_sqlalchemy_product_repo(
    db: Session = Depends(get_db),
) -> SQLAlchemyProductRepository:
    return SQLAlchemyProductRepository(db)


def get_product_service(
    repo: SQLAlchemyProductRepository = Depends(get_sqlalchemy_product_repo),
) -> ProductService:
    return ProductService(repo)
