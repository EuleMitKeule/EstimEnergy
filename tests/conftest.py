# from httpx import AsyncClient
# from prometheus_client.parser import text_string_to_metric_families
# import pytest
# from tortoise import Tortoise

# from estimenergy.config import metric_registry
# from estimenergy.devices.glow_device import GlowDevice
# from estimenergy.main import app
# from estimenergy.models.device_config import CollectorData

# DB_URL = "sqlite://:memory:"


# @pytest.fixture(scope="session")
# def anyio_backend():
#     return "asyncio"


# @pytest.fixture(scope="session")
# async def client():
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         yield client


# @pytest.fixture(scope="function", autouse=True)
# async def initialize_tests():
#     collectors = list(metric_registry._collector_to_names.keys())
#     for collector in collectors:
#         metric_registry.unregister(collector)
#     await Tortoise.init(
#         db_url=DB_URL, modules={"models": ["estimenergy.models"]}, _create_db=True
#     )
#     await Tortoise.generate_schemas()
#     yield
#     await Tortoise._drop_databases()


# @pytest.fixture(scope="function")
# async def create_collector_metrics():
#     async def create_collector_metrics(collector_data: CollectorData):
#         from estimenergy.metrics import CollectorMetrics

#         collector_metrics = CollectorMetrics(collector_data)
#         await collector_metrics.update_metrics()
#         return collector_metrics

#     return create_collector_metrics


# @pytest.fixture(scope="function")
# async def get_metric_value(client: AsyncClient):
#     async def get_metric_value(metric_name: str, collector_name: str):
#         response = await client.get("/metrics")
#         assert response.status_code == 200

#         families = list(text_string_to_metric_families(response.text))
#         for family in families:
#             if family.name == metric_name:
#                 for sample in family.samples:
#                     if sample.labels["name"] == collector_name:
#                         return sample.value

#         return None

#     return get_metric_value


# @pytest.fixture(scope="function")
# async def collector_config():
#     collector_data = await CollectorData.create(
#         name="glow_test",
#         host="0.0.0.0",
#         port=0,
#         password="",
#         cost_per_kwh=1,
#         base_cost_per_month=1,
#         payment_per_month=100,
#         billing_month=1,
#         min_accuracy=0,
#     )
#     await collector_data.save()
#     return collector_data


# @pytest.fixture(scope="function")
# async def glow_collector(collector_data):
#     return GlowDevice(collector_data)
