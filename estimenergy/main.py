"""Entrypoint for the EstimEnergy application."""
import asyncio
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Session
import uvicorn

from estimenergy.prometheus import instrumentator
from estimenergy.config import config
from estimenergy.device import devices
from estimenergy.db import db_engine
from estimenergy.routers.device_router import device_router
from estimenergy.routers.day_router import day_router
from estimenergy.routers.month_router import month_router
from estimenergy.routers.year_router import year_router
from estimenergy.routers.total_router import total_router
from estimenergy.const import LOGGING_CONFIG


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

app.include_router(device_router)
app.include_router(day_router)
app.include_router(month_router)
app.include_router(year_router)
app.include_router(total_router)


def start():
    """Start the EstimEnergy application."""

    LOGGING_CONFIG["handlers"]["file"]["filename"] = config.logging_config.log_path
    LOGGING_CONFIG["loggers"]["uvicorn.error"][
        "level"
    ] = config.logging_config.log_level
    LOGGING_CONFIG["loggers"]["uvicorn.access"][
        "level"
    ] = config.logging_config.log_level
    LOGGING_CONFIG["loggers"]["estimenergy"]["level"] = config.logging_config.log_level

    uvicorn.run(
        "estimenergy.main:app",
        host=config.networking_config.host,
        port=config.networking_config.port,
        log_config=LOGGING_CONFIG,
        reload=config.dev_config.reload,
    )


def generate_openapi():
    """Generate the OpenAPI schema for the EstimEnergy application."""

    with open("openapi.json", "w", encoding="utf-8") as f:
        dump = json.dumps(app.openapi(), indent=2)
        f.write(dump)


@app.on_event("startup")
async def startup():
    """Application startup event."""

    with Session(db_engine) as session:
        SQLModel.metadata.create_all(db_engine)
        session.commit()

    for device in devices:
        asyncio.create_task(device.start())
