from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    port: int = 8080


settings = Settings()
