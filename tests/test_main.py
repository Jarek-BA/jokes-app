# Import pytest, a testing framework for Python
import pytest
# Import TestClient, which allows us to simulate requests to our FastAPI app (like a fake browser)
from fastapi.testclient import TestClient
# Import our actual FastAPI application from jokes_app/main.py
from jokes_app.main import app

# Create a "client" that we can use to send test requests to our app
client = TestClient(app)


def test_read_main():
    """
    Test that the homepage ("/") works and contains the expected button.
    """
    # Send a GET request to the root URL ("/")
    response = client.get("/")

    # Check that the server responded with "200 OK" (which means success)
    assert response.status_code == 200

    # Check that the HTML page contains the "Get a Joke" button text
    # This ensures the template is rendering correctly
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
    # Send a GET request to the /joke endpoint
    response = client.get("/joke")

    # Check that the server responded with "200 OK"
    assert response.status_code == 200

    # Convert the server's response (JSON text) into a Python dictionary
    data = response.json()

    # The joke API can return two types of jokes:
    # 1. "single": one-line jokes
    # 2. "twopart": jokes with a setup and a delivery
    if data["type"] == "single":
        # If it's a single joke, make sure the "joke" field is present
        assert "joke" in data
    elif data["type"] == "twopart":
        # If it's a two-part joke, make sure both "setup" and "delivery" fields are present
        assert "setup" in data and "delivery" in data
    else:
        # If the type is something unexpected, mark the test as failed
        pytest.fail(f"Unexpected joke type: {data['type']}")
