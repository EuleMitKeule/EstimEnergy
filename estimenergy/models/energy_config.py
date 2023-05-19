from sqlmodel import Field, SQLModel


class EnergyConfigBase(SQLModel):
    """Base energy config."""


class EnergyConfig(EnergyConfigBase, table=True):
    """Energy config in database."""
