import sys
import os
import pytest
from fastapi.testclient import TestClient
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from FastAPI with Jenkins & SonarQube!"}


def test_average_success():
    response = client.get("/average?numbers=10&numbers=20&numbers=30")
    assert response.status_code == 200
    assert response.json()["average"] == 20.0


def test_average_empty_list():
    response = client.get("/average")
    assert response.status_code == 422  # missing query parameter


def test_reverse_string():
    response = client.get("/reverse?text=SonarQube")
    assert response.status_code == 200
    assert response.json()["reversed"] == "ebuQranoS"
