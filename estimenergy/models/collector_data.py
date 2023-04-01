
import datetime
import logging
from tortoise import fields, models
from tortoise.expressions import Q

from estimenergy.helpers import get_days_in_month
from estimenergy.models.energy_data import EnergyData
from estimenergy.const import METRICS, Metric, MetricPeriod, MetricType


class CollectorData(models.Model):
    name = fields.CharField(max_length=255, unique=True)
    host = fields.CharField(max_length=255)
    port = fields.IntField()
    password = fields.CharField(max_length=255)
    cost_per_kwh = fields.FloatField()
    base_cost_per_month = fields.FloatField()
    payment_per_month = fields.FloatField()
    energy_datas = fields.ReverseRelation["EnergyData"]
    billing_month = fields.IntField()
    min_accuracy = fields.FloatField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("energy_collector").getChild(self.name)

    async def get_metrics(self, date: datetime.date):
        return {
            metric.json_key: await self.get_metric(metric, date)
            for metric in METRICS
        }
    
    async def get_metric(self, metric: Metric, date: datetime.date):
        if metric.metric_type == MetricType.ENERGY:
            return await self.get_energy(metric, date)
        
        if metric.metric_type == MetricType.COST:
            return await self.get_cost(metric, date)
        
        if metric.metric_type == MetricType.COST_DIFFERENCE:
            return await self.get_cost_difference(metric, date)
        
        if metric.metric_type == MetricType.ACCURACY:
            return await self.get_accuracy(metric, date)
        
        raise ValueError(f"Unknown metric type {metric.metric_type}")

    async def get_energy(self, metric: Metric, date: datetime.date):
        energy_datas = await self.get_energy_datas(metric.metric_period, date)

        if not metric.is_predicted:
            return sum(energy_data.kwh for energy_data in energy_datas)
        
        if metric.metric_period == MetricPeriod.TOTAL:
            raise ValueError("Cannot predict total energy")
        
        if metric.metric_period == MetricPeriod.MONTH:
            days_in_month = get_days_in_month(date.month, date.year)
            days_with_data = len(energy_datas)

            if days_with_data == 0:
                return 0

            energy_total = sum(energy_data.kwh for energy_data in energy_datas if metric.is_raw or energy_data.accuracy >= self.min_accuracy)
            energy_per_day = energy_total / days_with_data
            return energy_per_day * days_in_month
        
        if metric.metric_period == MetricPeriod.YEAR:
            current_year = date.year

            kwh_total = 0
            missing_months = 0
            for month_offset in range(12):
                month = (self.billing_month + month_offset - 1) % 12 + 1

                is_after_billing_month = month >= self.billing_month
                year = current_year - (1 if is_after_billing_month else 0)

                date = date.replace(year=year, month=month, day=1)

                accuracy = await self.get_accuracy(Metric(MetricType.ACCURACY, MetricPeriod.MONTH, False, False), date)

                if not metric.is_raw and accuracy < self.min_accuracy:
                    missing_months += 1
                    continue

                kwh_total += await self.get_energy(Metric(MetricType.ENERGY, MetricPeriod.MONTH, True, metric.is_raw), date)

            if missing_months == 12:
                return 0
            
            return kwh_total / (12 - missing_months) * 12
        
    async def get_cost(self, metric: Metric, date: datetime.date):
        energy = await self.get_energy(metric, date)
        kwh_cost = energy * self.cost_per_kwh
        
        if metric.metric_period == MetricPeriod.DAY:
            return kwh_cost + self.base_cost_per_month / get_days_in_month(date.month, date.year)

        if metric.metric_period == MetricPeriod.MONTH:
            return kwh_cost + self.base_cost_per_month
        
        return kwh_cost + self.base_cost_per_month * 12
    
    async def get_cost_difference(self, metric: Metric, date: datetime.date):
        cost = await self.get_cost(metric, date)
        payment = await self.get_payment(metric, date)
        
        return payment - cost 

    async def get_accuracy(self, metric: Metric, date: datetime.date):
        energy_datas = await self.get_energy_datas(metric.metric_period, date)
        day_count = await self.get_day_count(metric.metric_period, date)
        accuracy_total = sum(energy_data.accuracy for energy_data in energy_datas) / day_count

        return accuracy_total

    async def get_payment(self, metric: Metric, date: datetime.date):
        if metric.metric_period == MetricPeriod.DAY:
            return self.payment_per_month / get_days_in_month(date.month, date.year)
        
        if metric.metric_period == MetricPeriod.MONTH:
            return self.payment_per_month
        
        return self.payment_per_month * 12

    async def get_energy_datas(
            self, 
            metric_period: 
            MetricPeriod, 
            date: datetime.date
        ) -> list[EnergyData]:
        if metric_period == MetricPeriod.DAY:
            return await EnergyData.filter(collector=self, year=date.year, month=date.month, day=date.day)
        
        if metric_period == MetricPeriod.MONTH:
            return await EnergyData.filter(collector=self, year=date.year, month=date.month)
        
        if metric_period == MetricPeriod.YEAR:
            start_year = date.year - 1 if date.month < self.billing_month else date.year
            end_year = date.year if date.month < self.billing_month else date.year + 1

            return await EnergyData.filter(
                Q(collector=self, year=start_year, month__gte=self.billing_month) |
                Q(collector=self, year=end_year, month__lt=self.billing_month)
            )
        
        if metric_period == MetricPeriod.TOTAL:
            return await EnergyData.filter(collector=self)

        raise ValueError(f"Unknown metric period {metric_period}")

    async def get_day_count(self, metric_period: MetricPeriod, date: datetime.date) -> int:
        if metric_period == MetricPeriod.DAY:
            return 1
        
        if metric_period == MetricPeriod.MONTH:
            return get_days_in_month(date.month, date.year)
        
        if metric_period == MetricPeriod.YEAR:
            return 365
        
        if metric_period == MetricPeriod.TOTAL:
            raise ValueError("Cannot get day count for total energy")

        raise ValueError(f"Unknown metric period {metric_period}")
