## tests/test_main.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import logging

from jokes_app.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

from typing import Any, AsyncGenerator

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport

from jokes_app.main import app, async_session, engine
from jokes_app.database import async_session, Base, engine
from jokes_app.models import DimJokeType, DimLanguage, DimLabel, FactJokes


# -------------------------------
# Fixtures: setup in-memory DB
# -------------------------------
@pytest.fixture(scope="module", autouse=True)
def event_loop():
    """Create a fresh event loop for the module"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    """Create tables in in-memory SQLite and clean up after tests"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def db_session():
    """Provide a fresh DB session for each test"""
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture()
async def client():
    """Async HTTP client using FastAPI app"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="module", autouse=True)
async def seed_data(setup_db):
    """Insert a sample joke into the test DB after tables are created"""
    async with async_session() as session:
        joke_type = DimJokeType(name="twopart")
        language = DimLanguage(code="en", name="English")
        session.add_all([joke_type, language])
        await session.flush()

        joke = FactJokes(
            joke_type_id=joke_type.id,
            language_id=language.id,
            setup="What time did the man go to the dentist?",
            delivery="Tooth hurt-y.",
            is_active=True,
            is_flagged=False
        )
        session.add(joke)
        await session.commit()



# -------------------------------
# Tests
# -------------------------------
@pytest.mark.asyncio
async def test_read_main(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert "Get a Joke" in response.text


@pytest.mark.asyncio
async def test_invalid_endpoint(client: AsyncClient):
    response = await client.get("/non-existent-url")
    assert response.status_code == 404


@router.get("/joke", response_class=JSONResponse)
async def get_joke(
    lang: str = "en",
    blacklist: str = "",
    session_token: str | None = None,
    rating_score: float | None = None,
    rating_description: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    # ✅ Step 1: Try to fetch a joke from the local DB
    result = await db.execute(select(FactJokes).limit(1))
    joke = result.scalar_one_or_none()

    if joke:
        # Get joke type name from relationship
        joke_type_name = joke.joke_type.name if joke.joke_type else "twopart"

        if joke_type_name == "single":
            return {"type": "single", "joke": joke.joke_text}
        else:
            return {"type": "twopart", "setup": joke.setup, "delivery": joke.delivery}

    # ✅ Step 2: Fallback to JokeAPI if no local joke
    if lang not in ["cs", "de", "en", "es", "fr"]:
        lang = "en"

    url = f"https://v2.jokeapi.dev/joke/Any?lang={lang}"
    if blacklist:
        url += f"&blacklistFlags={blacklist}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url)
            res.raise_for_status()
            data = res.json()
            logger.info(f"HTTP Status: {res.status_code}")
    except httpx.RequestError as e:
        logger.error(f"HTTP request failed: {e}")
        raise HTTPException(status_code=502, detail="Error fetching joke from API")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP status error: {e}")
        raise HTTPException(status_code=502, detail="Error fetching joke from API")

    joke_type_name = data.get("type", "single")
    joke_text = data.get("joke")
    setup = data.get("setup")
    delivery = data.get("delivery")

    if joke_type_name == "single":
        return {"type": "single", "joke": joke_text}
    else:
        return {"type": "twopart", "setup": setup, "delivery": delivery}