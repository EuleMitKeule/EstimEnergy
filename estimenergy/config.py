"""Configuration module for estimenergy."""
import os

from dotenv import load_dotenv

from estimenergy.const import DEFAULT_CONFIG_PATH
from estimenergy.models.config.config import Config

load_dotenv()

config_path = os.getenv("CONFIG_PATH", DEFAULT_CONFIG_PATH)

if os.path.exists(config_path):
    config = Config.from_file(config_path)
else:
    config_base_path = os.path.dirname(config_path)
    config = Config.with_location(config_base_path)
