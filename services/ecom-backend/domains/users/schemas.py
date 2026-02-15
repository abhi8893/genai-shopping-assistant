from datetime import datetime

from pydantic import BaseModel, ConfigDict

# Output Schemas


class UserData(BaseModel):
    id: int
    first_name: str
    last_name: str
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
