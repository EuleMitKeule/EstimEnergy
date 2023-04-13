from pydantic import BaseModel
from estimenergy.const import DEFAULT_HOST, DEFAULT_PORT


class NetworkingConfig(BaseModel):
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
