import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base

DB_USER = os.getenv("DB_USER", "postgres")  # fallback to postgres
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


TESTING = os.getenv("TESTING", "false").lower() == "true"

# Async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Async session maker
async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

# Base declarative class
Base = declarative_base()

from typing import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


