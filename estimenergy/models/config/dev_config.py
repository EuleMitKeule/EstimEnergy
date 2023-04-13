from pydantic import BaseModel


class DevConfig(BaseModel):
    reload: bool = False
