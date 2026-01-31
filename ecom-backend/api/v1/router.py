from fastapi import APIRouter
from domains.carts.api.router import router as carts_router
from domains.products.api.router import router as products_router
from domains.users.api.router import router as users_router

api_v1_router = APIRouter()
api_v1_router.include_router(carts_router)
api_v1_router.include_router(products_router)
api_v1_router.include_router(users_router)


@api_v1_router.get("/")
def root():
    return {"message": "Welcome to the E-commerce API", "version": "v1"}
