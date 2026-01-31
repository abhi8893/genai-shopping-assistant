from fastapi import APIRouter, Depends, Query
from domains.users.schemas import UserData
from domains.users.service import UserService
from domains.users.api.dependencies import get_user_service

router = APIRouter(tags=["users"], prefix="/users")


@router.get("/", response_model=list[UserData])
def get_all_users(
    service: UserService = Depends(get_user_service),
    page: int = Query(1, ge=1, description="Page Number"),
    limit: int = Query(10, ge=1, description="limit"),
):
    return service.get_all(page, limit)


@router.get("/{user_id}", response_model=UserData)
def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    return service.get(user_id)
