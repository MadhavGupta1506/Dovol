from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .config import settings


import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.database_username}:{settings.database_password}"
    f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
)


connect_args = {"statement_cache_size": 0}
if settings.database_ssl:
    connect_args["ssl"] = ssl_context

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    echo=True,
    future=True,
    connect_args=connect_args,
)

AsyncSessionLocal = sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)
# Base class for declarative models.
Base = declarative_base()

# Dependency function to get a database session.
async def get_db():
    async with AsyncSessionLocal() as db:  # Ensures proper session management
        yield db  # Yield the session for use in a request