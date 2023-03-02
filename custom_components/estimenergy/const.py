"""Constants for EstimEnergy"""
from homeassistant.const import Platform, CONF_FRIENDLY_NAME, CONF_UNIQUE_ID

PLATFORM = Platform.SENSOR
DOMAIN = "estimenergy"

SENSOR_TYPE_JSON = "json"
SENSOR_TYPE_FRIENDLY_NAME = CONF_FRIENDLY_NAME
SENSOR_TYPE_UNIQUE_ID = CONF_UNIQUE_ID

CONF_NAME = "collector_name"
CONF_HOST = "host"
CONF_PORT = "port"

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8000

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

JSON_DAY_KWH = "day_kwh"
FRIENDLY_DAY_KWH = "Daily Energy Usage"
UNIQUE_ID_DAY_KWH = "day_kwh"

JSON_DAY_COST = "day_cost"
FRIENDLY_DAY_COST = "Daily Energy Cost"
UNIQUE_ID_DAY_COST = "day_cost"

JSON_DAY_COST_DIFFERENCE = "day_cost_difference"
FRIENDLY_DAY_COST_DIFFERENCE = "Daily Energy Cost Difference"
UNIQUE_ID_DAY_COST_DIFFERENCE = "day_cost_difference"

JSON_MONTH_KWH_RAW = "predicted_month_kwh_raw"
FRIENDLY_MONTH_KWH_RAW = "Predicted Monthly Energy Usage Raw"
UNIQUE_ID_MONTH_KWH_RAW = "predicted_month_kwh_raw"

JSON_MONTH_COST_RAW = "predicted_month_cost_raw"
FRIENDLY_MONTH_COST_RAW = "Predicted Monthly Energy Cost Raw"
UNIQUE_ID_MONTH_COST_RAW = "predicted_month_cost_raw"

JSON_MONTH_COST_DIFFERENCE_RAW = "predicted_month_cost_difference_raw"
FRIENDLY_MONTH_COST_DIFFERENCE_RAW = "Predicted Monthly Energy Cost Difference Raw"
UNIQUE_ID_MONTH_COST_DIFFERENCE_RAW = "predicted_month_cost_difference_raw"

JSON_YEAR_KWH_RAW = "predicted_year_kwh_raw"
FRIENDLY_YEAR_KWH_RAW = "Predicted Yearly Energy Usage Raw"
UNIQUE_ID_YEAR_KWH_RAW = "predicted_year_kwh_raw"

JSON_YEAR_COST_RAW = "predicted_year_cost_raw"
FRIENDLY_YEAR_COST_RAW = "Predicted Yearly Energy Cost Raw"
UNIQUE_ID_YEAR_COST_RAW = "predicted_year_cost_raw"

JSON_YEAR_COST_DIFFERENCE_RAW = "predicted_year_cost_difference_raw"
FRIENDLY_YEAR_COST_DIFFERENCE_RAW = "Predicted Yearly Energy Cost Difference Raw"
UNIQUE_ID_YEAR_COST_DIFFERENCE_RAW = "predicted_year_cost_difference_raw"

JSON_MONTH_KWH = "predicted_month_kwh"
FRIENDLY_MONTH_KWH = "Predicted Monthly Energy Usage"
UNIQUE_ID_MONTH_KWH = "predicted_month_kwh"

JSON_MONTH_COST = "predicted_month_cost"
FRIENDLY_MONTH_COST = "Predicted Monthly Energy Cost"
UNIQUE_ID_MONTH_COST = "predicted_month_cost"

JSON_MONTH_COST_DIFFERENCE = "predicted_month_cost_difference"
FRIENDLY_MONTH_COST_DIFFERENCE = "Predicted Monthly Energy Cost Difference"
UNIQUE_ID_MONTH_COST_DIFFERENCE = "predicted_month_cost_difference"

JSON_YEAR_KWH = "predicted_year_kwh"
FRIENDLY_YEAR_KWH = "Predicted Yearly Energy Usage"
UNIQUE_ID_YEAR_KWH = "predicted_year_kwh"

JSON_YEAR_COST = "predicted_year_cost"
FRIENDLY_YEAR_COST = "Predicted Yearly Energy Cost"
UNIQUE_ID_YEAR_COST = "predicted_year_cost"

JSON_YEAR_COST_DIFFFERENCE = "predicted_year_cost_difference"
FRIENDLY_YEAR_COST_DIFFFERENCE = "Predicted Yearly Energy Cost Difference"
UNIQUE_ID_YEAR_COST_DIFFFERENCE = "predicted_year_cost_difference"

