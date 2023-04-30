from pydantic import BaseModel, SecretStr


class InfluxConfig(BaseModel):
    url: str
    token: str
    org: str
    bucket: str
