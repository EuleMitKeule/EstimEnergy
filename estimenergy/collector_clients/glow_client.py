
import asyncio
import logging
from typing import Awaitable
from aioesphomeapi import (
    APIClient,
    EntityState,
    ResolveAPIError,
    APIConnectionError,
    InvalidEncryptionKeyAPIError,
    RequiresEncryptionAPIError,
    ReconnectLogic,
)
from zeroconf import Zeroconf
from estimenergy.collector_clients import CollectorClient


class GlowClient(CollectorClient):
    def __init__(
        self,
        name: str,
        host: str,
        port: int,
        password: str,
        kwh_callback: Awaitable[None],
    ):
        self.name = name
        self.host = host
        self.port = port
        self.password = password
        self.logger = logging.getLogger("energy_collector").getChild(self.name)
        self.kwh_callback = kwh_callback

        self.logger.info(f"Creating API Client for {self.name} ({self.host}:{self.port})")

        self.zeroconf = Zeroconf()
        self.api = APIClient(
            host,
            port,
            password,
            zeroconf_instance=self.zeroconf,
        )
        self.reconnect_logic = ReconnectLogic(        
            client=self.api,
            on_connect=self.__on_connect,
            on_disconnect=self.__on_disconnect,
            zeroconf_instance=self.zeroconf,
            name=name,
            on_connect_error=self.__on_connect_error,
        )

    async def start(self):
        await self.__try_login()
        await self.reconnect_logic.start()

    async def __try_login(self):
        try:
            await self.api.connect(login=True)
            self.device_info = await self.api.device_info()
        except ResolveAPIError or APIConnectionError or InvalidEncryptionKeyAPIError or RequiresEncryptionAPIError as err:
            raise err
        finally:
            await self.api.disconnect(force=True)

    async def __on_connect(self):
        self.logger.info(f"Connected to ESPHome Device {self.name}")

        try:
            await self.api.subscribe_states(self.__state_changed)
        except APIConnectionError as err:
            await self.api.disconnect()
    
    async def __on_disconnect(self):
        self.logger.warn(f"Disconnected from ESPHome Device {self.name}")

    async def __on_connect_error(self, exception: Exception):
        self.logger.error(f"Error connecting to ESPHome Device {self.name}")
        self.logger.error(exception)

    def __state_changed(self, state: EntityState):
        if not state.key == 3673186328:
            return
        
        current_kwh: float = state.state
        loop = asyncio.get_event_loop()
        loop.create_task(self.kwh_callback(current_kwh))
    
