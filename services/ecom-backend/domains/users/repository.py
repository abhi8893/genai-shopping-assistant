from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from domains.users.models import UserDB


class UserRepository(ABC):
    @abstractmethod
    def create(self, user: UserDB) -> UserDB:
        pass

    @abstractmethod
    def get(self, user_id: int) -> UserDB:
        pass

    @abstractmethod
    def get_all(self, page: int, limit: int) -> list[UserDB]:
        pass


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, user: UserDB) -> UserDB:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get(self, user_id: int) -> UserDB:
        return self.db.query(UserDB).filter(UserDB.id == user_id).first()

    def get_all(self, page: int, limit: int) -> list[UserDB]:
        return self.db.query(UserDB).offset((page - 1) * limit).limit(limit).all()
