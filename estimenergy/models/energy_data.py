
from tortoise import fields, models


class EnergyData(models.Model):
    id = fields.IntField(pk=True)
