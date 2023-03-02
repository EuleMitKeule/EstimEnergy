from datetime import datetime
from fastapi import HTTPException
from fastapi_crudrouter import TortoiseCRUDRouter
from tortoise.contrib.pydantic import pydantic_model_creator

from estimenergy.models import Collector, CollectorWithDataSchema


router = TortoiseCRUDRouter(
    schema=pydantic_model_creator(Collector, name="Collector"),
    db_model=Collector,
    prefix="collector",
)


@router.get("/{item_id}", response_model=CollectorWithDataSchema)
async def get_collector(item_id: int, date: datetime = datetime.now()):
    collector = await Collector.filter(id=item_id).first()

    if collector is None:
        raise HTTPException(status_code=404, detail="Collector name not found.")

    collector.data = await collector.get_data(date)

    return collector
