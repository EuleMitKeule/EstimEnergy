from sqlmodel import SQLModel, Session
from estimenergy.common import db_engine


def drop_all():
    """Drop all tables."""

    with Session(db_engine) as session:
        SQLModel.metadata.drop_all(db_engine)
        session.commit()
