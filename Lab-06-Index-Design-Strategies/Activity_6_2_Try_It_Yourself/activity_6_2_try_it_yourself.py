"""Activity 6.2 Try-It-Yourself: Covered Query Payload Scaling & ESR In-Memory Sort Deep-Dive
Author: Kasireddy Meghana (USN: 24BTRCL119)
Course: NoSQL Databases (MongoDB) - Lab 6

Two Real-World Performance Deep-Dives:
1. Covered Query Impact on Large Payloads:
   - Small docs (~50 bytes) show ~1.0x - 1.3x speedup.
   - Large docs (~2 KB payloads) show substantial speedup because covered queries bypass megabytes of BSON fetching & deserialization!
2. ESR Rule Validation:
   - Comparing an ESR-ordered index vs Broken-ESR index (Range before Sort).
   - Proving that broken ESR triggers an in-memory SORT stage.
"""

import sys, os, time, json
from bson import json_util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.connection import get_db, reset_collection, banner


def main():
    banner("Activity 6.2 Try-It-Yourself: Covered Payloads & ESR Sort Deep-Dive")
    db = get_db("nosql_labs")

    results = {
        "activity": "Activity 6.2 Try-It-Yourself",
        "author": "Kasireddy Meghana (USN: 24BTRCL119)",
        "large_payload_benchmark": {},
        "esr_in_memory_sort_demo": {}
    }

    # =========================================================================
    # PART 1: Large Payload Covered Query Benchmark
    # =========================================================================
    print("=== Part 1: Covered Query Speedup with Large Document Payloads (2 KB / doc) ===")
    col_large = reset_collection("nosql_labs", "perf_large_payloads")
    
    # Generate 5,000 documents with 2 KB payload
    payload_str = "X" * 2048  # 2 KB text string
    docs = [
        {
            "sensor_id": f"SENSOR-{i:04d}",
            "reading": i * 0.1,
            "status": "active" if i % 2 == 0 else "inactive",
            "metadata_payload": payload_str
        }
        for i in range(5000)
    ]
    col_large.insert_many(docs)
    col_large.create_index([("sensor_id", 1)], name="idx_sensor")
    print(f"[OK] Inserted 5,000 documents with 2 KB payload each (~10 MB collection). Index created.\n")

    query = {"sensor_id": "SENSOR-2500"}
    iterations = 2000

    # Non-covered read (fetches 2 KB document)
    start = time.perf_counter()
    for _ in range(iterations):
        list(col_large.find(query).limit(10))
    t_non = time.perf_counter() - start
    ms_non = (t_non / iterations) * 1000

    # Covered read (only returns index key, 0 document fetch)
    start = time.perf_counter()
    for _ in range(iterations):
        list(col_large.find(query, {"_id": 0, "sensor_id": 1}).limit(10))
    t_cov = time.perf_counter() - start
    ms_cov = (t_cov / iterations) * 1000

    speedup_large = t_non / t_cov if t_cov > 0 else 1.0
    print(f"  Non-Covered (Full 2 KB doc): {iterations} reads in {t_non:.2f}s ({ms_non:.3f} ms/query)")
    print(f"  Covered (Index key only)   : {iterations} reads in {t_cov:.2f}s ({ms_cov:.3f} ms/query)")
    print(f"  Speedup on Large Payloads  : {speedup_large:.2f}x")
    print(f"  Insight: Covered queries shine when documents are large or cold on disk!\n")

    results["large_payload_benchmark"] = {
        "doc_payload_bytes": 2048,
        "iterations": iterations,
        "non_covered_ms": round(ms_non, 3),
        "covered_ms": round(ms_cov, 3),
        "speedup_factor": round(speedup_large, 2)
    }

    # =========================================================================
    # PART 2: ESR Rule Execution Plan Comparison (In-Memory Sort vs Index Sort)
    # =========================================================================
    print("=== Part 2: ESR Rule (Equality - Sort - Range) Execution Plan Test ===")
    col_esr = reset_collection("nosql_labs", "esr_demo")
    
    # 5,000 sample records
    esr_docs = [
        {
            "status": "active" if i % 2 == 0 else "maintenance",
            "reading": (i * 7) % 500,
            "sensor_id": f"SENSOR-{i:04d}",
            "firmware": "v2.1"
        }
        for i in range(5000)
    ]
    col_esr.insert_many(esr_docs)

    # Good Index: Equality (status) -> Sort (reading) -> Range (sensor_id)
    col_esr.create_index([("status", 1), ("reading", -1), ("sensor_id", 1)], name="idx_good_esr")
    # Broken Index: Equality (status) -> Range (sensor_id) -> Sort (reading)
    col_esr.create_index([("status", 1), ("sensor_id", 1), ("reading", -1)], name="idx_bad_esr")

    esr_query = {"status": "active", "sensor_id": {"$gte": "SENSOR-1000", "$lte": "SENSOR-3000"}}
    esr_sort = [("reading", -1)]

    # Plan with GOOD ESR Index
    plan_good = col_esr.find(esr_query).sort(esr_sort).hint("idx_good_esr").explain()
    win_good = plan_good["queryPlanner"]["winningPlan"]
    has_sort_good = "SORT" in str(win_good) and "SORT_KEY_GENERATOR" not in win_good.get("stage", "")

    # Plan with BAD ESR Index
    plan_bad = col_esr.find(esr_query).sort(esr_sort).hint("idx_bad_esr").explain()
    win_bad = plan_bad["queryPlanner"]["winningPlan"]
    has_sort_bad = "SORT" in str(win_bad)

    print(f"  Target Query: {esr_query}")
    print(f"  Target Sort : {esr_sort}\n")

    print(f"  [GOOD INDEX - ESR Order] -> [('status', 1), ('reading', -1), ('sensor_id', 1)]:")
    print(f"    Winning Stage       : {win_good.get('stage')}")
    print(f"    In-Memory Sort Stage: {'YES' if has_sort_good else 'NO (Index provides order directly)'}")
    print(f"    Docs Examined       : {plan_good['executionStats']['totalDocsExamined']}")
    print(f"    Keys Examined       : {plan_good['executionStats']['totalKeysExamined']}")

    print(f"\n  [BAD INDEX - Broken Order] -> [('status', 1), ('sensor_id', 1), ('reading', -1)]:")
    print(f"    Winning Stage       : {win_bad.get('stage')}")
    print(f"    In-Memory Sort Stage: {'YES (Expensive blocking memory sort!)' if has_sort_bad else 'NO'}")
    print(f"    Docs Examined       : {plan_bad['executionStats']['totalDocsExamined']}")
    print(f"    Keys Examined       : {plan_bad['executionStats']['totalKeysExamined']}")

    results["esr_in_memory_sort_demo"] = {
        "good_index": {
            "keys": [("status", 1), ("reading", -1), ("sensor_id", 1)],
            "stage": win_good.get("stage"),
            "in_memory_sort": has_sort_good,
            "docs_examined": plan_good["executionStats"]["totalDocsExamined"],
            "keys_examined": plan_good["executionStats"]["totalKeysExamined"]
        },
        "bad_index": {
            "keys": [("status", 1), ("sensor_id", 1), ("reading", -1)],
            "stage": win_bad.get("stage"),
            "in_memory_sort": has_sort_bad,
            "docs_examined": plan_bad["executionStats"]["totalDocsExamined"],
            "keys_examined": plan_bad["executionStats"]["totalKeysExamined"]
        }
    }

    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "covered_esr_deepdive.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n[OK] Deep-dive results saved to {out_file}")

    banner("Activity 6.2 Try-It-Yourself Complete")


if __name__ == "__main__":
    main()
