from sqlmodel import SQLModel, Session, create_engine
from estimenergy.config import config


db_engine = create_engine(config.sql_config.url)


def drop_all():
    """Drop all tables."""

    with Session(db_engine) as session:
        SQLModel.metadata.drop_all(db_engine)
        session.commit()
