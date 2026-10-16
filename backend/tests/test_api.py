import pytest
from sqlalchemy.exc import OperationalError

from app.db import get_db
from app.main import app


def test_health_and_readiness(client):
    assert client.get("/health").json()["status"] == "UP"
    assert client.get("/ready").json() == {"status": "READY"}


def test_create_and_get_equipment(client, equipment):
    response = client.post("/api/equipment", json=equipment)
    assert response.status_code == 201
    record = response.json()
    assert record["created_at"]
    assert record["name"] == equipment["name"]
    assert client.get(f"/api/equipment/{record['id']}").json() == record


def test_empty_inventory_is_isolated(client):
    assert client.get("/api/equipment").json() == []
    assert client.get("/api/summary").json() == {
        "records": 0,
        "units": 0,
        "low_stock": 0,
        "categories": [],
    }


def test_update_persists_all_fields(client, equipment):
    record_id = client.post("/api/equipment", json=equipment).json()["id"]
    changed = {**equipment, "name": "Bench microscope", "quantity": 1, "location": "Lab B"}
    response = client.put(f"/api/equipment/{record_id}", json=changed)
    assert response.status_code == 200
    stored = client.get(f"/api/equipment/{record_id}").json()
    assert all(stored[key] == value for key, value in changed.items())
    assert client.get("/api/summary").json()["low_stock"] == 1


def test_delete_removes_equipment(client, equipment):
    record_id = client.post("/api/equipment", json=equipment).json()["id"]
    response = client.delete(f"/api/equipment/{record_id}")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/api/equipment/{record_id}").status_code == 404
    assert client.get("/api/summary").json()["records"] == 0


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_missing_record_returns_404(client, equipment, method):
    kwargs = {"json": equipment} if method == "put" else {}
    response = getattr(client, method)("/api/equipment/999", **kwargs)
    assert response.status_code == 404
    assert response.json()["detail"] == "Equipment not found"


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", "   "),
        ("category", ""),
        ("location", ""),
        ("quantity", -1),
        ("quantity", 1.5),
        ("quantity", True),
        ("low_stock_threshold", -1),
        ("quantity", 1_000_001),
    ],
)
def test_invalid_record_is_rejected(client, equipment, field, value):
    response = client.post("/api/equipment", json={**equipment, field: value})
    assert response.status_code == 422
    assert client.get("/api/equipment").json() == []


def test_invalid_update_preserves_record(client, equipment):
    record = client.post("/api/equipment", json=equipment).json()
    response = client.put(f"/api/equipment/{record['id']}", json={**equipment, "quantity": None})
    assert response.status_code == 422
    assert client.get(f"/api/equipment/{record['id']}").json() == record


def test_search_category_and_low_stock_filters(client, equipment):
    client.post("/api/equipment", json=equipment)
    client.post(
        "/api/equipment",
        json={**equipment, "name": "Beaker 100%", "category": "Glassware", "quantity": 2},
    )
    assert len(client.get("/api/equipment?q=MICROSCOPE").json()) == 1
    assert len(client.get("/api/equipment?category=Glassware&low_stock=true").json()) == 1
    assert client.get("/api/equipment?category=Microscopy&low_stock=true").json() == []
    assert len(client.get("/api/equipment", params={"q": "%"}).json()) == 1
    assert client.get("/api/summary").json() == {
        "records": 2,
        "units": 6,
        "low_stock": 1,
        "categories": ["Glassware", "Microscopy"],
    }


def test_whitespace_is_trimmed(client, equipment):
    response = client.post("/api/equipment", json={**equipment, "name": "  Pipette  "})
    assert response.json()["name"] == "Pipette"


def test_readiness_failure_does_not_break_liveness(client):
    class UnavailableDatabase:
        def execute(self, *_):
            raise OperationalError("SELECT 1", {}, Exception("database is offline"))

    app.dependency_overrides[get_db] = lambda: UnavailableDatabase()
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
    assert client.get("/health").status_code == 200


def test_metrics_records_api_requests(client):
    client.get("/api/equipment")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert 'handler="/api/equipment"' in response.text
