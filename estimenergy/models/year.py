from typing import Optional
import datetime
from sqlmodel import Field, SQLModel

from estimenergy.models.config.device_config import DeviceConfig


class Year(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_name: str = Field(default=None, index=True)
    date: datetime.date = Field(default=None, index=True)

    energy: float = Field(default=0)
    cost: float = Field(default=0)
    cost_difference: float = Field(default=0)
    accuracy: float = Field(default=0)

    energy_predicted: float = Field(default=0)
    cost_predicted: float = Field(default=0)
    cost_difference_predicted: float = Field(default=0)

    def __init__(
        self,
        device_config: DeviceConfig,
        date: datetime.date,
        energy: float = 0,
        accuracy: float = 0,
    ):
        device_name = device_config.name
        cost = (
            energy * device_config.cost_per_kwh + device_config.base_cost_per_month * 12
        )
        cost_difference = device_config.payment_per_month * 12 - cost

        super().__init__(
            device_name=device_name,
            date=date,
            energy=energy,
            cost=cost,
            cost_difference=cost_difference,
            accuracy=accuracy,
        )
