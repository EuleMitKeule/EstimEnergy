
from tortoise import fields, models


class EnergyData(models.Model):
    collector = fields.ForeignKeyField("models.CollectorData", related_name="energy_datas")
    year = fields.IntField()
    month = fields.IntField()
    day = fields.IntField()
    kwh = fields.FloatField()
    hour_created = fields.IntField()
    hour_updated = fields.IntField()
    is_completed = fields.BooleanField()

    class Meta:
        unique_together = ("collector", "year", "month", "day")

    @property
    def accuracy(self) -> float:
        hour_updated = 24 if self.is_completed else self.hour_updated
        hours_with_data = hour_updated - self.hour_created
        return hours_with_data / 24
