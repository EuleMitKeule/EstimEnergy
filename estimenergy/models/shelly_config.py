from sqlmodel import Field, SQLModel


class ShellyConfigBase(SQLModel):
    """Config class for Shelly devices."""

    host: str
    username: str | None = Field(default=None)
    poll_interval: float = Field(default=0.1)


class ShellyConfig(ShellyConfigBase, table=True):
    """Config class for Shelly devices with secrets."""

    id: int | None = Field(default=None, primary_key=True)
    password: str | None = Field(default=None)


class ShellyConfigIn(ShellyConfigBase):
    """Config class for Shelly devices with secrets."""

    password: str | None


class ShellyConfigOut(ShellyConfigBase):
    """Config class for Shelly devices without secrets."""

    id: int
