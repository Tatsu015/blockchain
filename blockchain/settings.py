from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cache_dir: str = "aaa"


settings = Settings()
