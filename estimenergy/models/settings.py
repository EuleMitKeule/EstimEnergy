
from pydantic import BaseSettings


class Settings(BaseSettings):
    glow_host: str = "localhost"
    glow_port: int = 6053
    glow_password: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


    