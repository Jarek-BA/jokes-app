import asyncio
import logging
import pytest
from httpx import AsyncClient, ASGITransport

from jokes_app.database import async_session, Base, engine
from jokes_app.main import app
from jokes_app.models import DimJokeType, DimLanguage, FactJokes

logger = logging.getLogger(__name__)


# -------------------------------
# Fixtures: setup in-memory DB
# -------------------------------

@pytest.fixture(scope="module")
def event_loop():
    """Create a fresh event loop for the module"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def setup_db():
    """Create all tables, then drop them after tests"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="module")
async def seed_data(setup_db):
    """Insert seed rows after tables exist"""
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
    yield


@pytest.fixture()
async def db_session():
    """Provide a fresh DB session for each test"""
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture()
async def client(seed_data):  # ensures data exists before API calls
    """Async HTTP client using FastAPI app"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
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
    response = await client.get("/joke")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "twopart"
    assert data["setup"] == "What time did the man go to the dentist?"
    assert data["delivery"] == "Tooth hurt-y."