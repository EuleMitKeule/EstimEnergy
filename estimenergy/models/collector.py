
import datetime
import logging
from prometheus_client import Gauge, Metric
from prometheus_client.registry import Collector as PrometheusCollector
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from estimenergy.const import SENSOR_TYPE_FRIENDLY_NAME, SENSOR_TYPE_JSON, SENSOR_TYPES
from estimenergy.helpers import get_days_in_month

from estimenergy.models.energy_data import EnergyData
from estimenergy.common import collector_registry
from estimenergy.collector_clients import GlowClient


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
    max_incomplete_days = fields.IntField()
    billing_month = fields.IntField()

    async def connect(self):
        self.logger = logging.getLogger("energy_collector").getChild(self.name)

        self.client = GlowClient(
            name=self.name,
            host=self.host,
            port=self.port,
            password=self.password,
            kwh_callback=self.__on_kwh_changed,
        )

        await self.client.start()
        
        self.prometheus_collector = CollectorPrometheusCollector(self)
        collector_registry.register(self.prometheus_collector)

    async def get_data(self, date: datetime.date = datetime.datetime.now()):
        day_kwh = await self.get_day_kwh(date)
        day_cost = await self.get_day_cost(date)
        day_cost_difference = await self.get_day_cost_difference(date)
        predicted_month_kwh_raw = await self.get_predicted_month_kwh_raw(date)
        predicted_month_cost_raw = await self.get_predicted_month_cost_raw(date)
        predicted_month_cost_difference_raw = await self.get_predicted_month_cost_difference_raw(date)
        predicted_month_kwh = await self.get_predicted_month_kwh(date)
        predicted_month_cost = await self.get_predicted_month_cost(date)
        predicted_month_cost_difference = await self.get_predicted_month_cost_difference(date)
        predicted_year_kwh_raw = await self.get_predicted_year_kwh_raw(date)
        predicted_year_cost_raw = await self.get_predicted_year_cost_raw(date)
        predicted_year_cost_difference_raw = await self.get_predicted_year_cost_difference_raw(date)
        predicted_year_kwh = await self.get_predicted_year_kwh(date)
        predicted_year_cost = await self.get_predicted_year_cost(date)
        predicted_year_cost_difference = await self.get_predicted_year_cost_difference(date)

        return {
            "day_kwh": day_kwh,
            "day_cost": day_cost,
            "day_cost_difference": day_cost_difference,
            "predicted_month_kwh_raw": predicted_month_kwh_raw,
            "predicted_month_cost_raw": predicted_month_cost_raw,
            "predicted_month_cost_difference_raw": predicted_month_cost_difference_raw,
            "predicted_month_kwh": predicted_month_kwh,
            "predicted_month_cost": predicted_month_cost,
            "predicted_month_cost_difference": predicted_month_cost_difference,
            "predicted_year_kwh_raw": predicted_year_kwh_raw,
            "predicted_year_cost_raw": predicted_year_cost_raw,
            "predicted_year_cost_difference_raw": predicted_year_cost_difference_raw,
            "predicted_year_kwh": predicted_year_kwh,
            "predicted_year_cost": predicted_year_cost,
            "predicted_year_cost_difference": predicted_year_cost_difference,
        }

    async def get_day_kwh(self, date):
        energy_data = await EnergyData.filter(collector=self, year=date.year, month=date.month, day=date.day).first()
        if energy_data is None:
            return 0
        
        return energy_data.kwh

    async def get_day_cost(self, date):
        day_base_cost = self.base_cost_per_month / get_days_in_month(date.month, date.year)

        energy_data = await EnergyData.filter(collector=self, year=date.year, month=date.month, day=date.day).first()
        if energy_data is None:
            return 0

        return day_base_cost + self.cost_per_kwh * energy_data.kwh

    async def get_day_cost_difference(self, date):
        days_in_month = get_days_in_month(date.month, date.year)

        payment_per_day: float = self.payment_per_month / days_in_month

        cost = await self.get_day_cost(date)
        
        return payment_per_day - cost
    
    async def get_predicted_month_kwh_raw(self, date):
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
    
    async def get_predicted_month_kwh(self, date):
        days_in_month = get_days_in_month(date.month, date.year)

        energy_datas = await self.get_recorded_energy_datas_in_month(date)
        
        recorded_days = len(energy_datas)
        
        if recorded_days == 0:
            return 0

        kwh_total = 0
        for energy_data in energy_datas:
            kwh_total += energy_data.kwh
        
        kwh_per_day: float = kwh_total / recorded_days
        estimated_kwh_total: float = kwh_per_day * days_in_month
        return estimated_kwh_total

    async def get_predicted_month_cost_raw(self, date):
        kwh = await self.get_predicted_month_kwh_raw(date)
        
        return self.base_cost_per_month + kwh * self.cost_per_kwh

    async def get_predicted_month_cost(self, date):
        kwh = await self.get_predicted_month_kwh(date)
        
        return self.base_cost_per_month + kwh * self.cost_per_kwh
    
    async def get_predicted_month_cost_difference_raw(self, date):
        cost = await self.get_predicted_month_cost_raw(date)
        return self.payment_per_month - cost
    
    async def get_predicted_month_cost_difference(self, date):
        cost = await self.get_predicted_month_cost(date)
        return self.payment_per_month - cost
    
    async def get_predicted_year_kwh_raw(self, date):
        current_year = date.year
        
        kwh_total = 0
        for month_offset in range(12):
            month = (self.billing_month + month_offset - 1) % 12 + 1

            is_after_billing_month = month >= self.billing_month
            year = current_year - (1 if is_after_billing_month else 0)

            date = date.replace(year=year, month=month, day=1)

            kwh_total += await self.get_predicted_month_kwh_raw(date)
        
        return kwh_total
    
    async def get_predicted_year_kwh(self, date):
        current_year = date.year

        kwh_total = 0
        recorded_months = 0
        for month_offset in range(12):
            month = (self.billing_month + month_offset - 1) % 12 + 1

            is_after_billing_month = month >= self.billing_month
            year = current_year - (1 if is_after_billing_month else 0)

            date = date.replace(year=year, month=month, day=1)

            energy_datas = await self.get_recorded_energy_datas_in_month(date)
            recorded_days = len(energy_datas)

            days_in_month = get_days_in_month(date.month, date.year)
            if recorded_days < days_in_month - self.max_incomplete_days:
                continue

            recorded_months += 1
            kwh_total += await self.get_predicted_month_kwh(date)

        if recorded_months == 0:
            return 0
        
        kwh_per_month = kwh_total / recorded_months
        return kwh_per_month * 12
    
    async def get_predicted_year_cost_raw(self, date):
        kwh = await self.get_predicted_year_kwh_raw(date)
        base_cost = self.base_cost_per_month * 12
        return base_cost + kwh * self.cost_per_kwh
    
    async def get_predicted_year_cost(self, date):
        kwh = await self.get_predicted_year_kwh(date)
        base_cost = self.base_cost_per_month * 12
        return base_cost + kwh * self.cost_per_kwh
    
    async def get_predicted_year_cost_difference_raw(self, date):
        cost = await self.get_predicted_year_cost_raw(date)
        payment = self.payment_per_month * 12
        return payment - cost
    
    async def get_predicted_year_cost_difference(self, date):
        cost = await self.get_predicted_year_cost(date)
        payment = self.payment_per_month * 12
        return payment - cost

    async def get_recorded_energy_datas_in_month(self, date) -> list[EnergyData]:
        energy_datas = await EnergyData.filter(collector=self, year=date.year, month=date.month)

        recorded_energy_datas = []
        for energy_data in energy_datas:
            is_completed = energy_data.is_completed and self.max_hour == 24
            reached_max_hour = energy_data.hour_updated >= self.max_hour and self.max_hour < 24

            if not is_completed or not reached_max_hour:
                continue

            if energy_data.hour_created > self.min_hour:
                continue
            
            recorded_energy_datas.append(energy_data)
        
        return recorded_energy_datas

    async def __on_kwh_changed(self, current_kwh: float):
        date = datetime.datetime.now()
        days_in_month = get_days_in_month(date.month, date.year)
        
        current_cost = current_kwh * self.cost_per_kwh + self.base_cost_per_month / days_in_month

        self.logger.info(f"Current KWh: {current_kwh}")

        energy_data = await EnergyData.filter(collector=self, year=date.year, month=date.month, day=date.day).first()
        
        if energy_data is None:
            await self.__create_energy_data(current_kwh, current_cost, date)
            await self.__update_previous_energy_data(date)
            return

        await self.__update_energy_data(energy_data, current_kwh, current_cost, date)
        await self.prometheus_collector.update_metrics()

    async def __create_energy_data(self, kwh, cost, date):
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

    async def __update_energy_data(self, energy_data, kwh, cost, date):
        energy_data.kwh = kwh
        energy_data.cost = cost
        energy_data.hour_updated = date.hour
        await energy_data.save()

    async def __update_previous_energy_data(self, date):
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

class CollectorWithDataSchema(CollectorSchema):
    data: dict


class CollectorPrometheusCollector(PrometheusCollector):
    def __init__(self, collector: Collector):
        self.collector = collector
        self.metrics = {
            sensor_type[SENSOR_TYPE_JSON]: self.create_metric(
                name=sensor_type[SENSOR_TYPE_JSON],
                documentation=sensor_type[SENSOR_TYPE_FRIENDLY_NAME]
            )
            for sensor_type in SENSOR_TYPES
        }

    async def collect(self):
        return self.metrics.values()
    
    def create_metric(self, name: str, documentation: str) -> Metric:
        metric = Gauge(
            name=name,
            documentation=documentation,
            labelnames=["name", "id"]
        )

        return metric
    
    async def update_metrics(self):
        data = await self.collector.get_data()
        for sensor_type in SENSOR_TYPES:
            self.metrics[sensor_type[SENSOR_TYPE_JSON]].labels(name=self.collector.name, id=self.collector.id).set(data[sensor_type[SENSOR_TYPE_JSON]])
