from fastapi import APIRouter, Depends, Query
from domains.products.service import ProductService
from domains.products.schemas import ProductData
from domains.products.api.dependencies import get_product_service
from domains.products.types import (
    ProductHierarchyFilter,
    EmptyProductHierarchyFilterError,
    MultipleProductHierarchyFilterError,
)
from core.exceptions import ValidationException

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
    category_id: int | None = Query(None),
    subcategory_id: int | None = Query(None),
    product_id: int | None = Query(None),
    category_slug: str | None = Query(None),
    subcategory_slug: str | None = Query(None),
    product_slug: str | None = Query(None),
    keywords: list[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    service: ProductService = Depends(get_product_service),
):
    try:
        hier_filter = ProductHierarchyFilter(
            category_id=category_id,
            subcategory_id=subcategory_id,
            product_id=product_id,
            category_slug=category_slug,
            subcategory_slug=subcategory_slug,
            product_slug=product_slug,
        )
    except EmptyProductHierarchyFilterError:
        hier_filter = None
    except MultipleProductHierarchyFilterError as e:
        raise ValidationException(str(e))
    return service.search(page, limit, hier_filter, keywords=keywords)


@router.get("/id/{product_id}", response_model=ProductData)
def get_by_id(product_id: int, service: ProductService = Depends(get_product_service)):
    return service.get(product_id)


@router.get("/slug/{product_slug}", response_model=ProductData)
def get_by_slug(
    product_slug: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    service: ProductService = Depends(get_product_service),
):
    hierarchy_filter = ProductHierarchyFilter(product_slug=product_slug)
    product = service.get_by_hierarchy(hierarchy_filter, page=page, limit=limit)[0]
    return product


@router.get("/category/id/{category_id}", response_model=list[ProductData])
def get_by_category_id(
    category_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    service: ProductService = Depends(get_product_service),
):
    hierarchy_filter = ProductHierarchyFilter(category_id=category_id)
    return service.get_by_hierarchy(hierarchy_filter, page=page, limit=limit)


@router.get("/subcategory/id/{subcategory_id}", response_model=list[ProductData])
def get_by_subcategory_id(
    subcategory_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    service: ProductService = Depends(get_product_service),
):
    hierarchy_filter = ProductHierarchyFilter(subcategory_id=subcategory_id)
    return service.get_by_hierarchy(hierarchy_filter, page=page, limit=limit)


@router.get("/category/slug/{category_slug}", response_model=list[ProductData])
def get_by_category_slug(
    category_slug: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    service: ProductService = Depends(get_product_service),
):
    hierarchy_filter = ProductHierarchyFilter(category_slug=category_slug)
    return service.get_by_hierarchy(hierarchy_filter, page=page, limit=limit)


@router.get("/subcategory/slug/{subcategory_slug}", response_model=list[ProductData])
def get_by_subcategory_slug(
    subcategory_slug: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    service: ProductService = Depends(get_product_service),
):
    hierarchy_filter = ProductHierarchyFilter(subcategory_slug=subcategory_slug)
    return service.get_by_hierarchy(hierarchy_filter, page=page, limit=limit)
