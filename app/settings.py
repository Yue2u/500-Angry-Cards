from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str
    NATS_URL: str
    DB_URL: str


settings = Settings()
