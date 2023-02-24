from fastapi_crudrouter import TortoiseCRUDRouter
from tortoise.contrib.pydantic import pydantic_model_creator

from estimenergy.models import Collector


router = TortoiseCRUDRouter(
    schema=pydantic_model_creator(Collector, name="Collector"),
    db_model=Collector,
    prefix="energy_data",
)
