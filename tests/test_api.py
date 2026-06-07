from fastapi.testclient import TestClient

from src.app.main import app

client = TestClient(app)


def test_landing_page() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Fibonacci Sequence API" in response.text


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_fibonacci_zero() -> None:
    response = client.get("/fibonacci?n=0")
    assert response.status_code == 200
    assert response.json() == {"n": 0, "value": 0}


def test_fibonacci_two() -> None:
    response = client.get("/fibonacci?n=2")
    assert response.status_code == 200
    assert response.json() == {"n": 2, "value": 1}


def test_fibonacci_ten() -> None:
    response = client.get("/fibonacci?n=10")
    assert response.status_code == 200
    assert response.json() == {"n": 10, "value": 55}


def test_fibonacci_negative() -> None:
    response = client.get("/fibonacci?n=-1")
    assert response.status_code == 400
    assert response.json()["error"]["message"] == "n must be greater than or equal to 0"


def test_fibonacci_invalid_type() -> None:
    response = client.get("/fibonacci?n=abc")
    assert response.status_code == 422


def test_fibonacci_missing_param() -> None:
    response = client.get("/fibonacci")
    assert response.status_code == 422


def test_fibonacci_too_large() -> None:
    response = client.get("/fibonacci?n=100001")
    assert response.status_code == 400
    assert "Maximum allowed value" in response.json()["error"]["message"]
