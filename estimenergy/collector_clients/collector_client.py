

from abc import ABC, abstractmethod


class CollectorClient(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def start(self):
        pass


