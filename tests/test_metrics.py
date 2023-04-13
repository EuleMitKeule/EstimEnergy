from freezegun import freeze_time
from httpx import AsyncClient
import pytest

from estimenergy.const import Metric, MetricPeriod, MetricType
from estimenergy.models.device_config import CollectorData
from estimenergy.models.obsolete.energy_data import EnergyData


@pytest.mark.anyio
@freeze_time("2023-06-05")
async def test_day_kwh(client: AsyncClient, get_metric_value, create_collector_metrics):
    collector_data = await CollectorData.create(
        name="glow_test",
        host="0.0.0.0",
        port=0,
        password="",
        cost_per_kwh=1,
        base_cost_per_month=1,
        payment_per_month=100,
        billing_month=1,
        min_accuracy=0,
    )
    await collector_data.save()

    created_energy_data = await EnergyData.create(
        collector_id=1,
        year=2023,
        month=6,
        day=5,
        kwh=10,
        hour_created=0,
        hour_updated=23,
        is_completed=True,
    )
    await created_energy_data.save()

    energy_data = await EnergyData.filter(
        collector=collector_data, year=2023, month=6, day=5
    ).first()

    assert energy_data is not None

    assert energy_data.kwh == 10

    await create_collector_metrics(collector_data)
    value = await get_metric_value(
        Metric(
            MetricType.ENERGY, MetricPeriod.DAY, is_predicted=False, is_raw=False
        ).metric_key,
        collector_data.name,
    )

    assert value == 10


@pytest.mark.anyio
@freeze_time("2023-06-05")
async def test_month_kwh(
    client: AsyncClient, get_metric_value, create_collector_metrics
):
    collector_data = await CollectorData.create(
        name="glow_test",
        host="0.0.0.0",
        port=0,
        password="",
        cost_per_kwh=1,
        base_cost_per_month=1,
        payment_per_month=100,
        billing_month=1,
        min_accuracy=0,
    )
    await collector_data.save()

    for day in range(1, 6):
        energy_data = await EnergyData.create(
            collector_id=1,
            year=2023,
            month=6,
            day=day,
            kwh=10,
            hour_created=0,
            hour_updated=23,
            is_completed=True,
        )
        await energy_data.save()

    await create_collector_metrics(collector_data)
    value = await get_metric_value(
        Metric(
            MetricType.ENERGY, MetricPeriod.MONTH, is_predicted=False, is_raw=False
        ).metric_key,
        collector_data.name,
    )

    assert value == 50


@pytest.mark.anyio
@freeze_time("2023-06-05")
async def test_year_kwh(
    client: AsyncClient, get_metric_value, create_collector_metrics
):
    collector_data = await CollectorData.create(
        name="glow_test",
        host="0.0.0.0",
        port=0,
        password="",
        cost_per_kwh=1,
        base_cost_per_month=1,
        payment_per_month=100,
        billing_month=1,
        min_accuracy=0,
    )
    await collector_data.save()

    for month in range(1, 6):
        for day in range(1, 6):
            energy_data = await EnergyData.create(
                collector_id=1,
                year=2023,
                month=month,
                day=day,
                kwh=10,
                hour_created=0,
                hour_updated=23,
                is_completed=True,
            )
            await energy_data.save()

    await create_collector_metrics(collector_data)
    value = await get_metric_value(
        Metric(
            MetricType.ENERGY, MetricPeriod.YEAR, is_predicted=False, is_raw=False
        ).metric_key,
        collector_data.name,
    )

    assert value == 250
