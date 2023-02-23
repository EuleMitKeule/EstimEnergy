
from fastapi import APIRouter, Depends
from estimenergy.models import Settings
from estimenergy.dependencies import get_settings


router = APIRouter()


@router.get("/settings")
async def get_settings(settings: Settings = Depends(get_settings)):
    return settings.dict()