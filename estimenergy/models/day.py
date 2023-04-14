import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

from estimenergy.models.config.device_config import DeviceConfig
from estimenergy.helpers import get_days_in_month


class Day(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_name: str = Field(default=None, index=True)
    date: datetime.date = Field(default=None, index=True)

    year_id: Optional[int] = Field(default=None, foreign_key="year.id")
    month_id: Optional[int] = Field(default=None, foreign_key="month.id")

    energy: float = Field(default=0)
    cost: float = Field(default=0)
    cost_difference: float = Field(default=0)
    accuracy: float = Field(default=0)

    def __init__(
        self,
        device_config: DeviceConfig,
        date: datetime.date,
        energy: float = 0,
        accuracy: float = 0,
    ):
        device_name = device_config.name
        days_in_month = get_days_in_month(date.month, date.year)
        base_cost_per_day = device_config.base_cost_per_month / days_in_month
        payment_per_day = device_config.payment_per_month / days_in_month

        cost = energy * device_config.cost_per_kwh + base_cost_per_day
        cost_difference = payment_per_day - cost

        super().__init__(
            device_name=device_name,
            date=date,
            energy=energy,
            cost=cost,
            cost_difference=cost_difference,
            accuracy=accuracy,
        )
