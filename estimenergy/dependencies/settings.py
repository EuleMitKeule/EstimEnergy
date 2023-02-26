
from functools import lru_cache

from estimenergy.models import Settings


@lru_cache()
def get_settings():
    return Settings()
