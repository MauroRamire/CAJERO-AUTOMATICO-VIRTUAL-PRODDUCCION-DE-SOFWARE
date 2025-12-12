from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_app_imports_and_runs():
    response = client.get("/")
    assert response.status_code in (200, 404)
