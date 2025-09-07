from fastapi.testclient import TestClient
from jokes_app.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    # Check for the button text since it's always in index.html
    assert "Get a Joke" in response.text


def test_get_joke():
    response = client.get("/joke")
    assert response.status_code == 200
    data = response.json()

    # Either "joke" exists (single) or both "setup" and "delivery" exist (twopart)
    if data["type"] == "single":
        assert "joke" in data
    elif data["type"] == "twopart":
        assert "setup" in data and "delivery" in data
    else:
        pytest.fail(f"Unexpected joke type: {data['type']}")

