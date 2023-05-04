"""Service for predicting energy usage."""
import datetime

from estimenergy.const import MetricPeriod
from estimenergy.helpers import get_days_in_month, get_days_in_year
from estimenergy.models.config.config import Config
from estimenergy.models.device_config import DeviceConfig


class PredictionService:
    """Service for predicting energy usage."""

    device_config: DeviceConfig
    config: Config

    def __init__(self, device_config: DeviceConfig, config: Config):
        self.device_config = device_config
        self.config = config

    async def calculate_cost(
        self,
        metric_period: MetricPeriod,
        energy: float,
        date: datetime.date,
    ) -> float:
        """Calculate the cost."""

        if metric_period == MetricPeriod.DAY:
            days_in_month = get_days_in_month(date.month, date.year)
            base_cost = self.device_config.base_cost_per_month / days_in_month
        elif metric_period == MetricPeriod.MONTH:
            base_cost = self.device_config.base_cost_per_month
        elif metric_period == MetricPeriod.YEAR:
            base_cost = self.device_config.base_cost_per_month * 12
        else:
            base_cost = 0

        energy_cost = energy * self.device_config.cost_per_kwh
        cost = base_cost + energy_cost

        return cost

    async def calculate_cost_difference(
        self,
        metric_period: MetricPeriod,
        energy: float,
        date: datetime.date,
    ) -> float:
        """Calculate the cost difference."""

        if metric_period == MetricPeriod.DAY:
            days_in_month = get_days_in_month(date.month, date.year)
            payment = self.device_config.payment_per_month / days_in_month
        elif metric_period == MetricPeriod.MONTH:
            payment = self.device_config.payment_per_month
        elif metric_period == MetricPeriod.YEAR:
            payment = self.device_config.payment_per_month * 12
        else:
            return 0

        cost = await self.calculate_cost(metric_period, energy, date)
        cost_difference = payment - cost

        return cost_difference

    async def calculate_accuracy(
        self,
        metric_period: MetricPeriod,
        accuracy_sum: float,
        date: datetime.date,
    ) -> float:
        """Calculate the accuracy."""

        if metric_period == MetricPeriod.MONTH:
            day_count = get_days_in_month(date.year, date.month)
        elif metric_period == MetricPeriod.YEAR:
            day_count = get_days_in_year(date.year)
        else:
            return 0

        total_accuracy = accuracy_sum / day_count

        return total_accuracy

    async def predict_energy(
        self,
        metric_period: MetricPeriod,
        energy: float,
        accurate_day_count: int,
        date: datetime.date,
    ) -> float:
        """Predict the energy."""

        if metric_period == MetricPeriod.MONTH:
            day_count = get_days_in_month(date.year, date.month)
        elif metric_period == MetricPeriod.YEAR:
            day_count = get_days_in_year(date.year)
        else:
            return 0

        if accurate_day_count == 0:
            return 0

        mean_energy_per_day = energy / accurate_day_count
        predicted_energy = mean_energy_per_day * day_count

        return predicted_energy

    async def predict_cost(
        self,
        metric_period: MetricPeriod,
        energy: float,
        accurate_day_count: int,
        date: datetime.date,
    ) -> float:
        """Predict the cost."""

        predicted_energy = await self.predict_energy(
            metric_period, energy, accurate_day_count, date
        )
        predicted_cost = await self.calculate_cost(
            metric_period, predicted_energy, date
        )

        return predicted_cost

    async def predict_cost_difference(
        self,
        metric_period: MetricPeriod,
        energy: float,
        accurate_day_count: int,
        date: datetime.date,
    ) -> float:
        """Predict the cost difference."""

        predicted_energy = await self.predict_energy(
            metric_period, energy, accurate_day_count, date
        )
        predicted_cost_difference = await self.calculate_cost_difference(
            metric_period, predicted_energy, date
        )

        return predicted_cost_difference
