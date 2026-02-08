from core.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

from domains.carts.repository import SQLAlchemyCartRepository
from domains.carts.service import CartService
from domains.products.repository import SQLAlchemyProductRepository
from domains.products.service import ProductService


def get_sqlalchemy_cart_repo(db: Session = Depends(get_db)) -> SQLAlchemyCartRepository:
    return SQLAlchemyCartRepository(db)


def get_sqlalchemy_product_repo(
    db: Session = Depends(get_db),
) -> SQLAlchemyProductRepository:
    return SQLAlchemyProductRepository(db)


def get_product_service(
    repo: SQLAlchemyProductRepository = Depends(get_sqlalchemy_product_repo),
) -> ProductService:
    return ProductService(repo)


def get_cart_service(
    repo: SQLAlchemyCartRepository = Depends(get_sqlalchemy_cart_repo),
    product_service: ProductService = Depends(get_product_service),
) -> CartService:
    return CartService(repo, product_service)
