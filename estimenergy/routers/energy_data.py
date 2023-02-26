from fastapi_crudrouter import TortoiseCRUDRouter
from tortoise.contrib.pydantic import pydantic_model_creator

from estimenergy.models import EnergyData


router = TortoiseCRUDRouter(
    schema=pydantic_model_creator(EnergyData, name="EnergyData"),
    db_model=EnergyData,
    prefix="energy_data",
)
