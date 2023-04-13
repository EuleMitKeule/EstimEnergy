import os
from dotenv import load_dotenv
from prometheus_client import CollectorRegistry
from prometheus_fastapi_instrumentator import Instrumentator
from influxdb_client import InfluxDBClient
from sqlmodel import create_engine
from estimenergy.const import DEFAULT_CONFIG_PATH
from estimenergy.models.config.config import Config

load_dotenv()

config_path = os.getenv("CONFIG_PATH", DEFAULT_CONFIG_PATH)
config = Config.from_file(config_path)

if config.influx_config:
    influx_client = InfluxDBClient(
        url=config.influx_config.url,
        token=config.influx_config.token.get_secret_value(),
        org=config.influx_config.org,
    )

db_engine = create_engine(config.sql_config.url)
metric_registry = CollectorRegistry()
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=False,
    should_instrument_requests_inprogress=True,
    excluded_handlers=[".*admin.*", "/metrics"],
    inprogress_name="inprogress",
    inprogress_labels=True,
    registry=metric_registry,
)
