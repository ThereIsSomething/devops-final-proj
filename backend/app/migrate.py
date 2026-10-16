"""Run Alembic once at a time when multiple PostgreSQL replicas start."""

from pathlib import Path

from alembic.config import Config
from sqlalchemy import text

from alembic import command

from .db import engine


def migrate():
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    with engine.connect() as connection:
        if connection.dialect.name == "postgresql":
            # Session lock survives Alembic commits and is released on disconnect.
            connection.execute(text("SELECT pg_advisory_lock(729401)"))
            connection.commit()
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
        if connection.dialect.name == "postgresql":
            connection.execute(text("SELECT pg_advisory_unlock(729401)"))
            connection.commit()


if __name__ == "__main__":
    migrate()
