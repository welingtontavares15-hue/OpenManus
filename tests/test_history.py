import pytest
from fastapi.testclient import TestClient
from app.database import get_db
from app.main import app
from .test_workflow import TestingSessionLocal, override_get_db, setup_db, client

app.dependency_overrides[get_db] = override_get_db

def test_history_import():
    history_data = [
        {
            "description": "Historical Machine 1",
            "client_id": "OLD-001",
            "machine_id": "MAC-H1",
            "contract_expiration": "2027-01-01",
            "adjustment_month": 1
        },
        {
            "description": "Historical Machine 2",
            "client_id": "OLD-002",
            "machine_id": "MAC-H2"
        }
    ]

    response = client.post("/api/requests/import-history", json=history_data)
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["machine_id"] == "MAC-H1"
    assert response.json()[0]["status"] == "completed"
    assert response.json()[1]["status"] == "completed"
