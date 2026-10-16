"""Exercise real HTTP CRUD against a running LabShelf instance."""

import argparse
import json
import urllib.error
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("url")
args = parser.parse_args()
base = args.url.rstrip("/")
if not base.startswith(("http://", "https://")):
    raise SystemExit("Expected HTTP(S) URL")


def call(path, method="GET", payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        base + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        body = response.read()
        return response.status, json.loads(body) if body else None


health_status, health = call("/health")
assert health_status == 200 and health["status"] == "UP"
print(f"PASS health; deployed version {health['version']}")
_, before = call("/api/summary")
payload = {
    "name": "Verification caliper",
    "category": "Verification",
    "quantity": 3,
    "low_stock_threshold": 2,
    "location": "Temporary API check",
}
record_id = None
try:
    created_status, created = call("/api/equipment", "POST", payload)
    assert created_status == 201
    record_id = created["id"]
    _, fetched = call(f"/api/equipment/{record_id}")
    assert fetched["name"] == payload["name"]
    print(f"PASS POST and GET; equipment id {record_id}")
    payload["quantity"] = 1
    _, updated = call(f"/api/equipment/{record_id}", "PUT", payload)
    assert updated["quantity"] == 1
    _, low_stock = call("/api/equipment?category=Verification&low_stock=true")
    assert any(record["id"] == record_id for record in low_stock)
    print("PASS PUT and low-stock filter")
finally:
    if record_id is not None:
        deleted_status, _ = call(f"/api/equipment/{record_id}", "DELETE")
        assert deleted_status == 204
try:
    call(f"/api/equipment/{record_id}")
    raise AssertionError("Deleted equipment still exists")
except urllib.error.HTTPError as error:
    assert error.code == 404
_, after = call("/api/summary")
assert after == before
print("PASS DELETE, subsequent 404, and unchanged original inventory totals")
