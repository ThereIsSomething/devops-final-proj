from alembic.config import Config
from sqlalchemy import create_engine, inspect

from alembic import command


def test_migration_up_repeat_and_down(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'migration.db'}")
    config = Config("alembic.ini")
    with engine.connect() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
        assert "equipment" in inspect(connection).get_table_names()
        columns = {column["name"] for column in inspect(connection).get_columns("equipment")}
        assert {"name", "quantity", "low_stock_threshold", "location"} <= columns
        command.upgrade(config, "head")
        command.downgrade(config, "base")
        assert "equipment" not in inspect(connection).get_table_names()
    engine.dispose()
