import datetime

from prometheus_client import Gauge, Metric as PrometheusMetric

from estimenergy.const import METRICS, Metric
from estimenergy.models.config.config import Config
from estimenergy.models.device_config import DeviceConfig
from estimenergy.prometheus import metric_registry
from estimenergy.services.data_service import DataService
from estimenergy.services.sql_service import SqlService


class PrometheusService(DataService):
    sql_service: SqlService
    gauges: dict[Metric, Gauge]

    def __init__(
        self, sql_service: SqlService, device_config: DeviceConfig, config: Config
    ):
        super().__init__(device_config, config)

        self.sql_service = sql_service
        self.gauges = {}

        for metric in METRICS:
            try:
                self.gauges[metric] = metric.create_gauge(metric_registry).labels(
                    name=device_config.name
                )
            except ValueError:
                pass

    @property
    def supported_metrics(self):
        return []

    async def _last(
        self,
        metric: Metric,
        value_dt: datetime.datetime = datetime.datetime.now(),
    ) -> float:
        _ = metric
        _ = value_dt

        return 0

    async def _write(
        self,
        metric: Metric,
        value: float,
        value_dt: datetime.datetime = datetime.datetime.now(),
    ):
        _ = metric
        _ = value
        _ = value_dt

    async def update(
        self,
        value_dt: datetime.datetime = datetime.datetime.now(),
    ):
        _ = value_dt

        for metric in METRICS:
            last_value = await self.sql_service.last(metric, value_dt)

            self.gauges[metric].set(last_value)
