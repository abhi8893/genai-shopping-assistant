from core.database import get_db
from fastapi import Depends
from domains.products.repository import SQLAlchemyProductRepository
from domains.products.service import ProductService
from sqlalchemy.orm import Session


def get_sqlalchemy_product_repo(
    db: Session = Depends(get_db),
) -> SQLAlchemyProductRepository:
    return SQLAlchemyProductRepository(db)


def get_product_service(
    repo: SQLAlchemyProductRepository = Depends(get_sqlalchemy_product_repo),
) -> ProductService:
    return ProductService(repo)
