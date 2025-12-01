from domains.users.repository import UserRepository
from domains.users.schemas import UserData

class UserService:

    def __init__(self, repo: UserRepository):
        self.repo = repo

    def get(self, user_id: int) -> UserData:
        user_db = self.repo.get(user_id)
        return UserData.model_validate(user_db)

    def get_all(self, page: int, limit: int) -> list[UserData]:
        user_db_list = self.repo.get_all(page, limit)
        return [UserData.model_validate(user_db) for user_db in user_db_list]

    