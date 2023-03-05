
from fastapi_crudrouter import TortoiseCRUDRouter

from estimenergy.models import CollectorData
from estimenergy.schemas import CollectorSchema


router = TortoiseCRUDRouter(
    schema=CollectorSchema,
    db_model=CollectorData,
    prefix="collector",
)
