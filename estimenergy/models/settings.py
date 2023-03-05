
from pydantic import BaseSettings


class Settings(BaseSettings):
    
    config_path: str = "config.yml"
    log_config_path: str = "logging.yml"
    db_path: str = "estimenergy.db"
    enable_metrics: bool = True
    reload: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


    