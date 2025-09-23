## tests/test_main.py
import pytest
import asyncio
from httpx import AsyncClient

from jokes_app.main import app, async_session, Base, engine
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
async def client(db_session):
    """Async HTTP client using FastAPI app"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

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


@pytest.mark.asyncio
async def test_get_joke(client: AsyncClient):
    """Test that /joke returns a joke even without a real DB"""
    response = await client.get("/joke")
    assert response.status_code == 200
    data = response.json()

    # Check that API returned a joke
    joke_type = data.get("type")
    assert joke_type in ["single", "twopart"], f"Unexpected joke type: {joke_type}"

    if joke_type == "single":
        assert "joke" in data
    else:
        assert "setup" in data and "delivery" in data
