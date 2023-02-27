"""Constants for EstimEnergy"""
from homeassistant.const import Platform

PLATFORM = Platform.SENSOR
DOMAIN = "estimenergy"

CONF_NAME = "collector_name"
CONF_HOST = "host"
CONF_PORT = "port"

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8000