
import logging
import os
from prometheus_client import CollectorRegistry
from prometheus_fastapi_instrumentator import Instrumentator
from dotenv import load_dotenv

from estimenergy.models.settings import Settings


load_dotenv()

settings = Settings()
collector_registry = CollectorRegistry()
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=[".*admin.*", "/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="inprogress",
    inprogress_labels=True,
)