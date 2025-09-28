import asyncio
from logging.config import fileConfig
import os
from dotenv import load_dotenv

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Load .env file from project root
load_dotenv()

# Import Base here (delayed import to avoid circular import)
def get_base():
    from app.database import Base
    return Base

# Alembic Config object
config = context.config

# Setup Python logging config from .ini file
fileConfig(config.config_file_name)

# Construct the DATABASE_URL from env variables
DATABASE_URL = (
    os.getenv('DATABASE_URL')
)
def run_migrations_offline():
    Base = get_base()
    context.configure(
        url=DATABASE_URL,
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    Base = get_base()
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    Base = get_base()
    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def main():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())


if __name__ == "__main__":
    main()
