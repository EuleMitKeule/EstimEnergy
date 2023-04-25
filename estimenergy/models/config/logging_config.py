from pydantic import BaseModel

from estimenergy.const import DEFAULT_LOG_LEVEL, DEFAULT_LOG_PATH


class LoggingConfig(BaseModel):
    log_path: str = DEFAULT_LOG_PATH
    log_level: str = DEFAULT_LOG_LEVEL
