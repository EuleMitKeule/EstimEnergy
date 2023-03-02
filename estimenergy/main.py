
import asyncio
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
import yaml

from estimenergy.routers import energy_data, collector
from estimenergy.models import Collector
from estimenergy.common import instrumentator, settings


app = FastAPI(
    title="EstimEnergy",
)

register_tortoise(
    app,
    db_url=f"sqlite://{settings.db_path}",
    modules={"models": ["estimenergy.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

instrumentator.instrument(app)
instrumentator.expose(app, include_in_schema=True)

app.include_router(energy_data.router)
app.include_router(collector.router)

@app.on_event("startup")
async def start_energy_collectors():
    
    with open(settings.config_path) as f:
        config_dict = yaml.safe_load(f)

    collector_names = [collector_dict["name"] for collector_dict in config_dict["collectors"]]
    collectors = await Collector.all()
    
    for collector in collectors:
        if collector.name not in collector_names:
            await collector.delete()
    

    for collector_dict in config_dict["collectors"]:
        collector = await Collector.filter(name=collector_dict["name"]).first()
        if collector is None:
            collector = Collector(**collector_dict)
            await collector.save()
    

    collectors = await Collector.all()

    for collector in collectors:
        asyncio.create_task(collector.connect())
