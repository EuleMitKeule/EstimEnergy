"""Logging configuration for estimenergy."""
import logging
from logging import config as logging_config

from estimenergy.config import config
from estimenergy.const import LOGGING_CONFIG

LOGGING_CONFIG["handlers"]["file"]["filename"] = config.logging_config.log_path
LOGGING_CONFIG["loggers"]["uvicorn.error"]["level"] = config.logging_config.log_level
LOGGING_CONFIG["loggers"]["uvicorn.access"]["level"] = config.logging_config.log_level
LOGGING_CONFIG["loggers"]["estimenergy"]["level"] = config.logging_config.log_level

logging_config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger("estimenergy")
