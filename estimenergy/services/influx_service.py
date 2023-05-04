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

    async def write(
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
