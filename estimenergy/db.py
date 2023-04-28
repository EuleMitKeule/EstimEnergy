"""Database module for EstimEnergy application."""
from sqlmodel import Session, SQLModel, create_engine

from estimenergy.config import config
from estimenergy.log import logger

db_engine = create_engine(config.sql_config.url)


def create_db():
    """Create the database for the EstimEnergy application."""

    logger.info("Creating database...")

    with Session(db_engine) as session:
        SQLModel.metadata.create_all(db_engine)
        session.commit()


def drop_db():
    """Drop all tables."""

    logger.info("Dropping all tables...")

    with Session(db_engine) as session:
        SQLModel.metadata.drop_all(db_engine)
        session.commit()