SENSOR_TYPES = [
    {
        SENSOR_TYPE_JSON: JSON_DAY_KWH,
        SENSOR_TYPE_FRIENDLY_NAME: FRIENDLY_DAY_KWH,
        SENSOR_TYPE_UNIQUE_ID: UNIQUE_ID_DAY_KWH,
    },
    {
        SENSOR_TYPE_JSON: JSON_DAY_COST,
        SENSOR_TYPE_FRIENDLY_NAME: FRIENDLY_DAY_COST,
        SENSOR_TYPE_UNIQUE_ID: UNIQUE_ID_DAY_COST,
    },
    {
        SENSOR_TYPE_JSON: JSON_DAY_COST_DIFFERENCE,
        SENSOR_TYPE_FRIENDLY_NAME: FRIENDLY_DAY_COST_DIFFERENCE,
        SENSOR_TYPE_UNIQUE_ID: UNIQUE_ID_DAY_COST_DIFFERENCE,
    },
    {
        SENSOR_TYPE_JSON: JSON_MONTH_KWH_RAW,
        SENSOR_TYPE_FRIENDLY_NAME: FRIENDLY_MONTH_KWH_RAW,
        SENSOR_TYPE_UNIQUE_ID: UNIQUE_ID_MONTH_KWH_RAW,
    },
    {
        SENSOR_TYPE_JSON: JSON_MONTH_COST_RAW,
        SENSOR_TYPE_FRIENDLY_NAME: FRIENDLY_MONTH_COST_RAW,
        SENSOR_TYPE_UNIQUE_ID: UNIQUE_ID_MONTH_COST_RAW,
    },
    {
        SENSOR_TYPE_JSON: JSON_MONTH_COST_DIFFERENCE_RAW,
        SENSOR_TYPE_FRIENDLY_NAME: FRIENDLY_MONTH_COST_DIFFERENCE_RAW,
        SENSOR_TYPE_UNIQUE_ID: UNIQUE_ID_MONTH_COST_DIFFERENCE_RAW,
    },
    {
        SENSOR_TYPE_JSON: JSON_YEAR_KWH_RAW,
        SENSOR_TYPE_FRIENDLY_NAME: FRIENDLY_YEAR_KWH_RAW,
        SENSOR_TYPE_UNIQUE_ID: UNIQUE_ID_YEAR_KWH_RAW,
    },
    {
        SENSOR_TYPE_JSON: JSON_YEAR_COST_RAW,
        SENSOR_TYPE_FRIENDLY_NAME: FRIENDLY_YEAR_COST_RAW,
        SENSOR_TYPE_UNIQUE_ID: UNIQUE_ID_YEAR_COST_RAW,
    },
    {
        SENSOR_TYPE_JSON: JSON_YEAR_COST_DIFFERENCE_RAW,
        SENSOR_TYPE_FRIENDLY_NAME: FRIENDLY_YEAR_COST_DIFFERENCE_RAW,
        SENSOR_TYPE_UNIQUE_ID: UNIQUE_ID_YEAR_COST_DIFFERENCE_RAW,
    },
    {
        SENSOR_TYPE_JSON: JSON_MONTH_KWH,
        SENSOR_TYPE_FRIENDLY_NAME: FRIENDLY_MONTH_KWH,
        SENSOR_TYPE_UNIQUE_ID: UNIQUE_ID_MONTH_KWH,
    },
    {
        SENSOR_TYPE_JSON: JSON_MONTH_COST,
        SENSOR_TYPE_FRIENDLY_NAME: FRIENDLY_MONTH_COST,
        SENSOR_TYPE_UNIQUE_ID: UNIQUE_ID_MONTH_COST,
    },
    {
        SENSOR_TYPE_JSON: JSON_MONTH_COST_DIFFERENCE,
        SENSOR_TYPE_FRIENDLY_NAME: FRIENDLY_MONTH_COST_DIFFERENCE,
        SENSOR_TYPE_UNIQUE_ID: UNIQUE_ID_MONTH_COST_DIFFERENCE,
    },
    {
        SENSOR_TYPE_JSON: JSON_YEAR_KWH,
        SENSOR_TYPE_FRIENDLY_NAME: FRIENDLY_YEAR_KWH,
        SENSOR_TYPE_UNIQUE_ID: UNIQUE_ID_YEAR_KWH,
    },
    {
        SENSOR_TYPE_JSON: JSON_YEAR_COST,
        SENSOR_TYPE_FRIENDLY_NAME: FRIENDLY_YEAR_COST,
        SENSOR_TYPE_UNIQUE_ID: UNIQUE_ID_YEAR_COST,
    },
    {
        SENSOR_TYPE_JSON: JSON_YEAR_COST_DIFFFERENCE,
        SENSOR_TYPE_FRIENDLY_NAME: FRIENDLY_YEAR_COST_DIFFFERENCE,
        SENSOR_TYPE_UNIQUE_ID: UNIQUE_ID_YEAR_COST_DIFFFERENCE,
    },
]
