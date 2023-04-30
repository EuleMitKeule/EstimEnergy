"""Total model."""
from typing import Optional

from sqlmodel import Field, SQLModel


class Total(SQLModel, table=True):
    """Total model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    device_name: str = Field(default=None, index=True)
    energy: float = Field(default=0)
    cost: float = Field(default=0)
    power: float = Field(default=0)
