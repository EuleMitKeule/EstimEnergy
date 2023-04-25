"""Day model."""
import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class DayBase(SQLModel):
    """Day base model."""

    device_name: str = Field(default=None, index=True)
    date: datetime.date = Field(default=None, index=True)
    energy: float = Field(default=0)
    accuracy: float = Field(default=0)


class DayBaseCalc(DayBase):
    """Day base model with calculated fields."""

    cost: float = Field(default=0)
    cost_difference: float = Field(default=0)


class Day(DayBaseCalc, table=True):
    """Day model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    year_id: Optional[int] = Field(default=None, foreign_key="year.id")
    month_id: Optional[int] = Field(default=None, foreign_key="month.id")


class DayCreate(DayBase):
    """Day create model."""


class DayRead(DayBaseCalc):
    """Day read model."""

    id: int
