
from fastapi_crudrouter import TortoiseCRUDRouter

from estimenergy.models import EnergyData
from estimenergy.schemas import EnergySchema


router = TortoiseCRUDRouter(
    schema=EnergySchema,
    db_model=EnergyData,
    prefix="energy",
)
