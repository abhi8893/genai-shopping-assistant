from core.database import get_db
from core.exceptions import (
    ForbiddenException,
    ResourceNotFoundException,
    UnauthorizedException,
)
from fastapi import Depends, Header
from sqlalchemy.orm import Session

from domains.users.models import UserDB
from domains.users.repository import SQLAlchemyUserRepository
from domains.users.schemas import UserRole
from domains.users.service import UserService


# TODO: Make it depend on UserService
def get_current_user(
    db: Session = Depends(get_db),
    user_id: int | None = Header(default=None, alias="X-User-Id"),
):
    """
    Temporary simplified auth:
    Reads user id from header: X-User-Id: <int>
    """

    if user_id is None:
        raise UnauthorizedException(message="X-User-Id header is missing")

    # This should be service.get(user_id)
    user = db.query(UserDB).filter(UserDB.id == user_id).first()

    if user is None:
        raise ResourceNotFoundException(message="User not found")

    return user


def get_current_admin_user(
    current_user: UserDB = Depends(get_current_user),
) -> UserDB:
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException(message="Only administrators can perform this action")
    return current_user


def get_sqlalchemy_user_repo(db: Session = Depends(get_db)) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(db)


def get_user_service(
    repo: SQLAlchemyUserRepository = Depends(get_sqlalchemy_user_repo),
) -> UserService:
    return UserService(repo)
