"""Service for writing and reading data from the SQL database."""
import datetime
from sqlmodel import Session, select
from estimenergy.const import METRICS, Metric, MetricPeriod, MetricType
from estimenergy.helpers import get_days_in_month, get_days_in_year
from estimenergy.models.day import Day
from estimenergy.models.month import Month
from estimenergy.models.total import Total
from estimenergy.models.year import Year
from estimenergy.services.data_service import DataService
from estimenergy.common import db_engine


class SqlService(DataService):
    """Service for writing and reading data from the SQL database."""

    @property
    def supported_metrics(self) -> list[Metric]:
        return [
            metric
            for metric in METRICS
            if not metric.is_raw and metric.metric_type != MetricType.POWER
        ]

    async def _last(
        self,
        metric: Metric,
        date: datetime.datetime = datetime.datetime.now(),
    ) -> float:
        """Get a metric value."""

        row = self.get_or_create_row(metric.metric_period, date)
        value = getattr(row, metric.key, 0)

        return value

    async def _write(
        self,
        metric: Metric,
        value: float,
        date: datetime.datetime = datetime.datetime.now(),
    ):
        """Write a metric value."""

        row = self.get_or_create_row(metric.metric_period, date)
        setattr(row, metric.key, value)

        with Session(db_engine) as session:
            session.add(row)
            session.commit()

    async def _predict(
        self,
        metric: Metric,
        date: datetime.datetime = datetime.datetime.now(),
    ):
        """Calculate the predicted value for a metric."""

        with Session(db_engine) as session:
            row: Month | Year = self.get_or_create_row(metric.metric_period, date)

            if metric.metric_period == MetricPeriod.MONTH:
                total_days = get_days_in_month(date.month, date.year)
                days = session.exec(select(Day).where(Day.month_id == row.id)).all()
                base_cost = self.device_config.base_cost_per_month
                payment = self.device_config.payment_per_month
            elif metric.metric_period == MetricPeriod.YEAR:
                total_days = get_days_in_year(date.year)
                months = session.exec(
                    select(Month).where(Month.year_id == row.id)
                ).all()
                days = [
                    day
                    for month in months
                    for day in session.exec(
                        select(Day).where(Day.month_id == month.id)
                    ).all()
                ]
                base_cost = self.device_config.base_cost_per_month * 12
                payment = self.device_config.payment_per_month * 12
            else:
                return

            accurate_days: list[Day] = [
                day for day in days if day.accuracy >= self.device_config.min_accuracy
            ]
            accurate_energy = sum(day.energy for day in accurate_days)
            if len(accurate_days) == 0:
                energy_per_day_predicted = 0
            else:
                energy_per_day_predicted = accurate_energy / len(accurate_days)
            energy_predicted = energy_per_day_predicted * total_days

            if metric.metric_type == MetricType.ENERGY:
                row.energy_predicted = energy_predicted
            elif metric.metric_type == MetricType.COST:
                row.cost_predicted = (
                    energy_predicted * self.device_config.cost_per_kwh + base_cost
                )
            elif metric.metric_type == MetricType.COST_DIFFERENCE:
                row.cost_difference_predicted = (
                    payment
                    - energy_predicted * self.device_config.cost_per_kwh
                    + base_cost
                )

            session.add(row)
            session.commit()

    async def _calculate(
        self, metric: Metric, date: datetime.datetime = datetime.datetime.now()
    ):
        """Calculate the value for a metric."""

        with Session(db_engine) as session:
            row: Day | Month | Year | Total = self.get_or_create_row(
                metric.metric_period, date
            )

            if metric.metric_period == MetricPeriod.DAY:
                days_in_month = get_days_in_month(date.month, date.year)
                total_days = 1
                days = [row]
                base_cost = self.device_config.base_cost_per_month / days_in_month
                payment = self.device_config.payment_per_month / days_in_month
            elif metric.metric_period == MetricPeriod.MONTH:
                total_days = get_days_in_month(date.month, date.year)
                days = session.exec(select(Day).where(Day.month_id == row.id)).all()
                base_cost = self.device_config.base_cost_per_month
                payment = self.device_config.payment_per_month
            elif metric.metric_period == MetricPeriod.YEAR:
                total_days = get_days_in_year(date.year)
                months = session.exec(
                    select(Month).where(Month.year_id == row.id)
                ).all()
                days = [
                    day
                    for month in months
                    for day in session.exec(
                        select(Day).where(Day.month_id == month.id)
                    ).all()
                ]
                base_cost = self.device_config.base_cost_per_month * 12
                payment = self.device_config.payment_per_month * 12
            elif metric.metric_period == MetricPeriod.TOTAL:
                days = self.get_rows(MetricPeriod.DAY)
                total_days = len(days)
                base_cost = 0
                payment = 0

            total_energy = sum(day.energy for day in days)
            total_cost = total_energy * self.device_config.cost_per_kwh + base_cost
            total_cost_difference = payment - total_cost
            accuracy = sum(day.accuracy for day in days) / total_days

            if metric.metric_type == MetricType.ENERGY:
                setattr(row, metric.key, total_energy)
            elif metric.metric_type == MetricType.COST:
                setattr(row, metric.key, total_cost)
            elif metric.metric_type == MetricType.COST_DIFFERENCE:
                setattr(row, metric.key, total_cost_difference)
            elif metric.metric_type == MetricType.ACCURACY:
                setattr(row, metric.key, accuracy)

            session.add(row)
            session.commit()

    def get_or_create_row(
        self,
        metric_period: MetricPeriod,
        value_dt: datetime.datetime = datetime.datetime.now(),
    ) -> Day | Month | Year | Total | None:
        """Get or create a row in the database."""

        row = self.get_row(metric_period, value_dt)
        if row is None:
            row = self.create_row(metric_period, value_dt)

        return row

    def create_row(
        self,
        metric_period: MetricPeriod,
        date: datetime.datetime = datetime.datetime.now(),
    ) -> Day | Month | Year | Total | None:
        """Create a row in the database."""

        with Session(db_engine, expire_on_commit=False) as session:
            if metric_period == MetricPeriod.DAY:
                row = Day(device_config=self.device_config, date=date.date())

            elif metric_period == MetricPeriod.MONTH:
                row = Month(device_config=self.device_config, date=date.date())
                session.add(row)
                session.commit()
                day = self.get_row(MetricPeriod.DAY, date)
                if day is not None:
                    day.month_id = row.id
                    session.add(day)

            elif metric_period == MetricPeriod.YEAR:
                row = Year(device_config=self.device_config, date=date.date())
                session.add(row)
                session.commit()
                month = self.get_row(MetricPeriod.MONTH, date)
                if month is not None:
                    month.year_id = row.id
                    session.add(month)

            elif metric_period == MetricPeriod.TOTAL:
                row = Total(device_config=self.device_config, date=date.date())
            else:
                raise ValueError(f"Unknown metric period {metric_period}")

            session.add(row)
            session.commit()

            return row

    def get_rows(
        self,
        metric_period: MetricPeriod,
        _: datetime.datetime = datetime.datetime.now(),
    ) -> list[Day | Month | Year | Total]:
        """Get rows from the database."""

        with Session(db_engine, expire_on_commit=False) as session:
            if metric_period == MetricPeriod.DAY:
                query = select(Day).where(
                    Day.device_name == self.device_config.name,
                )
            elif metric_period == MetricPeriod.MONTH:
                query = select(Month).where(
                    Month.device_name == self.device_config.name,
                )
            elif metric_period == MetricPeriod.YEAR:
                query = select(Year).where(
                    Year.device_name == self.device_config.name,
                )
            elif metric_period == MetricPeriod.TOTAL:
                query = select(Total).where(
                    Total.device_name == self.device_config.name,
                )
            else:
                raise ValueError(f"Unknown metric period {metric_period}")

            return session.exec(query).all()

    def get_row(
        self,
        metric_period: MetricPeriod,
        date: datetime.datetime = datetime.datetime.now(),
    ) -> Day | Month | Year | Total | None:
        """Get a row from the database."""

        rows = self.get_rows(metric_period, date)

        if len(rows) == 0:
            return None

        return rows[0]
