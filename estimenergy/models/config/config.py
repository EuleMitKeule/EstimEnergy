"""The main config class."""
from typing import Optional

from pydantic import BaseModel, Field
import yaml

from estimenergy.models.config.dev_config import DevConfig
from estimenergy.models.config.influx_config import InfluxConfig
from estimenergy.models.config.logging_config import LoggingConfig
from estimenergy.models.config.networking_config import NetworkingConfig
from estimenergy.models.config.sql_config import SqlConfig
from estimenergy.models.device_config import DeviceConfig


class Config(BaseModel):
    """The main config class."""

    dev_config: DevConfig = Field(DevConfig(), alias="dev")
    networking_config: NetworkingConfig = Field(NetworkingConfig(), alias="networking")
    logging_config: LoggingConfig = Field(LoggingConfig(), alias="logging")
    sql_config: SqlConfig = Field(SqlConfig(), alias="db")
    influx_config: Optional[InfluxConfig] = Field(alias="influxdb")

    @classmethod
    def from_file(cls, config_path: str):
        """Load the config from a file."""

        with open(config_path, "r", encoding="utf-8") as config_file:
            config_dict: dict = yaml.safe_load(config_file)

        config = cls.parse_obj(config_dict)
        return config

    @classmethod
    def with_location(cls, path: str):
        """Create default config with base location."""

        config = Config()
        config.sql_config.url = f"sqlite:///{path}/estimenergy.db"
        config.logging_config.log_path = f"{path}/estimenergy.log"

        return config
