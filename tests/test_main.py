import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from jokes_app.main import app

# -------------------------------
# Event loop fixture
# -------------------------------
@pytest.fixture(scope="module")
def event_loop():
    """Create a fresh event loop for the module"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# -------------------------------
# Async HTTP client fixture
# -------------------------------
@pytest.fixture()
async def client():
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

    # The joke must have a valid type
    assert data["type"] in ("single", "twopart")

    if data["type"] == "twopart":
        # Two-part joke must have setup & delivery
        assert "setup" in data and isinstance(data["setup"], str)
        assert "delivery" in data and isinstance(data["delivery"], str)
        assert len(data["setup"]) > 0
        assert len(data["delivery"]) > 0
    else:
        # Single joke must have the joke text
        assert "joke" in data and isinstance(data["joke"], str)
        assert len(data["joke"]) > 0
