# python script for part 4 analysis
#Usage: python benchmark.py --host 34.136.217.136 --port 5000 --n 50

import argparse
import time
import statistics
import requests

SAMPLE_RECORD = {
    "VIN (1-10)": "TEST00001",
    "County": "King",
    "City": "Seattle",
    "State": "WA",
    "Postal Code": "98101",
    "Model Year": "2023",
    "Make": "Tesla",
    "Model": "Model 3",
    "Electric Vehicle Type": "Battery Electric Vehicle (BEV)",
    "Clean Alternative Fuel Vehicle (CAFV) Eligibility": "Eligible",
    "Electric Range": "358",
    "Legislative District": "43",
    "DOL Vehicle ID": "999999999",
    "Vehicle Location": "POINT (-122.32 47.61)",
    "Electric Utility": "CITY OF SEATTLE - (WA)",
    "2020 Census Tract": "53033005600",
}

def benchmark(url: str, n: int) -> tuple[float, float]:
    latencies = []
    for _ in range(n):
        t0 = time.perf_counter()
        r = requests.post(url, json=SAMPLE_RECORD, timeout=30)
        latencies.append(time.perf_counter() - t0)
        r.raise_for_status()
    return statistics.mean(latencies) * 1000, statistics.stdev(latencies) * 1000


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--n", type=int, default=50)
    args = parser.parse_args()

    base = f"http://{args.host}:{args.port}"
    print(f"Benchmarking {base}  (n={args.n} requests each)\n")

    print("Running /insert-fast …")
    fast_mean, fast_std = benchmark(f"{base}/insert-fast", args.n)
    print(f"  avg={fast_mean:.1f} ms  stdev={fast_std:.1f} ms\n")

    print("Running /insert-safe …")
    safe_mean, safe_std = benchmark(f"{base}/insert-safe", args.n)
    print(f"  avg={safe_mean:.1f} ms  stdev={safe_std:.1f} ms\n")

    print("=" * 42)
    print(f"{'Endpoint':<20} {'Avg (ms)':>10} {'Stdev (ms)':>12}")
    print("-" * 42)
    print(f"{'insert-fast':<20} {fast_mean:>10.1f} {fast_std:>12.1f}")
    print(f"{'insert-safe':<20} {safe_mean:>10.1f} {safe_std:>12.1f}")
    overhead = safe_mean - fast_mean
    print(f"\nDurability overhead: +{overhead:.1f} ms ({overhead/fast_mean*100:.0f}% slower)")


if __name__ == "__main__":
    main()
