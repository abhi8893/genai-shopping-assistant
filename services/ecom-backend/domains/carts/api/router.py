from fastapi import APIRouter, status, Depends, Query
from domains.carts.schemas import CartData, CartCreate, CartUpdate
from domains.carts.service import CartService
from domains.carts.api.dependencies import get_cart_service
from domains.users.api.dependencies import get_current_user
from domains.users.models import UserDB

router = APIRouter(tags=["carts"], prefix="/carts")


@router.get("/", response_model=list[CartData], status_code=status.HTTP_200_OK)
def get_all_carts(
    user: UserDB = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
    page: int = Query(1, ge=1, le=100, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
):
    return service.get_all(user.id, page, limit)


@router.get(
    "/{cart_id}",
    response_model=CartData,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
def get_cart(
    cart_id: int,
    service: CartService = Depends(get_cart_service),
):
    return service.get(cart_id)


@router.post("/", response_model=CartData, status_code=status.HTTP_201_CREATED)
def create_cart(
    cart: CartCreate,
    user: UserDB = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service),
):
    return cart_service.create(cart, user.id)


@router.delete(
    "/{cart_id}",
    response_model=CartData,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
def delete_cart(
    cart_id: int,
    service: CartService = Depends(get_cart_service),
):
    return service.delete(cart_id)


@router.put(
    "/{cart_id}",
    response_model=CartData,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
def update_cart(
    cart_id: int, cart: CartUpdate, service: CartService = Depends(get_cart_service)
):
    return service.update(cart, cart_id)
