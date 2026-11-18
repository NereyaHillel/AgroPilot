"""NFR-2.3: p95 latency of fresh forecasts at a steady request rate.

Usage: uv run python scripts/measure_fresh_latency.py [base_url] [rps] [seconds]
The first request fills the cache; every measured request is then a fresh answer,
so the provider is never called during the measurement.
"""

import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import httpx

base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8021"
rps = float(sys.argv[2]) if len(sys.argv) > 2 else 10
seconds = float(sys.argv[3]) if len(sys.argv) > 3 else 60
params = {"lat": 48.85, "lon": 2.35, "days": 7}

with httpx.Client(timeout=30) as warm:
    first = warm.get(f"{base}/v1/forecast", params=params)
    assert first.status_code == 200 and first.json()["stale"] is False, first.text


def one(client: httpx.Client) -> tuple[int, float]:
    start = time.perf_counter()
    response = client.get(f"{base}/v1/forecast", params=params)
    return response.status_code, (time.perf_counter() - start) * 1000


latencies, statuses = [], []
with httpx.Client(timeout=30) as client, ThreadPoolExecutor(max_workers=32) as pool:
    futures = []
    began = time.perf_counter()
    for i in range(int(rps * seconds)):
        time.sleep(max(0.0, began + i / rps - time.perf_counter()))
        futures.append(pool.submit(one, client))
    elapsed = time.perf_counter() - began
    for future in futures:
        status, ms = future.result()
        statuses.append(status)
        latencies.append(ms)

latencies.sort()
p = lambda q: latencies[min(len(latencies) - 1, int(q * len(latencies)))]
print(f"requests={len(latencies)} failures={sum(s != 200 for s in statuses)} rps={len(latencies) / elapsed:.2f}")
print(f"median={statistics.median(latencies):.1f}ms p95={p(0.95):.1f}ms p99={p(0.99):.1f}ms max={latencies[-1]:.1f}ms")
