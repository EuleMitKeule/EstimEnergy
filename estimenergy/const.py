from enum import Enum

from prometheus_client import Gauge

API_PREFIX = "/api"

DEFAULT_CONFIG_PATH = "config.yml"
DEFAULT_LOG_PATH = "estimenergy.log"
DEFAULT_LOG_LEVEL = "INFO"

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 12321

DEFAULT_INFLUXDB_HOST = "127.0.0.1"
DEFAULT_INFLUXDB_PORT = 8086
DEFAULT_INFLUXDB_USERNAME = "estimenergy"

SENSOR_TYPE_JSON = "json"
SENSOR_TYPE_FRIENDLY_NAME = "friendly_name"
SENSOR_TYPE_UNIQUE_ID = "unique_id"

RESPONSE_DEVICE_NOT_FOUND = "Device not found"
RESPONSE_DEVICE_FAILED_TO_START = "Device failed to start"
RESPONSE_DEVICE_DELETED = "Device deleted"
RESPONSE_DAY_NOT_FOUND = "Day not found"


class DeviceType(Enum):
    GLOW = "glow"


class MetricPeriod(Enum):
    DAY = ("day", "Daily")
    MONTH = ("month", "Monthly")
    YEAR = ("year", "Yearly")
    TOTAL = ("total", "Total")


class MetricType(Enum):
    COST = ("cost", "Cost")
    COST_DIFFERENCE = ("cost_difference", "Cost Difference")
    ENERGY = ("energy", "Energy")
    ACCURACY = ("accuracy", "Accuracy")
    POWER = ("power", "Power")


class Metric:
    def __init__(
        self,
        metric_type: MetricType,
        metric_period: MetricPeriod,
        is_predicted: bool,
        is_raw: bool,
    ):
        self.metric_type = metric_type
        self.metric_period = metric_period
        self.is_predicted = is_predicted
        self.is_raw = is_raw

    @property
    def key(self) -> str:
        return f"{self.metric_type.value[0]}{'_predicted' if self.is_predicted else ''}{'_raw' if self.is_raw else ''}"

    @property
    def metric_key(self) -> str:
        return f"estimenergy_{self.metric_period.value[0]}_{self.metric_type.value[0]}{'_predicted' if self.is_predicted else ''}{'_raw' if self.is_raw else ''}"

    @property
    def friendly_name(self) -> str:
        return f"{self.metric_period.value[1]} {self.metric_type.value[1]} {'(Predicted)' if self.is_predicted else ''} {'(Raw)' if self.is_raw else ''}"

    def create_gauge(self, registry) -> Gauge:
        return Gauge(
            f"{self.metric_key}",
            f"EstimEnergy {self.friendly_name}",
            ["name"],
            registry=registry,
        )

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Metric):
            return (
                self.metric_type == __value.metric_type
                and self.metric_period == __value.metric_period
                and self.is_predicted == __value.is_predicted
                and self.is_raw == __value.is_raw
            )
        return False

    def __hash__(self) -> int:
        return hash(
            (self.metric_type, self.metric_period, self.is_predicted, self.is_raw)
        )


METRICS = [
    Metric(MetricType.ENERGY, MetricPeriod.DAY, False, False),
    Metric(MetricType.ENERGY, MetricPeriod.MONTH, False, False),
    Metric(MetricType.ENERGY, MetricPeriod.YEAR, False, False),
    Metric(MetricType.ENERGY, MetricPeriod.TOTAL, False, False),
    Metric(MetricType.ENERGY, MetricPeriod.MONTH, True, False),
    Metric(MetricType.ENERGY, MetricPeriod.YEAR, True, False),
    Metric(MetricType.ENERGY, MetricPeriod.MONTH, True, True),
    Metric(MetricType.ENERGY, MetricPeriod.YEAR, True, True),
    Metric(MetricType.COST, MetricPeriod.DAY, False, False),
    Metric(MetricType.COST, MetricPeriod.MONTH, False, False),
    Metric(MetricType.COST, MetricPeriod.YEAR, False, False),
    Metric(MetricType.COST, MetricPeriod.TOTAL, False, False),
    Metric(MetricType.COST, MetricPeriod.MONTH, True, False),
    Metric(MetricType.COST, MetricPeriod.YEAR, True, False),
    Metric(MetricType.COST, MetricPeriod.MONTH, True, True),
    Metric(MetricType.COST, MetricPeriod.YEAR, True, True),
    Metric(MetricType.COST_DIFFERENCE, MetricPeriod.DAY, False, False),
    Metric(MetricType.COST_DIFFERENCE, MetricPeriod.MONTH, False, False),
    Metric(MetricType.COST_DIFFERENCE, MetricPeriod.YEAR, False, False),
    Metric(MetricType.COST_DIFFERENCE, MetricPeriod.MONTH, True, False),
    Metric(MetricType.COST_DIFFERENCE, MetricPeriod.YEAR, True, False),
    Metric(MetricType.COST_DIFFERENCE, MetricPeriod.MONTH, True, True),
    Metric(MetricType.COST_DIFFERENCE, MetricPeriod.YEAR, True, True),
    Metric(MetricType.ACCURACY, MetricPeriod.DAY, False, False),
    Metric(MetricType.ACCURACY, MetricPeriod.MONTH, False, False),
    Metric(MetricType.ACCURACY, MetricPeriod.YEAR, False, False),
]

JSON_NAME = "name"
JSON_HOST = "host"
JSON_PORT = "port"
JSON_COST_PER_KWH = "cost_per_kwh"
JSON_BASE_COST_PER_MONTH = "base_cost_per_month"
JSON_PAYMENT_PER_MONTH = "payment_per_month"
JSON_MIN_HOUR = "min_hour"
JSON_MAX_HOUR = "max_hour"
JSON_MAX_INCOMPLETE_DAYS = "max_incomplete_days"
JSON_BILLING_MONTH = "billing_month"
JSON_DATA = "data"

LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)-25s %(name)-30s %(levelname)-8s %(message)s",
        },
        "file": {
            "format": "%(asctime)-25s %(name)-30s %(levelname)-8s %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "formatter": "file",
            "class": "logging.FileHandler",
            "filename": "estimenergy.log",
        },
    },
    "loggers": {
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["default", "file"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["access", "file"],
            "propagate": False,
        },
        "estimenergy": {
            "level": "INFO",
            "handlers": ["default", "file"],
            "propagate": False,
        },
    },
}
