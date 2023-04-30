"""InfluxDB data service."""
import datetime

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.flux_table import FluxRecord, FluxTable
from influxdb_client.client.write_api import SYNCHRONOUS

from estimenergy.const import Metric, MetricPeriod, MetricType
from estimenergy.influx import influx_client
from estimenergy.services.data_service import DataService


class InfluxService(DataService):
    """InfluxDB data service."""

    @property
    def supported_metrics(self) -> list[Metric]:
        """Return a list of metrics supported by this service."""
        return [
            Metric(
                MetricType.ENERGY,
                MetricPeriod.TOTAL,
                False,
                False,
            ),
            Metric(
                MetricType.COST,
                MetricPeriod.TOTAL,
                False,
                False,
            ),
            Metric(
                MetricType.POWER,
                MetricPeriod.TOTAL,
                False,
                False,
            ),
        ]

    async def _last(
        self,
        metric: Metric,
        value_dt: datetime.datetime,
    ) -> float:
        """Get the last value for a metric type."""

        if self.config.influx_config is None:
            return 0

        if metric.metric_period != MetricPeriod.TOTAL:
            return 0

        if metric.metric_type not in [MetricType.ENERGY, MetricType.COST]:
            return 0

        timestamp = value_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        result: list[FluxTable] = influx_client.query_api().query(
            f'from(bucket:"{self.config.influx_config.bucket}") |> range(start: 0) |> filter(fn: (r) => r._measurement == "energy" and r._field == "{metric.metric_type.value[0]}") |> filter(fn: (r) => r._time >= {timestamp}) |> sort(columns: ["_time"], desc: false) |> limit(n: 1)'
        )

        if len(result) == 0:
            return 0

        last_data: FluxTable = result[0]
        records: list[FluxRecord] = last_data.records

        if len(records) == 0:
            return 0

        last_record: FluxRecord = records[0]
        return last_record.get_value()

    async def _write(
        self,
        metric: Metric,
        value: float,
        value_dt: datetime.datetime,
    ):
        """Write a metric to the database."""

        if self.config.influx_config is None:
            return

        point: str = (
            Point("energy")
            .tag("device", self.device_config.name)
            .time(value_dt.isoformat())
            .field(metric.metric_type.value[0], value)
            .to_line_protocol()
        )

        influx_client.write_api(write_options=SYNCHRONOUS).write(
            bucket=self.config.influx_config.bucket,
            org=self.config.influx_config.org,
            record=point,
        )

    async def update(
        self,
        value_dt: datetime.datetime,
    ):
        """Update the database with the latest values."""
        _ = value_dt
