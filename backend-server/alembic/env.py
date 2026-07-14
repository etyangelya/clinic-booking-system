import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# alembic's console-script entry point (unlike `python -m alembic`) does not
# add the project root to sys.path, so the app package would fail to import.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings
from app.database import Base
from app.models import *  # noqa: F401,F403

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# alembic.ini's sqlalchemy.url is just a fallback for local dev; always prefer
# the app's actual DATABASE_URL (from .env) so migrations target the real DB.
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
