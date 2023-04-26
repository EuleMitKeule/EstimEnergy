"""Entrypoint for the EstimEnergy application."""
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from estimenergy.config import config
from estimenergy.const import API_PREFIX
from estimenergy.db import create_db
from estimenergy.devices import device_registry
from estimenergy.log import logger
from estimenergy.prometheus import instrumentator
from estimenergy.routers.day_router import day_router
from estimenergy.routers.device_router import device_router
from estimenergy.routers.month_router import month_router
from estimenergy.routers.total_router import total_router
from estimenergy.routers.year_router import year_router

app = FastAPI(
    title="EstimEnergy",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.networking_config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

instrumentator.instrument(app, "estimenergy")
instrumentator.expose(app, include_in_schema=True)

app.include_router(device_router, prefix=API_PREFIX)
app.include_router(day_router, prefix=API_PREFIX)
app.include_router(month_router, prefix=API_PREFIX)
app.include_router(year_router, prefix=API_PREFIX)
app.include_router(total_router, prefix=API_PREFIX)


def start():
    """Start the EstimEnergy application."""

    uvicorn.run(
        "estimenergy.main:app",
        host=config.networking_config.host,
        port=config.networking_config.port,
        reload=config.dev_config.reload,
    )


def generate_openapi():
    """Generate the OpenAPI schema for the EstimEnergy application."""

    with open("openapi.json", "w", encoding="utf-8") as openapi_file:
        dump = json.dumps(app.openapi(), indent=2)
        openapi_file.write(dump)


@app.on_event("startup")
async def startup():
    """Application startup event."""

    logger.info("Starting EstimEnergy application.")

    create_db()

    await device_registry.initialize()

    logger.info("EstimEnergy application started.")
