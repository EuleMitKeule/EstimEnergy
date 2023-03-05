
import uvicorn
import asyncio
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
import yaml
from estimenergy.collectors.glow_collector import GlowCollector
from estimenergy.const import DEFAULT_HOST, DEFAULT_PORT

from estimenergy.routers import collector_router, energy_router
from estimenergy.models import CollectorData
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

app.include_router(energy_router.router)
app.include_router(collector_router.router)

def start():
    uvicorn.run(
        "estimenergy.main:app",
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        log_config=settings.log_config_path,
        reload=True,
    )

@app.on_event("startup")
async def start_energy_collectors():
    
    with open(settings.config_path) as f:
        config_dict = yaml.safe_load(f)

    collector_names = [collector_data_dict["name"] for collector_data_dict in config_dict["collectors"]]
    collector_datas = await CollectorData.all()
    
    for collector_data in collector_datas:
        if collector_data.name not in collector_names:
            await collector_data.delete()
    

    for collector_dict in config_dict["collectors"]:
        collector_data = await CollectorData.filter(name=collector_dict["name"]).first()
        if collector_data is None:
            collector_data = CollectorData(**collector_dict)
            await collector_data.save()
    

    collector_datas = await CollectorData.all()

    for collector_data in collector_datas:
        collector = GlowCollector(collector_data)
        asyncio.create_task(collector.start())
