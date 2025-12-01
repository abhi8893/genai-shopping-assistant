from fastapi import APIRouter
from domains.carts.api.router import router as carts_router
from domains.products.api.router import router as products_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(carts_router)
api_v1_router.include_router(products_router)

@api_v1_router.get("/")
def root():
    return {
        "message": "Welcome to the E-commerce API",
        "version": "v1"
    }

