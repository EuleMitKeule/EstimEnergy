from freezegun import freeze_time
import pytest

from estimenergy.collectors.glow_collector import GlowCollector
from estimenergy.models.energy_data import EnergyData


@pytest.mark.anyio
async def test_fixtures(glow_collector, collector_data):
    assert glow_collector.collector_data == collector_data


@pytest.mark.anyio
async def test_kwh_changed(glow_collector: GlowCollector, get_metric_value):
    kwh = 0
    for _ in range(10):
        kwh += 1
        await glow_collector.update_kwh(kwh)
        await glow_collector.metrics.update_metrics()
        value = await get_metric_value("estimenergy_day_kwh", "glow_test")
        assert value == kwh


@freeze_time("2021-11-01")
@pytest.mark.anyio
async def test_create_energy_data(glow_collector: GlowCollector):
    energy_data = await EnergyData.filter(
        collector=glow_collector.collector_data, year=2021, month=11, day=1
    ).first()
    assert energy_data is None

    await glow_collector.update_kwh(123.321)

    energy_data = await EnergyData.filter(
        collector=glow_collector.collector_data, year=2021, month=11, day=1
    ).first()
    assert energy_data is not None
    assert energy_data.kwh == 123.321


@freeze_time("2021-11-01")
@pytest.mark.anyio
async def test_update_energy_data(glow_collector: GlowCollector):
    energy_data = await EnergyData.filter(
        collector=glow_collector.collector_data, year=2021, month=11, day=1
    ).first()
    assert energy_data is None

    await glow_collector.update_kwh(123.321)
    await glow_collector.update_kwh(321.123)

    energy_data = await EnergyData.filter(
        collector=glow_collector.collector_data, year=2021, month=11, day=1
    ).first()
    assert energy_data is not None
    assert energy_data.kwh == 321.123


@freeze_time("2021-11-01")
@pytest.mark.anyio
async def test_create_energy_data_next_day(glow_collector: GlowCollector):
    energy_data = await EnergyData.filter(
        collector=glow_collector.collector_data, year=2021, month=11, day=1
    ).first()
    assert energy_data is None

    await glow_collector.update_kwh(123.321)

    energy_data = await EnergyData.filter(
        collector=glow_collector.collector_data, year=2021, month=11, day=1
    ).first()
    assert energy_data is not None
    assert energy_data.kwh == 123.321

    with freeze_time("2021-11-02"):
        await glow_collector.update_kwh(1.234)

    energy_data = await EnergyData.filter(
        collector=glow_collector.collector_data, year=2021, month=11, day=1
    ).first()
    assert energy_data is not None
    assert energy_data.kwh == 123.321

    energy_data = await EnergyData.filter(
        collector=glow_collector.collector_data, year=2021, month=11, day=2
    ).first()
    assert energy_data is not None
    assert energy_data.kwh == 1.234
