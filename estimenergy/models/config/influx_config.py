from pydantic import BaseModel, SecretStr


class InfluxConfig(BaseModel):
    url: str
    token: SecretStr
    org: str
    bucket: str
