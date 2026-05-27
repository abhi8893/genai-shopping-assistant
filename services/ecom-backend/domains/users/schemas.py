from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"


# Input Schemas
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    role: UserRole


# Output Schemas
class UserData(BaseModel):
    id: int
    first_name: str
    last_name: str
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
