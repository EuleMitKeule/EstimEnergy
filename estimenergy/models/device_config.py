"""Device config models."""
from sqlmodel import Field, SQLModel

from estimenergy.const import DeviceType


class BaseDeviceConfig(SQLModel):
    """Base device config."""

    name: str = Field(default=None, primary_key=True)
    type: DeviceType = Field(default=DeviceType.GLOW)
    host: str = Field(default=None)
    port: int = Field(default=None)
    cost_per_kwh: float = Field(default=0)
    base_cost_per_month: float = Field(default=0)
    payment_per_month: float = Field(default=0)
    billing_month: int = Field(default=1)
    min_accuracy: float = Field(default=0)
    is_active: bool = Field(default=True)
    is_connected: bool = Field(default=False)


class DeviceConfig(BaseDeviceConfig, table=True):
    """Device config with secrets."""

    password: str = Field(default="")


class DeviceConfigRead(BaseDeviceConfig):
    """Device config without secrets."""
