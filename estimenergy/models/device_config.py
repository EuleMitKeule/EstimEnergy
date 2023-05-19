"""Device config models."""

from sqlmodel import Field, Relationship, SQLModel

from estimenergy.const import DeviceType
from estimenergy.models.glow_config import GlowConfig, GlowConfigIn, GlowConfigOut
from estimenergy.models.shelly_config import (
    ShellyConfig,
    ShellyConfigIn,
    ShellyConfigOut,
)


class DeviceConfigBase(SQLModel):
    """Base device config."""

    name: str = Field(unique=True)
    device_type: DeviceType
    is_active: bool = Field(default=True)

    cost_per_kwh: float = Field(default=0)
    base_cost_per_month: float = Field(default=0)
    payment_per_month: float = Field(default=0)
    billing_month: int = Field(default=1)
    min_accuracy: float = Field(default=0)

    glow_config_id: int | None = Field(
        default=None, foreign_key="glowconfig.id", nullable=True
    )
    shelly_config_id: int | None = Field(
        default=None, foreign_key="shellyconfig.id", nullable=True
    )


class DeviceConfig(DeviceConfigBase, table=True):
    """Device config model."""

    id: int | None = Field(default=None, primary_key=True)
    glow_config: GlowConfig | None = Relationship(
        sa_relationship_kwargs={"cascade": "delete"},
    )
    shelly_config: ShellyConfig | None = Relationship(
        sa_relationship_kwargs={"cascade": "delete"},
    )


class DeviceConfigIn(DeviceConfigBase):
    """Device config in model."""

    glow_config: GlowConfigIn | None
    shelly_config: ShellyConfigIn | None


class DeviceConfigOut(DeviceConfigBase):
    """Device config out model."""

    id: int
    glow_config: GlowConfigOut | None
    shelly_config: ShellyConfigOut | None
