import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# Patch the DATABASE_URL environment variable for testing
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

# Import app AFTER setting DATABASE_URL
from jokes_app.main import app

# Use TestClient for synchronous tests (FastAPI will handle async internally)
client = TestClient(app)


@pytest.fixture(autouse=True)
def patch_db_session():
    """
    Automatically patch the get_db dependency to avoid real DB calls during tests.
    """
    with patch("jokes_app.main.get_db", new_callable=AsyncMock) as mock_get_db:
        yield mock_get_db


def test_read_main():
    """
    Test that the homepage ("/") works and contains the expected button.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "Get a Joke" in response.text


def test_invalid_endpoint():
    """
    Test that a non-existent endpoint returns a 404 Not Found status.
    """
    response = client.get("/non-existent-url")
    assert response.status_code == 404


def test_get_joke():
    """
    Test that the /joke endpoint returns a valid joke in JSON format.
    """
    response = client.get("/joke")
    assert response.status_code == 200

    data = response.json()

    # The joke API can return two types of jokes: "single" or "twopart"
    joke_type = data.get("joke", {}).get("type") or data.get("type")
    if joke_type == "single":
        assert "joke" in data.get("joke", data)
    elif joke_type == "twopart":
        assert "setup" in data.get("joke", data) and "delivery" in data.get("joke", data)
    else:
        pytest.fail(f"Unexpected joke type: {joke_type}")
