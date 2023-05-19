import asyncio

import aiohttp
from aioshelly.block_device import COAP, BlockDevice
from aioshelly.common import ConnectionOptions
from aioshelly.exceptions import (
    DeviceConnectionError,
    FirmwareUnsupported,
    InvalidAuthError,
)


async def async_connect():
    options = ConnectionOptions(ip_address="192.168.0.14")

    async with aiohttp.ClientSession() as aiohttp_session, COAP() as coap_context:
        try:
            device = await BlockDevice.create(aiohttp_session, coap_context, options)
        except FirmwareUnsupported as err:
            print(f"Device firmware not supported, error: {repr(err)}")
            return
        except InvalidAuthError as err:
            print(f"Invalid or missing authorization, error: {repr(err)}")
            return
        except DeviceConnectionError as err:
            print(f"Error connecting to {options.ip_address}, error: {repr(err)}")
            return

        for block in device.blocks:
            print(block)
            print(block.current_values())
            print()


def main():
    asyncio.run(async_connect())
