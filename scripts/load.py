"""Generate bounded real API traffic for the monitoring demonstration."""

import argparse
import time
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument("url", help="Application base URL, e.g. http://localhost:3000")
parser.add_argument("--requests", type=int, default=180)
args = parser.parse_args()
if not args.url.startswith(("http://", "https://")):
    raise SystemExit("Expected HTTP(S) URL")
for index in range(args.requests):
    with urllib.request.urlopen(
        f"{args.url.rstrip('/')}/api/equipment", timeout=10
    ) as response:
        response.read()
    if index % 30 == 0:
        print(f"{index + 1}/{args.requests} requests completed", flush=True)
    time.sleep(0.5)
print(f"Completed {args.requests} actual API requests")
