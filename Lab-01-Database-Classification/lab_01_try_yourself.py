"""Activity 1.1 (Try It Yourself) - Advanced Database Classification & Automated Evaluation Engine

Extends the NoSQL product survey by:
1. Formally classifying the 3 mystery products (DynamoDB, InfluxDB, OrientDB) plus 5 additional modern specialized / multi-model engines into MongoDB.
2. Storing rich architectural metadata (multi-model capability, latency tier, licensing).
3. Executing aggregation pipelines (family distribution, multi-model breakdown, open-source ratio).
4. Running an automated workload-to-family classification validator.
5. Exporting collection to lab_01_try_yourself.json.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.connection import get_db, reset_collection, banner, print_json
from rich.table import Table
from rich.console import Console
import json
from bson import json_util

console = Console()


def main():
    banner("Activity 1.1 (Try It Yourself): Advanced NoSQL Classification Engine")

    db = get_db("nosql_labs")
    col = reset_collection("nosql_labs", "database_products_tryit")

    # Mystery products + modern specialized/multi-model NoSQL engines
    advanced_products = [
        {
            "name": "DynamoDB",
            "family": "Key-Value / Document",
            "primary_model": "Key-Value",
            "data_model": "Partition Key / JSON Document",
            "vendor": "Amazon Web Services",
            "use_case": "Shopping carts, high-throughput session state, gaming leaderboards",
            "open_source": False,
            "multi_model": True,
            "latency_tier": "Single-digit millisecond"
        },
        {
            "name": "InfluxDB",
            "family": "Wide-Column / Time-Series",
            "primary_model": "Time-Series",
            "data_model": "TSM Engine / Columnar Time-Series",
            "vendor": "InfluxData",
            "use_case": "IoT sensor telemetry, server metrics, real-time DevOps monitoring",
            "open_source": True,
            "multi_model": False,
            "latency_tier": "Sub-10 millisecond range scans"
        },
        {
            "name": "OrientDB",
            "family": "Multi-Model (Document + Graph)",
            "primary_model": "Graph / Document",
            "data_model": "Direct Pointer Graph + Document",
            "vendor": "OrientDB Ltd.",
            "use_case": "Fraud rings, recommendation networks, dynamic knowledge graphs",
            "open_source": True,
            "multi_model": True,
            "latency_tier": "Millisecond graph traversals"
        },
        {
            "name": "ScyllaDB",
            "family": "Wide-Column",
            "primary_model": "Wide-Column",
            "data_model": "Column-Family (C++ async architecture)",
            "vendor": "ScyllaDB Inc.",
            "use_case": "Ultra-low latency real-time messaging, financial tick data, ad-tech",
            "open_source": True,
            "multi_model": False,
            "latency_tier": "Sub-millisecond p99"
        },
        {
            "name": "ArangoDB",
            "family": "Multi-Model (Document + Graph + Search)",
            "primary_model": "Document / Graph",
            "data_model": "JSON Document + Graph Edge Traversal",
            "vendor": "ArangoDB GmbH",
            "use_case": "Master data management, identity graphs, integrated full-text search",
            "open_source": True,
            "multi_model": True,
            "latency_tier": "Millisecond multi-model queries"
        },
        {
            "name": "Google Cloud Bigtable",
            "family": "Wide-Column",
            "primary_model": "Wide-Column",
            "data_model": "Sparse multi-dimensional sorted map",
            "vendor": "Google Cloud",
            "use_case": "Petabyte-scale analytical workloads, financial time-series, GIS maps",
            "open_source": False,
            "multi_model": False,
            "latency_tier": "Low single-digit millisecond"
        },
        {
            "name": "ClickHouse",
            "family": "Columnar / OLAP",
            "primary_model": "Columnar",
            "data_model": "Column-Oriented Vectorized Execution",
            "vendor": "ClickHouse Inc.",
            "use_case": "Real-time analytical dashboards, clickstream web analytics, log exploration",
            "open_source": True,
            "multi_model": False,
            "latency_tier": "Sub-second aggregate scans on billions of rows"
        },
        {
            "name": "Firebase Firestore",
            "family": "Document",
            "primary_model": "Document",
            "data_model": "Hierarchical Document / Collection",
            "vendor": "Google",
            "use_case": "Mobile apps with offline sync, collaborative web applications",
            "open_source": False,
            "multi_model": False,
            "latency_tier": "Millisecond document listeners"
        }
    ]

    col.insert_many(advanced_products)
    print(f"[OK] Inserted {len(advanced_products)} advanced database products into 'database_products_tryit'.\n")

    # Display Rich Table
    table = Table(title="Activity 1.1 (Try It Yourself) - Advanced Database Product Survey", show_lines=True)
    table.add_column("Product", style="cyan", width=18)
    table.add_column("Classified Family", style="magenta", width=26)
    table.add_column("Vendor", style="yellow", width=20)
    table.add_column("Multi-Model?", justify="center", width=12)
    table.add_column("Primary Use Case", width=42)

    for p in col.find().sort("name"):
        table.add_row(
            p["name"],
            p["family"],
            p["vendor"],
            "[green]Yes[/green]" if p["multi_model"] else "[dim]No[/dim]",
            p["use_case"]
        )

    console.print(table)

    # Aggregation 1: Group by Classified Family
    print("\n--- Pipeline 1: Aggregation by NoSQL Family ---")
    pipeline_family = [
        {"$group": {"_id": "$family", "count": {"$sum": 1}, "products": {"$push": "$name"}}},
        {"$sort": {"count": -1}}
    ]
    for g in col.aggregate(pipeline_family):
        print(f"  {g['_id']:<32} : {g['count']} product(s) -> {', '.join(g['products'])}")

    # Aggregation 2: Multi-Model Architecture Ratio
    print("\n--- Pipeline 2: Architecture Model Distribution (Single vs Multi-Model) ---")
    pipeline_model = [
        {"$group": {"_id": "$multi_model", "count": {"$sum": 1}, "products": {"$push": "$name"}}},
        {"$sort": {"_id": -1}}
    ]
    for g in col.aggregate(pipeline_model):
        arch_type = "Multi-Model Engines" if g["_id"] else "Pure Single-Model Engines"
        print(f"  {arch_type:<24} : {g['count']} products -> {', '.join(g['products'])}")

    # Aggregation 3: Open-Source vs Cloud-Managed
    print("\n--- Pipeline 3: Licensing Breakdown (Open Source vs Managed) ---")
    pipeline_os = [
        {"$group": {"_id": "$open_source", "count": {"$sum": 1}, "products": {"$push": "$name"}}},
        {"$sort": {"_id": -1}}
    ]
    for g in col.aggregate(pipeline_os):
        lic_type = "Open-Source" if g["_id"] else "Proprietary / Managed Cloud"
        print(f"  {lic_type:<28} : {g['count']} products -> {', '.join(g['products'])}")

    # Interactive/Automated Classification Validation
    print("\n--- Automated Workload-to-NoSQL Family Validator ---")
    workload_tests = [
        {
            "scenario": "E-commerce shopping cart requiring sub-5ms lookup by customer_id",
            "expected_family": "Key-Value / Document",
            "matched_product": "DynamoDB"
        },
        {
            "scenario": "Industrial IoT factory floor streaming 100,000 sensor telemetry readings/sec",
            "expected_family": "Wide-Column / Time-Series",
            "matched_product": "InfluxDB"
        },
        {
            "scenario": "Fraud ring detection traversing relationships between documents and bank entities",
            "expected_family": "Multi-Model (Document + Graph)",
            "matched_product": "OrientDB"
        },
        {
            "scenario": "Ad-tech programmatic bidding needing sub-millisecond p99 latency without JVM pauses",
            "expected_family": "Wide-Column",
            "matched_product": "ScyllaDB"
        }
    ]

    for idx, test in enumerate(workload_tests, 1):
        product_doc = col.find_one({"name": test["matched_product"]})
        match_status = "[MATCH VALIDATED]" if product_doc and test["expected_family"] in product_doc["family"] else "[MISMATCH]"
        print(f"  [{idx}] Workload: {test['scenario']}")
        print(f"      Mapped Family: {test['expected_family']} | DB Candidate: {test['matched_product']} {match_status}")

    # Export collection to JSON file
    docs = list(col.find())
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab_01_try_yourself.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(docs, indent=2, default=json_util.default))
    print(f"\n[OK] Exported {len(docs)} documents to {os.path.basename(json_path)}")

    banner("Activity 1.1 (Try It Yourself) Complete")


if __name__ == "__main__":
    main()
