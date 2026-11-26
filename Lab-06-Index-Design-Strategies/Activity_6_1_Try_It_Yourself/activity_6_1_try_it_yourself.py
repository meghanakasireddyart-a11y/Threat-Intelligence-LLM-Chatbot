"""Activity 6.1 Try-It-Yourself: Compound Index Prefixing & Phone Book Analogy
Author: Kasireddy Meghana (USN: 24BTRCL119)
Course: NoSQL Databases (MongoDB) - Lab 6

Demonstrates the phone book analogy:
An index on {"level": 1, "service": 1} behaves like a phone book sorted by (LastName, FirstName).
- Looking up by level alone (LastName) -> Instant IXSCAN.
- Looking up by level + service (LastName + FirstName) -> Instant IXSCAN.
- Looking up by service alone (FirstName) -> CANNOT use index -> Full COLLSCAN (50,000 docs).
"""

import sys, os, time, random, json
from bson import json_util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.connection import get_db, reset_collection, banner


def run_explain(col, query, label, sort=None):
    """Run explain plan and print key metrics."""
    cursor = col.find(query)
    if sort:
        cursor = cursor.sort(sort)
    plan = cursor.explain()
    
    winning = plan["queryPlanner"]["winningPlan"]
    stage = winning.get("stage", "")
    input_stage = winning.get("inputStage", {})
    ix_scan = input_stage.get("indexName", winning.get("indexName", "COLLSCAN"))
    
    exec_stats = plan.get("executionStats", {})
    docs_exam = exec_stats.get("totalDocsExamined", "N/A")
    keys_exam = exec_stats.get("totalKeysExamined", 0)
    returned = exec_stats.get("nReturned", "N/A")
    exec_ms = exec_stats.get("executionTimeMillis", "N/A")
    
    has_sort_stage = "SORT" in str(winning) and "SORT_KEY_GENERATOR" not in stage
    
    print(f"  {label}:")
    print(f"    Query Filter : {query}")
    if sort:
        print(f"    Sort Order   : {sort}")
    print(f"    Access Stage : {stage}")
    if "IXSCAN" in stage or "IXSCAN" in str(winning):
        print(f"    Index Used   : {ix_scan} (IXSCAN)")
    else:
        print(f"    Index Used   : NONE (Full Collection Scan - COLLSCAN)")
    print(f"    Docs Examined: {docs_exam}")
    print(f"    Keys Examined: {keys_exam}")
    print(f"    Docs Returned: {returned} (Time: {exec_ms} ms)")
    if sort:
        print(f"    In-Memory Sort: {'YES (Expensive!)' if has_sort_stage else 'NO (Index provides sort order)'}")
    print()

    return {
        "label": label,
        "query": str(query),
        "sort": str(sort) if sort else None,
        "stage": stage,
        "index": ix_scan,
        "totalDocsExamined": docs_exam,
        "totalKeysExamined": keys_exam,
        "nReturned": returned,
        "executionTimeMillis": exec_ms,
        "inMemorySort": has_sort_stage
    }


def main():
    banner("Activity 6.1 Try-It-Yourself: Prefix Rule & Phone Book Analogy")
    db = get_db("nosql_labs")
    col = reset_collection("nosql_labs", "prefix_demo_logs")

    # Reuse or copy logs
    print("Populating 50,000 synthetic log records...")
    random.seed(42)
    levels = ["INFO", "WARN", "ERROR", "DEBUG"]
    services = ["auth-svc", "payment-svc", "inventory-svc", "notification-svc", "api-gateway"]
    entries = []
    for i in range(50000):
        entries.append({
            "timestamp": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}Z",
            "level": random.choice(levels),
            "service": random.choice(services),
            "response_time_ms": random.randint(1, 5000),
            "status_code": random.choice([200, 200, 200, 201, 301, 400, 401, 403, 404, 500]),
        })
    col.insert_many(entries)
    print(f"[OK] Collection ready with {col.count_documents({})} documents.\n")

    # Create ONLY one compound index: {"level": 1, "service": 1}
    print("=== Creating Compound Index: {'level': 1, 'service': 1} ===")
    col.create_index([("level", 1), ("service", 1)], name="idx_level_service_only")
    print("[OK] Index 'idx_level_service_only' created.\n")

    results = {
        "activity": "Activity 6.1 Try-It-Yourself: Prefix Rule Verification",
        "author": "Kasireddy Meghana (USN: 24BTRCL119)",
        "demonstrations": []
    }

    print("=== Phone Book Analogy Test Suite ===")
    
    # Test 1: Level only (LastName) -> Left prefix
    t1 = run_explain(
        col,
        {"level": "ERROR"},
        "Test 1: Filter on 'level' only (Leading Prefix Match)"
    )

    # Test 2: Level + Service (LastName + FirstName) -> Full compound match
    t2 = run_explain(
        col,
        {"level": "ERROR", "service": "payment-svc"},
        "Test 2: Filter on 'level' AND 'service' (Full Compound Match)"
    )

    # Test 3: Service only (FirstName without LastName) -> Trailing field -> COLLSCAN
    t3 = run_explain(
        col,
        {"service": "payment-svc"},
        "Test 3: Filter on 'service' ALONE (Non-Prefix Trailing Field)"
    )

    results["demonstrations"].extend([t1, t2, t3])

    # Test 4: Compound Sorting
    print("=== Compound Index Sort Order Test ===")
    t4 = run_explain(
        col,
        {"level": "ERROR"},
        "Test 4: Filter on 'level' + Sort by 'service' (Index-Assisted Sort)",
        sort=[("service", 1)]
    )
    t5 = run_explain(
        col,
        {"level": "ERROR"},
        "Test 5: Filter on 'level' + Sort by 'status_code' (Unindexed Sort -> In-Memory Sort)",
        sort=[("status_code", 1)]
    )
    results["demonstrations"].extend([t4, t5])

    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "compound_prefix_analysis.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"[OK] Try-it-yourself findings saved to {out_file}")

    banner("Activity 6.1 Try-It-Yourself Complete")


if __name__ == "__main__":
    main()
