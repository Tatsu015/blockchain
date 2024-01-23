from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    repository_dir: str = "aaa"


settings = Settings()
