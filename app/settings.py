from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    NATS_URL: str
    DB_URL: str


settings = Settings()
