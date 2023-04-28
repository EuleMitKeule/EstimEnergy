"""The config for the SQL database."""
from pydantic import BaseModel


class SqlConfig(BaseModel):
    """The config for the SQL database."""

    url: str = "sqlite:///estimenergy.db"
