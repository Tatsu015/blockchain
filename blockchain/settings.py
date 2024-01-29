from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ip_adress: str = "127.0.0.1"
    port: int = 8080
    hosts: str = "127.0.0.1:8080"

    class Config:
        env_file = ".env"

    def my_adress(self) -> str:
        return self.ip_adress + ":" + str(self.port)


settings = Settings()
