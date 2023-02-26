
import asyncio
from typing import Awaitable, Type
from tortoise import fields, models
from tortoise.signals import pre_save
from estimenergy.helpers import get_days_in_month


class EnergyData(models.Model):
    collector = fields.ForeignKeyField("models.Collector", related_name="energy_datas")
    year = fields.IntField()
    month = fields.IntField()
    day = fields.IntField()
    kwh = fields.FloatField()
    hour_created = fields.IntField()
    hour_updated = fields.IntField()
    is_completed = fields.BooleanField()

    class Meta:
        unique_together = ("collector", "year", "month", "day")
