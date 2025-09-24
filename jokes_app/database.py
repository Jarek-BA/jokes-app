import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

def get_database_url() -> str:
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "postgres")
    use_ssl = os.getenv("DB_USE_SSL", "false").lower() in ("1", "true", "yes")

    ssl_param = "require" if use_ssl else "disable"
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}?ssl={ssl_param}"

DATABASE_URL = get_database_url()
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

# -----------------------
# Dependency
# -----------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
