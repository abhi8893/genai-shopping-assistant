from api.dependencies import get_db
from fastapi import Depends, Header
from sqlalchemy.orm import Session
from domains.users.models import UserDB
from exceptions import UnauthorizedException, ResourceNotFoundException


# TODO: Make it depend on UserService
def get_current_user(db: Session = Depends(get_db), user_id: int | None = Header(default=None, alias="X-User-Id")):
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
    