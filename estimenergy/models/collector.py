
import asyncio
import datetime
import logging
from aioesphomeapi import EntityState, APIClient
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from estimenergy.helpers import get_days_in_month

from estimenergy.models.energy_data import EnergyData


class Collector(models.Model):
    name = fields.CharField(max_length=255, unique=True)
    host = fields.CharField(max_length=255)
    port = fields.IntField()
    password = fields.CharField(max_length=255)
    cost_per_kwh = fields.FloatField()
    base_cost_per_month = fields.FloatField()
    payment_per_month = fields.FloatField()
    energy_datas = fields.ReverseRelation["EnergyData"]
    min_hour = fields.IntField()
    max_hour = fields.IntField()

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

    async def calculate_day_cost(self):
        date = datetime.datetime.now()
        day_base_cost = self.base_cost_per_month / get_days_in_month(date.month, date.year)

        energy_data = await EnergyData.filter(collector=self, year=date.year, month=date.month, day=date.day).first()

        return day_base_cost + self.cost_per_kwh * energy_data.kwh

    async def calculate_day_cost_difference(self):
        date = datetime.datetime.now()
        days_in_month = get_days_in_month(date.month, date.year)

        payment_per_day: float = self.payment_per_month / days_in_month

        cost = await self.calculate_day_cost()
        
        return payment_per_day - cost
    
    async def predict_month_kwh_raw(self):
        date = datetime.datetime.now()
        days_in_month = get_days_in_month(date.month, date.year)

        energy_datas = await EnergyData.filter(collector=self, year=date.year, month=date.month)

        kwh_total = 0
        for energy_data in energy_datas:
            kwh_total = energy_data.kwh
        
        if len(energy_datas) == 0:
            return 0

        kwh_per_day: float = kwh_total / len(energy_datas)
        estimated_kwh_total: float = kwh_per_day * days_in_month
        return estimated_kwh_total
    
    async def predict_month_kwh(self):
        date = datetime.datetime.now()
        days_in_month = get_days_in_month(date.month, date.year)

        energy_datas = await EnergyData.filter(collector=self, year=date.year, month=date.month)
        
        if len(energy_datas) == 0:
            return 0

        recorded_days = 0
        kwh_total = 0
        for energy_data in energy_datas:
            is_completed = energy_data.is_completed and self.max_hour == 24
            reached_max_hour = energy_data.hour_updated >= self.max_hour and self.max_hour < 24

            if not is_completed or not reached_max_hour:
                continue

            if energy_data.hour_created > self.min_hour:
                continue

            kwh_total = energy_data.kwh
            recorded_days += 1

        if recorded_days == 0:
            return 0
        
        kwh_per_day: float = kwh_total / recorded_days
        estimated_kwh_total: float = kwh_per_day * days_in_month
        return estimated_kwh_total

    async def predict_month_cost_raw(self):
        kwh = await self.predict_month_kwh_raw()
        
        return self.base_cost_per_month + kwh * self.cost_per_kwh

    async def predict_month_cost(self):
        kwh = await self.predict_month_kwh()
        
        return self.base_cost_per_month + kwh * self.cost_per_kwh
    
    async def predict_month_cost_difference_raw(self):
        cost = await self.predict_month_cost_raw()
        return self.payment_per_month - cost
    
    async def predict_month_cost_difference(self):
        cost = await self.predict_month_cost()
        return self.payment_per_month - cost

    def __state_changed(self, state: EntityState):
        if not state.key == 3673186328:
            return
        
        current_kwh: float = state.state
        loop = asyncio.get_event_loop()
        loop.create_task(self.__current_kwh_changed(current_kwh))
    
    async def __current_kwh_changed(self, current_kwh: float):
        date = datetime.datetime.now()
        days_in_month = get_days_in_month(date.month, date.year)
        
        current_cost = current_kwh * self.cost_per_kwh + self.base_cost_per_month / days_in_month

        self.logger.info(f"Current KWh: {current_kwh}")

        energy_data = await EnergyData.filter(collector=self, year=date.year, month=date.month, day=date.day).first()
        
        if energy_data is None:
            await self.create_energy_data(current_kwh, current_cost, date)
            await self.update_previous_energy_data(date)
            return

        await self.update_energy_data(energy_data, current_kwh, current_cost, date)

    async def create_energy_data(self, kwh, cost, date):
        energy_data = EnergyData(
            collector=self,
            year=date.year,
            month=date.month,
            day=date.day,
            kwh=kwh,
            cost=cost,
            hour_created=date.hour,
            hour_updated=date.hour,
            is_completed=False
        )
        await energy_data.save()

    async def update_energy_data(self, energy_data, kwh, cost, date):
        energy_data.kwh = kwh
        energy_data.cost = cost
        energy_data.hour_updated = date.hour
        await energy_data.save()

    async def update_previous_energy_data(self, date):
        date_yesterday = date - datetime.timedelta(days=1)
        previous_energy_data = await EnergyData.filter(
            collector=self,
            year=date_yesterday.year,
            month=date_yesterday.month,
            day=date_yesterday.day
        ).first()

        if previous_energy_data is None:
            return
        
        if previous_energy_data.hour_updated < 23:
            return
        
        previous_energy_data.is_completed = True
        await previous_energy_data.save()

CollectorSchema = pydantic_model_creator(Collector, name="Collector")
