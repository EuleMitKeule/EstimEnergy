

from abc import ABC, abstractmethod


class Collector(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def start(self):
        pass


