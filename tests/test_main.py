# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import asyncio

from jokes_app.main import app, async_session, engine
from jokes_app.models import Base, DimJokeType, DimLanguage, FactJokes

# -------------------------------
# Client fixture
# -------------------------------
client = TestClient(app)

# -------------------------------
# Setup in-memory DB and create tables
# -------------------------------
@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """
    Create all tables in an in-memory SQLite DB for testing.
    """
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    # Run setup
    asyncio.get_event_loop().run_until_complete(create_tables())
    yield
    # Run teardown
    asyncio.get_event_loop().run_until_complete(drop_tables())

# -------------------------------
# Mocked JokeAPI responses
# -------------------------------
mock_single_joke = {
    "type": "single",
    "joke": "Why did the tomato turn red? Because it saw the salad dressing!",
    "flags": {"nsfw": False, "religious": False, "political": False, "racist": False, "sexist": False, "explicit": False},
}

mock_twopart_joke = {
    "type": "twopart",
    "setup": "Why did the chicken cross the road?",
    "delivery": "To get to the other side.",
    "flags": {"nsfw": False, "religious": False, "political": False, "racist": False, "sexist": False, "explicit": False},
}

# -------------------------------
# Tests
# -------------------------------
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "Get a Joke" in response.text


def test_invalid_endpoint():
    response = client.get("/non-existent-url")
    assert response.status_code == 404


@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
def test_get_single_joke(mock_get):
    # Mock the API response
    mock_get.return_value.status_code = 200
    mock_get.return_value.json = AsyncMock(return_value=mock_single_joke)
    mock_get.return_value.text = str(mock_single_joke)

    response = client.get("/joke")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "single"
    assert "joke" in data


@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
def test_get_twopart_joke(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json = AsyncMock(return_value=mock_twopart_joke)
    mock_get.return_value.text = str(mock_twopart_joke)

    response = client.get("/joke")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "twopart"
    assert "setup" in data and "delivery" in data
