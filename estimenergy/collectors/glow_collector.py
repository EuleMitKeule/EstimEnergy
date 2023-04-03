
import asyncio
import datetime
import logging
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

from estimenergy.collectors import Collector
from estimenergy.models import CollectorData, EnergyData
from estimenergy.metrics import CollectorMetrics
from estimenergy.helpers import get_current_datetime


class GlowCollector(Collector):
    def __init__(
        self,
        collector_data: CollectorData
    ):
        self.collector_data = collector_data
        self.logger = logging.getLogger("estimenergy").getChild(self.collector_data.name)

        self.logger.info(f"Creating API Client for {self.collector_data.name} ({self.collector_data.host}:{self.collector_data.port})")

        self.zeroconf = Zeroconf()
        self.api = APIClient(
            self.collector_data.host,
            self.collector_data.port,
            self.collector_data.password,
            zeroconf_instance=self.zeroconf,
        )
        self.reconnect_logic = ReconnectLogic(        
            client=self.api,
            on_connect=self.__on_connect,
            on_disconnect=self.__on_disconnect,
            zeroconf_instance=self.zeroconf,
            name=self.collector_data.name,
            on_connect_error=self.__on_connect_error,
        )
        
        self.metrics = CollectorMetrics(self.collector_data)

    async def start(self):
        if not await self.__try_login():
            self.logger.error(f"Unable to login to {self.collector_data.name}")
            return
        await self.reconnect_logic.start()

    async def update_kwh(self, kwh: float):
        return await self.__on_kwh_changed(kwh)

    async def __try_login(self):
        try:
            await self.api.connect(login=True)
            self.device_info = await self.api.device_info()
            return True
        except (
            ResolveAPIError, 
            APIConnectionError, 
            InvalidEncryptionKeyAPIError, 
            RequiresEncryptionAPIError
        ):
            return False
        finally:
            await self.api.disconnect(force=True)

    async def __on_connect(self):
        self.logger.info(f"Connected to ESPHome Device {self.collector_data.name}")

        try:
            await self.api.subscribe_states(self.__state_changed)
        except APIConnectionError:
            await self.api.disconnect()
    
    async def __on_disconnect(self):
        self.logger.warn(f"Disconnected from ESPHome Device {self.collector_data.name}")

    async def __on_connect_error(self, exception: Exception):
        self.logger.error(f"Error connecting to ESPHome Device {self.collector_data.name}")
        self.logger.error(exception)

    def __state_changed(self, state: EntityState):
        if state.key != 3673186328:
            return

        current_kwh: float = state.state
        loop = asyncio.get_event_loop()
        loop.create_task(self.__on_kwh_changed(current_kwh))
    
    async def __on_kwh_changed(self, current_kwh: float):
        date = get_current_datetime()

        self.logger.info(f"Current KWh: {current_kwh}")

        energy_data = await EnergyData.filter(collector=self.collector_data, year=date.year, month=date.month, day=date.day).first()
        previous_energy_data = await self.__get_previous_energy_data(date)
        
        if energy_data is None:
            if previous_energy_data is not None and current_kwh > previous_energy_data.kwh:
                previous_energy_data.kwh = current_kwh
                previous_energy_data.hour_updated = 23
                previous_energy_data.is_completed = True
                await previous_energy_data.save()
                return                

            energy_data = EnergyData(
                collector=self.collector_data,
                year=date.year,
                month=date.month,
                day=date.day,
                kwh=current_kwh,
                hour_created=date.hour,
                hour_updated=date.hour,
                is_completed=False
            )

            await energy_data.save()
            await self.__update_previous_energy_data(date)
            return
        
        if energy_data.kwh > current_kwh:
            return
        
        energy_data.kwh = current_kwh
        energy_data.hour_updated = date.hour
        await energy_data.save()
        await self.metrics.update_metrics()

    async def __update_previous_energy_data(self, date):
        previous_energy_data = await self.__get_previous_energy_data(date)

        if previous_energy_data is None:
            return
        
        if previous_energy_data.hour_updated < 23:
            return
        
        previous_energy_data.is_completed = True
        await previous_energy_data.save()

    async def __get_previous_energy_data(self, date):
        date_yesterday = date - datetime.timedelta(days=1)
        return await EnergyData.filter(
            collector=self.collector_data,
            year=date_yesterday.year,
            month=date_yesterday.month,
            day=date_yesterday.day
        ).first()
