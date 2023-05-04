"""Service for writing and reading data from the SQL database."""
import datetime

from sqlalchemy import extract
from sqlmodel import Session, select
from sqlmodel.sql.expression import SelectOfScalar

from estimenergy.const import Metric, MetricPeriod
from estimenergy.db import db_engine
from estimenergy.models.config.config import Config
from estimenergy.models.day import Day
from estimenergy.models.device_config import DeviceConfig
from estimenergy.models.month import Month
from estimenergy.models.total import Total
from estimenergy.models.year import Year
from estimenergy.services.data_service import DataService
from estimenergy.services.prediction_service import PredictionService


class SqlService(DataService):
    """Service for writing and reading data from the SQL database."""

    prediction_service: PredictionService

    def __init__(self, device_config: DeviceConfig, config: Config):
        super().__init__(device_config, config)

        self.prediction_service = PredictionService(device_config, config)

    async def write(
        self,
        metric: Metric,
        value: float,
        value_dt: datetime.datetime,
    ):
        """Write a metric value."""

        date = value_dt.date()
        row = self.get_or_create_row(metric.metric_period, date)
        setattr(row, metric.key, value)

        with Session(db_engine) as session:
            session.add(row)
            session.commit()

    async def update(
        self,
        value_dt: datetime.datetime,
    ):
        """Update all metrics."""

        date = value_dt.date()
        await self.update_day(date)
        await self.update_month(date)
        await self.update_year(date)
        await self.update_total(date)

    async def last(
        self,
        metric: Metric,
        value_dt: datetime.datetime,
    ) -> float:
        """Get a metric value."""

        date = value_dt.date()
        row = self.get_or_create_row(metric.metric_period, date)
        value = getattr(row, metric.key, 0)

        return value

    async def update_day(
        self,
        date: datetime.date,
    ):
        """Update the day metrics."""

        metric_period = MetricPeriod.DAY

        with Session(db_engine) as session:
            day = self.get_or_create_row(MetricPeriod.DAY, date)

            if not isinstance(day, Day):
                raise TypeError("day is not of type Day")

            day.cost = await self.prediction_service.calculate_cost(
                metric_period,
                day.energy,
                day.date,
            )

            day.cost_difference = (
                await self.prediction_service.calculate_cost_difference(
                    metric_period,
                    day.energy,
                    day.date,
                )
            )

            session.add(day)
            session.commit()

    async def update_month(
        self,
        date: datetime.date,
    ):
        """Update the month metrics."""

        await self.update_accumulative(MetricPeriod.MONTH, date)

    async def update_year(
        self,
        date: datetime.date,
    ):
        """Update the year metrics."""

        await self.update_accumulative(MetricPeriod.YEAR, date)

    async def update_accumulative(
        self,
        metric_period: MetricPeriod,
        date: datetime.date,
    ):
        """Update accumulative metrics."""

        with Session(db_engine) as session:
            row = self.get_or_create_row(metric_period, date)

            if metric_period == MetricPeriod.MONTH:
                recorded_days = session.exec(
                    select(Day).where(
                        Day.month_id == row.id,
                    )
                ).all()
                accurate_days = session.exec(
                    select(Day).where(
                        Day.month_id == row.id,
                        Day.accuracy >= self.device_config.min_accuracy,
                    )
                ).all()
            elif metric_period == MetricPeriod.YEAR:
                recorded_days = session.exec(
                    select(Day).where(
                        Day.year_id == row.id,
                    )
                ).all()
                accurate_days = session.exec(
                    select(Day).where(
                        Day.year_id == row.id,
                        Day.accuracy >= self.device_config.min_accuracy,
                    )
                ).all()
            else:
                raise ValueError(f"Invalid metric period: {metric_period}")

            recorded_day_count = len(recorded_days)
            accurate_day_count = len(accurate_days)

            energy_raw = sum(day.energy for day in recorded_days)
            energy = sum(day.energy for day in accurate_days)
            energy_predicted_raw = await self.prediction_service.predict_energy(
                metric_period,
                energy_raw,
                recorded_day_count,
                date,
            )
            energy_predicted = await self.prediction_service.predict_energy(
                metric_period,
                energy,
                accurate_day_count,
                date,
            )

            cost = await self.prediction_service.calculate_cost(
                metric_period,
                energy_raw,
                date,
            )
            cost_predicted_raw = await self.prediction_service.predict_cost(
                metric_period,
                energy_raw,
                recorded_day_count,
                date,
            )
            cost_predicted = await self.prediction_service.predict_cost(
                metric_period,
                energy,
                accurate_day_count,
                date,
            )

            cost_difference = await self.prediction_service.calculate_cost_difference(
                metric_period,
                energy_raw,
                date,
            )
            cost_difference_predicted_raw = (
                await self.prediction_service.predict_cost_difference(
                    metric_period,
                    energy_raw,
                    recorded_day_count,
                    date,
                )
            )
            cost_difference_predicted = (
                await self.prediction_service.predict_cost_difference(
                    metric_period,
                    energy,
                    accurate_day_count,
                    date,
                )
            )

            accuracy_sum = sum(day.accuracy for day in accurate_days)
            accuracy = await self.prediction_service.calculate_accuracy(
                metric_period,
                accuracy_sum,
                date,
            )

            row.energy = energy_raw
            row.energy_predicted_raw = energy_predicted_raw
            row.energy_predicted = energy_predicted
            row.cost = cost
            row.cost_predicted_raw = cost_predicted_raw
            row.cost_predicted = cost_predicted
            row.cost_difference = cost_difference
            row.cost_difference_predicted_raw = cost_difference_predicted_raw
            row.cost_difference_predicted = cost_difference_predicted
            row.accuracy = accuracy

            session.add(row)
            session.commit()

    async def update_total(self, date: datetime.date):
        """Update the total metrics."""

        metric_period = MetricPeriod.TOTAL

        with Session(db_engine) as session:
            total = self.get_or_create_row(metric_period, date)
            days = session.exec(select(Day)).all()
            energy = sum(day.energy for day in days)

            cost = await self.prediction_service.calculate_cost(
                metric_period,
                energy,
                date,
            )

            total.energy = energy
            total.cost = cost

            session.add(total)
            session.commit()

    def get_or_create_row(
        self,
        metric_period: MetricPeriod,
        date: datetime.date,
    ) -> Day | Month | Year | Total:
        """Get or create a row in the database."""

        row = self.get_row(metric_period, date)

        if row is None:
            row = self.create_row(metric_period, date)

        return row

    def create_row(
        self,
        metric_period: MetricPeriod,
        date: datetime.date,
    ) -> Day | Month | Year | Total:
        """Create a row in the database."""

        if metric_period == MetricPeriod.DAY:
            return self.create_day(date)

        elif metric_period == MetricPeriod.MONTH:
            return self.create_month(date)

        elif metric_period == MetricPeriod.YEAR:
            return self.create_year(date)

        elif metric_period == MetricPeriod.TOTAL:
            return self.create_total()

        else:
            raise ValueError(f"Unknown metric period {metric_period}")

    def create_day(
        self,
        date: datetime.date,
    ) -> Day:
        """Create a day in the database."""

        with Session(db_engine, expire_on_commit=False) as session:
            row = Day(device_name=self.device_config.name, date=date)
            session.add(row)
            session.commit()
            month = session.exec(
                select(Month).where(
                    extract("month", Month.date) == date.month,
                    extract("year", Month.date) == date.year,
                    Month.device_name == self.device_config.name,
                )
            ).first()
            if month is not None:
                row.month_id = month.id

            session.add(row)
            session.commit()

        return row

    def create_month(
        self,
        date: datetime.date,
    ) -> Month:
        """Create a month in the database."""

        with Session(db_engine, expire_on_commit=False) as session:
            date = date.replace(day=1)
            row = Month(device_name=self.device_config.name, date=date)
            session.add(row)
            session.commit()
            days = session.exec(
                select(Day).where(
                    extract("month", Day.date) == date.month,
                    extract("year", Day.date) == date.year,
                    Day.device_name == self.device_config.name,
                )
            ).all()
            for day in days:
                day.month_id = row.id
                session.add(day)
            year = session.exec(
                select(Year).where(
                    extract("year", Year.date) == date.year
                    and extract("month", Year.date) <= date.month
                    or extract("year", Year.date) == date.year + 1
                    and extract("month", Year.date) > date.month,
                    Year.device_name == self.device_config.name,
                )
            ).first()
            if year is not None:
                row.year_id = year.id

            session.commit()

        return row

    def create_year(
        self,
        date: datetime.date,
    ) -> Year:
        """Create a year in the database."""

        with Session(db_engine, expire_on_commit=False) as session:
            date = date.replace(
                year=date.year - 1
                if date.month <= self.device_config.billing_month
                else date.year,
                month=self.device_config.billing_month,
                day=1,
            )
            row = Year(device_name=self.device_config.name, date=date)
            session.add(row)
            session.commit()
            months = session.exec(
                select(Month).where(
                    extract("year", Month.date) == date.year
                    and extract("month", Month.date) >= date.month
                    or extract("year", Month.date) == date.year + 1
                    and extract("month", Month.date) < date.month,
                    Month.device_name == self.device_config.name,
                )
            ).all()
            for month in months:
                month.year_id = row.id
                session.add(month)
            days = session.exec(
                select(Day).where(
                    extract("year", Day.date) == date.year
                    and extract("month", Day.date) >= date.month
                    or extract("year", Day.date) == date.year + 1
                    and extract("month", Day.date) < date.month,
                    Day.device_name == self.device_config.name,
                )
            ).all()
            for day in days:
                day.year_id = row.id
                session.add(day)

            session.commit()

        return row

    def create_total(self) -> Total:
        """Create a total in the database."""

        with Session(db_engine, expire_on_commit=False) as session:
            row = Total(device_name=self.device_config.name)

            session.add(row)
            session.commit()

        return row

    def get_rows(
        self,
        metric_period: MetricPeriod,
        date: datetime.date,
    ) -> list[Day] | list[Month] | list[Year] | list[Total]:
        """Get rows from the database."""

        query: SelectOfScalar[Day] | SelectOfScalar[Month] | SelectOfScalar[
            Year
        ] | SelectOfScalar[Total]

        with Session(db_engine, expire_on_commit=False) as session:
            if metric_period == MetricPeriod.DAY:
                query = select(Day).where(
                    Day.date == date,
                    Day.device_name == self.device_config.name,
                )
            elif metric_period == MetricPeriod.MONTH:
                date = date.replace(day=1)
                query = select(Month).where(
                    Month.date == date,
                    Month.device_name == self.device_config.name,
                )
            elif metric_period == MetricPeriod.YEAR:
                date = date.replace(
                    year=date.year - 1
                    if date.month <= self.device_config.billing_month
                    else date.year,
                    month=self.device_config.billing_month,
                    day=1,
                )
                query = select(Year).where(
                    Year.date == date,
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
        date: datetime.date,
    ) -> Day | Month | Year | Total | None:
        """Get a row from the database."""

        rows = self.get_rows(metric_period, date)

        if len(rows) == 0:
            return None

        return rows[0]
