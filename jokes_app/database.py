# jokes_app/database.py
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# -----------------------
# DATABASE CONFIGURATION
# -----------------------
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

# Detect if we should use SSL (Supabase / Render)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
USE_SSL = ENVIRONMENT in ("production", "render", "supabase")

# Build asyncpg URL
ssl_param = "require" if USE_SSL else "disable"
DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?ssl={ssl_param}"
)

print("DATABASE_URL:", DATABASE_URL)  # ✅ Debugging

# -----------------------
# SQLALCHEMY BASE & ENGINE
# -----------------------
Base = declarative_base()

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# -----------------------
# ASYNC DEPENDENCY
# -----------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session."""
    async with async_session() as session:
        yield session
