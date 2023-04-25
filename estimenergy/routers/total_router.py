from typing import Optional

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from estimenergy.db import db_engine
from estimenergy.device import devices
from estimenergy.models.total import Total

total_router = APIRouter(prefix="/total", tags=["total"])


@total_router.get(
    "",
    response_model=list[Total],
    responses={
        404: {"description": "Device not found"},
    },
    operation_id="get_totals",
)
async def get_totals(device_name: Optional[str] = None):
    """Get all totals."""

    if device_name is not None and device_name not in [
        device.device_config.name for device in devices
    ]:
        raise HTTPException(status_code=404, detail="Device not found")

    with Session(db_engine) as session:
        if device_name is None:
            totals = session.exec(select(Total)).all()
        else:
            totals = session.exec(
                select(Total).where(Total.device_name == device_name)
            ).all()
        return totals


@total_router.get(
    "/{id}",
    response_model=Total,
    responses={
        404: {"description": "Total not found"},
    },
    operation_id="get_total",
)
async def get_total(total_id: int):
    """Get a total."""

    with Session(db_engine) as session:
        total = session.exec(select(Total).where(Total.id == total_id)).first()
        if total is None:
            raise HTTPException(status_code=404, detail="Total not found")
        return total
