from typing import Optional
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from estimenergy.models.year import Year
from estimenergy.db import db_engine
from estimenergy.device import devices


year_router = APIRouter(prefix="/year")


@year_router.get(
    "",
    response_model=list[Year],
    responses={
        404: {"description": "Device not found"},
    },
)
async def get_years(device_name: Optional[str] = None):
    """Get all years."""

    if device_name is not None and device_name not in [
        device.device_config.name for device in devices
    ]:
        raise HTTPException(status_code=404, detail="Device not found")

    with Session(db_engine) as session:
        if device_name is None:
            years = session.exec(select(Year)).all()
        else:
            years = session.exec(
                select(Year).where(Year.device_name == device_name)
            ).all()
        return years


@year_router.get(
    "/{id}",
    response_model=Year,
    responses={
        404: {"description": "Year not found"},
    },
)
async def get_year(year_id: int):
    """Get a year."""

    with Session(db_engine) as session:
        year = session.exec(select(Year).where(Year.id == year_id)).first()
        if year is None:
            raise HTTPException(status_code=404, detail="Year not found")
        return year
