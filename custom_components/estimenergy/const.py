"""Constants for EstimEnergy"""
from homeassistant.const import Platform

PLATFORM = Platform.SENSOR
DOMAIN = "estimenergy"

CONF_NAME = "collector_name"
CONF_HOST = "host"
CONF_PORT = "port"

SENSOR_DAY_KWH = "current_day_kwh"
SENSOR_DAY_COST = "current_day_cost"
SENSOR_DAY_COST_DIFFERENCE = "current_day_cost_difference"
SENSOR_MONTH_KWH_RAW = "predicted_month_kwh_raw"
SENSOR_MONTH_COST_RAW = "predicted_month_cost_raw"
SENSOR_MONTH_COST_DIFFERENCE_RAW = "predicted_month_cost_difference_raw"
SENSOR_YEAR_KWH_RAW = "predicted_year_kwh_raw"
SENSOR_YEAR_COST_RAW = "predicted_year_cost_raw"
SENSOR_YEAR_COST_DIFFFERENCE_RAW = "predicted_year_cost_difference_raw"
SENSOR_MONTH_KWH = "predicted_month_kwh"
SENSOR_MONTH_COST = "predicted_month_cost"
SENSOR_MONTH_COST_DIFFERENCE = "predicted_month_cost_difference"
SENSOR_YEAR_KWH = "predicted_year_kwh"
SENSOR_YEAR_COST = "predicted_year_cost"
SENSOR_YEAR_COST_DIFFFERENCE = "predicted_year_cost_difference"

SENSOR_TYPES = [
    SENSOR_DAY_KWH,
    SENSOR_DAY_COST,
    SENSOR_DAY_COST_DIFFERENCE,
    SENSOR_MONTH_KWH_RAW,
    SENSOR_MONTH_COST_RAW,
    SENSOR_MONTH_COST_DIFFERENCE_RAW,
    SENSOR_YEAR_KWH_RAW,
    SENSOR_YEAR_COST_RAW,
    SENSOR_YEAR_COST_DIFFFERENCE_RAW,
    SENSOR_MONTH_KWH,
    SENSOR_MONTH_COST,
    SENSOR_MONTH_COST_DIFFERENCE,
    SENSOR_YEAR_KWH,
    SENSOR_YEAR_COST,
    SENSOR_YEAR_COST_DIFFFERENCE,
]

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8000

SENSOR_TYPE_TO_UNIT = {
    SENSOR_DAY_KWH: "kWh",
    SENSOR_DAY_COST: "€",
    SENSOR_DAY_COST_DIFFERENCE: "€",
    SENSOR_MONTH_KWH_RAW: "kWh",
    SENSOR_MONTH_COST_RAW: "€",
    SENSOR_MONTH_COST_DIFFERENCE_RAW: "€",
    SENSOR_YEAR_KWH_RAW: "kWh",
    SENSOR_YEAR_COST_RAW: "€",
    SENSOR_YEAR_COST_DIFFFERENCE_RAW: "€",
    SENSOR_MONTH_KWH: "kWh",
    SENSOR_MONTH_COST: "€",
    SENSOR_MONTH_COST_DIFFERENCE: "€",
    SENSOR_YEAR_KWH: "kWh",
    SENSOR_YEAR_COST: "€",
    SENSOR_YEAR_COST_DIFFFERENCE: "€",
}
