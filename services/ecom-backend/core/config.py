from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_name: str = Field(..., validation_alias="ECOM_BACKEND_DB_NAME")


settings = Settings()
