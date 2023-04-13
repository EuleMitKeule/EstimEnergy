from sqlmodel import Field, SQLModel
from typing import Optional
from estimenergy.models.config.device_config import DeviceConfig


class Total(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_name: str = Field(default=None, index=True)
    energy: float = Field(default=0)
    cost: float = Field(default=0)

    def __init__(
        self,
        device_config: DeviceConfig,
        energy: float = 0,
        **data,
    ):
        device_name = device_config.name
        cost = energy * device_config.cost_per_kwh

        super().__init__(
            device_name=device_name,
            energy=energy,
            cost=cost,
            **data,
        )
