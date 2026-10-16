"""Save clearly synthetic equipment examples through the real API."""

import argparse
import json
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("url")
args = parser.parse_args()
base = args.url.rstrip("/")
if not base.startswith(("http://", "https://")):
    raise SystemExit("Expected HTTP(S) base URL")

examples = [
    ("Digital microscope", "Microscopy", 4, 2, "Lab A / Shelf 3"),
    ("Glass beaker · 250 mL", "Glassware", 18, 5, "Lab B / Cabinet 1"),
    ("Precision balance", "Measurement", 2, 2, "Lab A / Bench 2"),
    ("Safety goggles", "Safety", 24, 10, "Entrance / Safety station"),
    ("Adjustable micropipette", "Measurement", 6, 3, "Lab B / Drawer 4"),
    ("Nitrile gloves · box", "Consumables", 3, 5, "Store / Rack 2"),
]
with urllib.request.urlopen(f"{base}/api/equipment", timeout=10) as response:
    existing = {item["name"] for item in json.load(response)}

for name, category, quantity, threshold, location in examples:
    if name in existing:
        continue
    payload = {
        "name": name,
        "category": category,
        "quantity": quantity,
        "low_stock_threshold": threshold,
        "location": location,
    }
    request = urllib.request.Request(
        f"{base}/api/equipment",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        saved = json.load(response)
    print(f"Saved example equipment {saved['id']}: {saved['name']}")
