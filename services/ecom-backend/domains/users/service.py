from core.exceptions import ResourceNotFoundException

from domains.users.models import UserDB
from domains.users.repository import UserRepository
from domains.users.schemas import UserCreate, UserData


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def create(self, user_in: UserCreate) -> UserData:
        user_db = UserDB(
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            role=user_in.role.value,  # Convert enum to raw string for DB storage
        )
        user_db = self.repo.create(user_db)
        return UserData.model_validate(user_db)

    def get(self, user_id: int) -> UserData:
        user_db = self.repo.get(user_id)
        if user_db is None:
            raise ResourceNotFoundException(message=f"User with ID {user_id} not found")
        return UserData.model_validate(user_db)

    def get_all(self, page: int, limit: int) -> list[UserData]:
        user_db_list = self.repo.get_all(page, limit)
        return [UserData.model_validate(user_db) for user_db in user_db_list]

    def delete(self, user_id: int) -> UserData:
        user = self.get(user_id)
        self.repo.delete(user_id)
        return user
