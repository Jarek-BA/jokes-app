# jokes_app/database.py
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Use default SQLite for testing if not explicitly set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

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

