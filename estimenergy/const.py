
from enum import Enum
from prometheus_client import Gauge

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 12321

SENSOR_TYPE_JSON = "json"
SENSOR_TYPE_FRIENDLY_NAME = "friendly_name"
SENSOR_TYPE_UNIQUE_ID = "unique_id"

class MetricPeriod(Enum):
    DAY = ("day", "Daily")
    MONTH = ("month", "Monthly")
    YEAR = ("year", "Yearly")
    TOTAL = ("total", "Total")

class MetricType(Enum):
    COST = ("cost", "Cost")
    COST_DIFFERENCE = ("cost_difference", "Cost Difference")
    ENERGY = ("kwh", "Energy")
    ACCURACY = ("accuracy", "Accuracy")

class Metric:
    def __init__(self, metric_type: MetricType, metric_period: MetricPeriod, is_predicted: bool, is_raw: bool):
        self.metric_type = metric_type
        self.metric_period = metric_period
        self.is_predicted = is_predicted
        self.is_raw = is_raw
        
    @property
    def json_key(self) -> str:
        return f"estimenergy_{self.metric_period.value[0]}_{self.metric_type.value[0]}{'_predicted' if self.is_predicted else ''}{'_raw' if self.is_raw else ''}"

    @property
    def friendly_name(self) -> str:
        return f"{self.metric_period.value[1]} {self.metric_type.value[1]} {'(Predicted)' if self.is_predicted else ''} {'(Raw)' if self.is_raw else ''}"
    
    def create_gauge(self, registry) -> Gauge:
        return Gauge(
            f"{self.json_key}",
            f"EstimEnergy {self.friendly_name}",
            ["name", "id"],
            registry=registry
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

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.ColourizedFormatter",
            "format": "%(asctime)-25s %(name)-30s %(levelprefix)-8s %(message)s",
        },
        "file": {
            "()": "uvicorn.logging.ColourizedFormatter",
            "format": "%(asctime)-25s %(name)-30s %(levelprefix)-8s %(message)s",
            "use_colors": False
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
            "filename": "energy_collector.log",
        }
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
