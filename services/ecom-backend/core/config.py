from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_name: str
    model_config = ConfigDict(env_file=".env")


settings = Settings()
