from pydantic import BaseModel
from datetime import datetime

# Output Schemas


class UserData(BaseModel):
    id: int
    first_name: str
    last_name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
