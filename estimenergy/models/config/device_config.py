"""Device config models."""
from pydantic import BaseModel

from estimenergy.const import DeviceType


class BaseDeviceConfig(BaseModel):
    """Base device config."""

    name: str
    type: DeviceType
    cost_per_kwh: float
    base_cost_per_month: float
    payment_per_month: float
    billing_month: int
    min_accuracy: float


class DeviceConfig(BaseDeviceConfig):
    """Device config with secrets."""

    host: str
    port: int
    password: str


class DeviceConfigRead(BaseDeviceConfig):
    """Device config without secrets."""
