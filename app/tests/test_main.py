from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "<h1>Random Jokes</h1>" in response.text

def test_joke_endpoint(monkeypatch):
    async def mock_get(*args, **kwargs):
        class MockResponse:
            def raise_for_status(self): pass
            def json(self):
                return {"type": "single", "joke": "This is a test joke."}
        return MockResponse()

    import httpx
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    response = client.get("/joke")
    assert response.status_code == 200
    assert response.json()["joke"] == "This is a test joke."

def test_joke_twopart(monkeypatch):
    async def mock_get(*args, **kwargs):
        class MockResponse:
            def raise_for_status(self): pass
            def json(self):
                return {"type": "twopart", "setup": "Setup part", "delivery": "Delivery part"}
        return MockResponse()

    import httpx
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    response = client.get("/joke")
    assert response.status_code == 200
    assert response.json()["joke"] == "Setup part ... Delivery part"
