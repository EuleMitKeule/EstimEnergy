from sqlmodel import Field, SQLModel


class BaseGlowConfig(SQLModel):
    """Config class for glow devices."""

    host: str
    port: int = Field(default=6053)
    username: str | None = Field(default=None)


class GlowConfig(BaseGlowConfig, table=True):
    """Config class for glow devices in database."""

    id: int | None = Field(default=None, primary_key=True)
    password: str | None = Field(default=None)


class GlowConfigIn(BaseGlowConfig):
    """Config class for glow devices with secrets."""

    password: str | None


class GlowConfigOut(BaseGlowConfig):
    """Config class for glow devices without secrets."""

    id: int
