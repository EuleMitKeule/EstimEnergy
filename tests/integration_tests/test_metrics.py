import os
from httpx import AsyncClient
import pytest
from estimenergy.main import app
from fastapi.testclient import TestClient

from estimenergy.models.collector_data import CollectorData

client = TestClient(app)

@pytest.mark.asyncio
async def test_metrics(client: AsyncClient):
    # collector_data = await CollectorData.create(
    #     id=1,
    #     name="glow_test",
    #     host="0.0.0.0",
    #     port=0,
    #     password="",
    #     cost_per_kwh=1,
    #     base_cost_per_month=1,
    #     payment_per_month=100,
    #     billing_month=1,
    #     min_accuracy=0
    #     )
    # await collector_data.save()
    # collector_data = await CollectorData.filter(name="glow_test", id=1)
    # assert collector_data is not None

    # response = client.get("/metrics")
    # assert response.status_code == 200
    # assert os.environ["DB_PATH"] == "test.db"
    # print(response.content)

    collector_datas = await CollectorData.filter().count()
    assert collector_datas == 0
