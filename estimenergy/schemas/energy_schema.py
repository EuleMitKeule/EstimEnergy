
from tortoise.contrib.pydantic import pydantic_model_creator

from estimenergy.models import EnergyData


EnergySchema = pydantic_model_creator(EnergyData, name="Energy")
