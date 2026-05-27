from fastapi import APIRouter, Depends, Query, status

from domains.users.api.dependencies import get_current_admin_user, get_user_service
from domains.users.schemas import UserCreate, UserData
from domains.users.service import UserService

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


# Create a user
@router.post(
    "/",
    response_model=UserData,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin_user)],
)
def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    return service.create(user)


# Delete a user
@router.delete(
    "/{user_id}",
    response_model=UserData,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_admin_user)],
)
def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    return service.delete(user_id)
