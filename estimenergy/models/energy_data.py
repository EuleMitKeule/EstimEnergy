
from typing import Type
from tortoise import fields, models
from tortoise.signals import pre_save
from estimenergy.helpers import get_days_in_month


class EnergyData(models.Model):
    id = fields.IntField(pk=True)
    collector = fields.ForeignKeyField("models.Collector", related_name="energy_datas")
    year = fields.IntField()
    month = fields.IntField()
    day = fields.IntField()
    kwh = fields.FloatField()
    cost = fields.FloatField()
    
    async def calculate_cost(self) -> float:
        days_in_month = get_days_in_month(self.month, self.year)

        collector = await self.collector

        return self.kwh * collector.cost_per_kwh + collector.base_cost_per_month / days_in_month

    class Meta:
        unique_together = ("collector", "year", "month", "day")

@pre_save(EnergyData)
async def pre_save(sender: "Type[EnergyData]", instance: EnergyData, using_db, update_fields) -> None:
    instance.cost = await instance.calculate_cost()
