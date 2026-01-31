from pydantic import BaseModel


class Credentials(BaseModel):
    user_id: int | None = None
