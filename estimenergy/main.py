"""Entrypoint for the EstimEnergy application."""
import asyncio

from fastapi import FastAPI
from sqlmodel import SQLModel, Session
import uvicorn

from estimenergy.prometheus import instrumentator
from estimenergy.config import config
from estimenergy.device import devices
from estimenergy.db import db_engine
from estimenergy.const import LOGGING_CONFIG


app = FastAPI(
    title="EstimEnergy",
)

instrumentator.instrument(app, "estimenergy")
instrumentator.expose(app, include_in_schema=True)


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


@app.on_event("startup")
async def startup():
    """Application startup event."""

    with Session(db_engine) as session:
        SQLModel.metadata.create_all(db_engine)
        session.commit()

    for device in devices:
        asyncio.create_task(device.start())
