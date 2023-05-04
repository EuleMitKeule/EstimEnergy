"""Constants for EstimEnergy"""
from enum import Enum
from homeassistant.const import Platform


PLATFORM = Platform.SENSOR
DOMAIN = "estimenergy_integration"

CONF_HOST = "host"
CONF_PORT = "port"

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 12321


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
