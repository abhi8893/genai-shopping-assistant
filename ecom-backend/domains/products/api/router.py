from fastapi import APIRouter, Depends, Query
from domains.products.service import ProductService
from domains.products.schemas import ProductData
from domains.products.api.dependencies import get_product_service


router = APIRouter(tags=["products"], prefix="/products")

@router.get("/", response_model=list[ProductData])
def get_all_products(
    service: ProductService = Depends(get_product_service),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, description="Limit"),
):
    return service.get_all(page, limit)


@router.get("/search", response_model=list[ProductData])
def search(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    category_id: int = Query(None),
    subcategory_id: int = Query(None),
    keywords: list[str] = Query(None),
    service: ProductService = Depends(get_product_service)
):
    return service.search(
        page, limit,
        category_id=category_id,
        subcategory_id=subcategory_id,
        keywords=keywords
    )


@router.get("/{product_id}", response_model=ProductData)
def get(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    return service.get(product_id)
