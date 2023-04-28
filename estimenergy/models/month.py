"""Month model."""
import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Month(SQLModel, table=True):
    """Month model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    device_name: str = Field(default=None, index=True)
    date: datetime.date = Field(default=None, index=True)
    year_id: Optional[int] = Field(default=None, foreign_key="year.id")
    energy: float = Field(default=0)
    cost: float = Field(default=0)
    cost_difference: float = Field(default=0)
    accuracy: float = Field(default=0)
    energy_predicted_raw: float = Field(default=0)
    energy_predicted: float = Field(default=0)
    cost_predicted_raw: float = Field(default=0)
    cost_predicted: float = Field(default=0)
    cost_difference_predicted_raw: float = Field(default=0)
    cost_difference_predicted: float = Field(default=0)
