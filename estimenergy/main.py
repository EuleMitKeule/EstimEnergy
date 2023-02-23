
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from estimenergy.routers import settings, energy_data


app = FastAPI(
    title="EstimEnergy",
)

register_tortoise(
    app,
    db_url="sqlite://config/estimenergy.db",
    modules={"models": ["estimenergy.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

app.include_router(settings.router)
app.include_router(energy_data.router)
