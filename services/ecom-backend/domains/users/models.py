from core.database import Base
from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

__all__ = ("UserDB",)


class UserDB(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(
        Enum("admin", "user", name="user_role"), nullable=False, server_default="user"
    )
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=text("NOW()"), nullable=False
    )

    carts = relationship("CartDB", back_populates="user")
