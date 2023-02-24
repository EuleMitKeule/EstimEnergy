
import asyncio
import datetime
import logging
from aioesphomeapi import EntityState, APIClient
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

from estimenergy.models.energy_data import EnergyData


class Collector(models.Model):
    name = fields.CharField(max_length=255, unique=True)
    host = fields.CharField(max_length=255)
    port = fields.IntField()
    password = fields.CharField(max_length=255)
    cost_per_kwh = fields.FloatField()
    base_cost_per_month = fields.FloatField()
    energy_datas = fields.ReverseRelation["EnergyData"]

    async def connect(self):
        self.logger = logging.getLogger("energy_collector").getChild(self.name)
        self.logger.info("Connecting to Home Assistant Glow", )
        self.api = APIClient(
            self.host,
            self.port,
            self.password
        )

        await self.api.connect(login=True)
        await self.api.subscribe_states(self.__state_changed)

    def __state_changed(self, state: EntityState):
        if not state.key == 3673186328:
            return
        
        current_kwh: float = state.state
        loop = asyncio.get_event_loop()
        loop.create_task(self.__current_kwh_changed(current_kwh))
    
    async def __current_kwh_changed(self, current_kwh: float):
        
        self.logger.info(f"Current KWh: {current_kwh}")

        date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        energy_data = await EnergyData.filter(collector=self, year=date.year, month=date.month, day=date.day).first()
        
        if energy_data is None:
            energy_data = EnergyData(collector=self, year=date.year, month=date.month, day=date.day, kwh=current_kwh)
            await energy_data.save()
            return
        
        energy_data.kwh = current_kwh
        await energy_data.save()
    

CollectorSchema = pydantic_model_creator(Collector, name="Collector")
