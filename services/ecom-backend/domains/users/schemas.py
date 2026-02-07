from datetime import datetime

from pydantic import BaseModel

# Output Schemas


class UserData(BaseModel):
    id: int
    first_name: str
    last_name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
