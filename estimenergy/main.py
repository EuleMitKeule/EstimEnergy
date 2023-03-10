
import uvicorn
import asyncio
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
import yaml
from estimenergy.collectors.glow_collector import GlowCollector
from estimenergy.const import DEFAULT_PORT, LOGGING_CONFIG

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

instrumentator.instrument(app, "estimenergy")
instrumentator.expose(app, include_in_schema=True)

app.include_router(energy_router.router)
app.include_router(collector_router.router)

def start():
    if settings.log_path is not None and settings.log_path != "":
        LOGGING_CONFIG["handlers"]["file"]["filename"] = settings.log_path

    if settings.log_level is not None and settings.log_level != "":
        LOGGING_CONFIG["loggers"]["uvicorn.error"]["level"] = settings.log_level
        LOGGING_CONFIG["loggers"]["uvicorn.access"]["level"] = settings.log_level
        LOGGING_CONFIG["loggers"]["estimenergy"]["level"] = settings.log_level

    uvicorn.run(
        "estimenergy.main:app",
        host="0.0.0.0",
        port=DEFAULT_PORT,
        log_config=LOGGING_CONFIG,
        reload=settings.reload,
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
