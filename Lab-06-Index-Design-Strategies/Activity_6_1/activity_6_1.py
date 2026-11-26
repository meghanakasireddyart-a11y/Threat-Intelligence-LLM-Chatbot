"""Lab 6.1 - Index Design for a Query Workload
Author: Kasireddy Meghana (USN: 24BTRCL119)
Course: NoSQL Databases (MongoDB) - Lab 6
Generate data, compare explain() with/without indexes, analyze index usage.
"""

import sys, os, time, random, json
from bson import json_util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.connection import get_db, reset_collection, banner


def generate_log_entries(count=50000):
    """Generate synthetic server log entries."""
    levels = ["INFO", "WARN", "ERROR", "DEBUG"]
    services = ["auth-svc", "payment-svc", "inventory-svc", "notification-svc", "api-gateway"]
    entries = []
    # Seed for reproducibility in benchmarking
    random.seed(42)
    for i in range(count):
        entries.append({
            "timestamp": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}Z",
            "level": random.choice(levels),
            "service": random.choice(services),
            "message": f"Log entry #{i}: request processed successfully",
            "response_time_ms": random.randint(1, 5000),
            "status_code": random.choice([200, 200, 200, 201, 301, 400, 401, 403, 404, 500]),
        })
    return entries


def run_explain(col, query, label):
    """Run explain plan and print key metrics."""
    plan = col.find(query).explain()
    winning = plan["queryPlanner"]["winningPlan"]
    stage = winning.get("stage", "")
    
    input_stage = winning.get("inputStage", {})
    ix_scan = input_stage.get("indexName", winning.get("indexName", "COLLSCAN"))
    
    exec_stats = plan.get("executionStats", {})
    docs_exam = exec_stats.get("totalDocsExamined", "N/A (no exec stats)")
    keys_exam = exec_stats.get("totalKeysExamined", 0)
    returned = exec_stats.get("nReturned", "N/A")
    exec_ms = exec_stats.get("executionTimeMillis", "N/A")
    
    print(f"  {label}:")
    print(f"    Stage: {stage}")
    if "IXSCAN" in stage or "IXSCAN" in str(winning):
        print(f"    Index: {ix_scan}")
    print(f"    Docs examined: {docs_exam}")
    print(f"    Keys examined: {keys_exam}")
    print(f"    Returned: {returned} (Time: {exec_ms} ms)")
    
    return {
        "label": label,
        "query": str(query),
        "stage": stage,
        "index": ix_scan,
        "totalDocsExamined": docs_exam,
        "totalKeysExamined": keys_exam,
        "nReturned": returned,
        "executionTimeMillis": exec_ms
    }


def main():
    banner("Lab 6.1: Index Design for Query Workload")
    db = get_db("nosql_labs")
    col = reset_collection("nosql_labs", "server_logs")

    # Generate 50K docs
    print("Generating 50,000 log entries... (may take a few seconds)")
    entries = generate_log_entries(50000)
    col.insert_many(entries)
    print(f"[OK] Inserted {col.count_documents({})} log entries.\n")

    results = {
        "lab": "Lab 6.1 - Index Design for a Query Workload",
        "student": "Kasireddy Meghana (USN: 24BTRCL119)",
        "total_documents": 50000,
        "before_indexes": [],
        "after_indexes": [],
        "prefix_tests": []
    }

    # --- EXPLAIN WITHOUT INDEXES ---
    print("=== EXPLAIN: Without Indexes ===")
    r1 = run_explain(col, {"level": "ERROR", "service": "payment-svc"}, "ERROR logs from payment-svc")
    r2 = run_explain(col, {"status_code": 404}, "All 404 responses")
    r3 = run_explain(col, {"service": "api-gateway", "response_time_ms": {"$gt": 3000}}, "Slow API gateway requests")
    results["before_indexes"].extend([r1, r2, r3])

    # --- CREATE INDEXES ---
    print("\n=== Creating Indexes ===")
    col.create_index([("level", 1), ("service", 1)], name="idx_level_service")
    col.create_index([("service", 1), ("response_time_ms", -1)], name="idx_service_latency")
    col.create_index([("status_code", 1)], name="idx_status")
    print("[OK] Created 3 indexes.\n")

    # --- EXPLAIN WITH INDEXES ---
    print("=== EXPLAIN: With Indexes ===")
    r4 = run_explain(col, {"level": "ERROR", "service": "payment-svc"}, "ERROR logs from payment-svc")
    r5 = run_explain(col, {"status_code": 404}, "All 404 responses")
    r6 = run_explain(col, {"service": "api-gateway", "response_time_ms": {"$gt": 3000}}, "Slow API gateway requests")
    results["after_indexes"].extend([r4, r5, r6])

    # --- PREFIX RULE DEMONSTRATION ---
    print("\n=== Compound Index Prefix Rule Verification ===")
    print("Testing query on 'level' alone (valid prefix of idx_level_service):")
    p1 = run_explain(col, {"level": "ERROR"}, "Filter on level alone (Prefix Match)")
    print("Testing query on 'service' alone (matches idx_service_latency prefix):")
    p2 = run_explain(col, {"service": "notification-svc"}, "Filter on service alone (Matches idx_service_latency prefix)")
    results["prefix_tests"].extend([p1, p2])

    # List indexes
    print("\n=== Index Summary ===")
    index_list = []
    for idx in col.list_indexes():
        keys = dict(idx.get("key", {}))
        name = idx.get("name", "")
        print(f"  {name:30} keys={keys}")
        index_list.append({"name": name, "keys": keys})
    results["indexes"] = index_list

    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index_design_output.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n[OK] Results saved to {out_file}")

    banner("Lab 6.1 Complete")


if __name__ == "__main__":
    main()
