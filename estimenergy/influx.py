from influxdb_client import InfluxDBClient

from estimenergy.config import config

if config.influx_config:
    influx_client: InfluxDBClient = InfluxDBClient(
        url=config.influx_config.url,
        token=config.influx_config.token,
        org=config.influx_config.org,
    )
else:
    influx_client = None
