"""Lab 7.2 - Working Set Analysis
Author: Kasireddy Meghana (USN: 24BTRCL119)
Course: NoSQL Databases (MongoDB) - Lab 7

Insert 100K docs, check WiredTiger cache metrics via serverStatus,
and simulate range queries hitting different parts of the collection.
"""

import sys, os, time, json
from bson import json_util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.connection import get_db, reset_collection, banner
from rich.table import Table
from rich.console import Console

console = Console()


def main():
    banner("Lab 7.2: Working Set Analysis")
    db = get_db("nosql_labs")
    col = reset_collection("nosql_labs", "working_set_docs")

    # Insert 100K x ~2KB documents
    count = 100000
    print(f"Inserting {count:,} documents (~2KB each)...")
    docs = [{"sensor": f"S-{i:06d}", "reading": i * 0.01, "metadata": "x" * 1800} for i in range(count)]
    start = time.perf_counter()
    col.insert_many(docs)
    elapsed = time.perf_counter() - start
    print(f"[OK] Inserted {count:,} docs in {elapsed:.1f}s ({count/elapsed:,.0f} docs/sec)")

    # WiredTiger cache stats
    status = db.command("serverStatus")
    wt = status.get("wiredTiger", {})
    cache = wt.get("cache", {})

    print("\n=== WiredTiger Cache Metrics ===")
    max_bytes = cache.get('maximum bytes configured', 0)
    current_bytes = cache.get('bytes currently in the cache', 0)
    dirty_bytes = cache.get('tracked dirty bytes in the cache', 0)
    pages_evicted_app = cache.get('eviction pages evicted by application threads', 0)
    pages_read = cache.get('pages read into cache', 0)

    print(f"  Cache max:          {max_bytes:>15,} bytes ({max_bytes / (1024*1024):.0f} MB)")
    print(f"  Cache in use:       {current_bytes:>15,} bytes ({current_bytes / (1024*1024):.0f} MB)")
    print(f"  Dirty bytes:        {dirty_bytes:>15,} bytes ({dirty_bytes / (1024*1024):.0f} MB)")
    print(f"  Pages evicted:      {pages_evicted_app:>15,}")
    print(f"  Pages read:         {pages_read:>15,}")

    # Simulate queries hitting different parts of working set
    print("\n=== Simulating Working Set Queries ===")
    ranges = [(0, 1000), (49000, 50000), (99000, 100000)]
    query_results = []

    for query_range in ranges:
        start = time.perf_counter()
        matched = list(col.find({"sensor": {"$gte": f"S-{query_range[0]:06d}", "$lte": f"S-{query_range[1]:06d}"}}))
        q_elapsed = (time.perf_counter() - start) * 1000
        query_results.append({
            "range": f"{query_range[0]}-{query_range[1]}",
            "count": len(matched),
            "elapsed_ms": round(q_elapsed, 2)
        })
        print(f"  Range {query_range[0]:>6}-{query_range[1]:<6}: {q_elapsed:.1f} ms ({len(matched)} docs)")

    # Cache hit ratio
    cache_after = db.command("serverStatus")["wiredTiger"]["cache"]
    pages_read_after = cache_after.get('pages read into cache', 0)
    pages_evict_after = cache_after.get('eviction pages evicted by application threads', 0)
    print(f"\n  Pages read into cache: {pages_read_after:,}")
    print(f"  Pages evicted:         {pages_evict_after:,}")
    hit_ratio = 1.0
    if pages_read_after > 0:
        hit_ratio = max(0, 1 - (pages_evict_after / pages_read_after))
        print(f"  Approx cache hit ratio: {hit_ratio:.1%}")
    print(f"  [TIP] If working set > cache, hit ratio drops and evictions increase.")

    output_data = {
        "lab": "Lab 7.2 - Working Set Analysis",
        "student": "Kasireddy Meghana",
        "usn": "24BTRCL119",
        "inserted_docs": count,
        "insert_time_sec": round(elapsed, 2),
        "cache_metrics": {
            "maximum_bytes": max_bytes,
            "bytes_in_use": current_bytes,
            "dirty_bytes": dirty_bytes,
            "pages_read": pages_read_after,
            "pages_evicted": pages_evict_after,
            "approx_hit_ratio": round(hit_ratio, 4)
        },
        "query_timings": query_results
    }
    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "working_set_output.json")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(output_data, indent=2))
    print(f"\n[OK] Results saved to {out_file}")

    banner("Lab 7.2 Complete")


if __name__ == "__main__":
    main()
