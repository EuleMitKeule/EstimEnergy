
from tortoise.contrib.pydantic import pydantic_model_creator

from estimenergy.models import CollectorData


CollectorSchema = pydantic_model_creator(CollectorData, name="Collector")
