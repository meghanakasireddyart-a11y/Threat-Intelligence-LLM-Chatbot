"""Activity 1.2 (Try It Yourself) - Enterprise Polyglot Persistence Architecture Mapping

Maps data domains of two complex modern enterprise systems to NoSQL families:
1. Global E-Commerce & Retail Platform (Amazon / Flipkart scale)
2. Smart Healthcare & Remote Patient Telemetry System

Demonstrates how real-world system architects leverage polyglot persistence based on
read/write workload patterns, latency SLAs, consistency requirements, and data relationships.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.connection import get_db, reset_collection, banner
from rich.table import Table
from rich.console import Console
import json
from bson import json_util

console = Console()


def main():
    banner("Activity 1.2 (Try It Yourself): Enterprise Polyglot Persistence Mapping")

    db = get_db("nosql_labs")
    col = reset_collection("nosql_labs", "app_domain_mapping_tryit")

    # --- Application 1: Global E-Commerce & Retail Platform ---
    print("=== Application 1: Global E-Commerce Platform ===")
    ecommerce_domains = [
        {
            "app": "Global E-Commerce",
            "domain": "product_catalog",
            "description": "Multi-category product catalog with polymorphic attributes (electronics, clothing, grocery)",
            "read_write_pattern": "Heavy read (cached), periodic seller updates, dynamic schema",
            "recommended_family": "Document",
            "recommended_db": "MongoDB",
            "rationale": "Flexible JSON/BSON schema accommodates arbitrary product attributes without sparse tables or ALTER TABLE migrations"
        },
        {
            "app": "Global E-Commerce",
            "domain": "shopping_cart_sessions",
            "description": "Transient active user shopping carts, temporary reservations, and authentication tokens",
            "read_write_pattern": "Extreme read/write rate, sub-millisecond SLA, TTL auto-expiry",
            "recommended_family": "Key-Value",
            "recommended_db": "Redis",
            "rationale": "In-memory key lookup delivers sub-millisecond response times with native TTL key expiration for abandoned carts"
        },
        {
            "app": "Global E-Commerce",
            "domain": "checkout_order_ledger",
            "description": "Completed customer orders, payment receipts, invoice history, and settlement records",
            "read_write_pattern": "Write-once, strong consistency required, multi-document ACID transactions",
            "recommended_family": "Document",
            "recommended_db": "MongoDB (ACID Transactions)",
            "rationale": "Multi-document distributed transactions guarantee financial atomicity; rich document structure preserves order snapshot"
        },
        {
            "app": "Global E-Commerce",
            "domain": "recommendation_social_graph",
            "description": "Collaborative filtering, 'Frequently Bought Together' item associations, and influencer graphs",
            "read_write_pattern": "Multi-hop graph traversal, path finding, relationship queries",
            "recommended_family": "Graph",
            "recommended_db": "Neo4j",
            "rationale": "Index-free adjacency traverses multi-hop item and user relationships exponentially faster than relational SQL joins"
        },
        {
            "app": "Global E-Commerce",
            "domain": "clickstream_event_logging",
            "description": "User clicks, impressions, scrolling events, and hover tracking across millions of concurrent users",
            "read_write_pattern": "Massive write-heavy append-only ingestion, partitioned time-series queries",
            "recommended_family": "Wide-Column",
            "recommended_db": "Apache Cassandra",
            "rationale": "LSM-tree storage engine provides linearly scalable write throughput with zero single point of failure"
        },
        {
            "app": "Global E-Commerce",
            "domain": "product_search_and_discovery",
            "description": "Tokenized text search, fuzzy spell-correction, and faceted price/brand filtering",
            "read_write_pattern": "Read-heavy search queries, asynchronous catalog re-indexing",
            "recommended_family": "Search / Inverted Index",
            "recommended_db": "Elasticsearch / Atlas Search",
            "rationale": "Inverted index enables tokenized relevance scoring, n-gram fuzzy matching, and instant faceted counts"
        }
    ]

    # --- Application 2: Smart Healthcare & Remote Patient Telemetry System ---
    print("=== Application 2: Smart Healthcare & Telemetry System ===")
    healthcare_domains = [
        {
            "app": "Smart Healthcare & Telemetry",
            "domain": "patient_health_records",
            "description": "Longitudinal patient clinical charts, physician encounter notes, and lab diagnostic histories",
            "read_write_pattern": "Read-heavy clinical view, occasional updates, complex nested records",
            "recommended_family": "Document",
            "recommended_db": "MongoDB",
            "rationale": "Hierarchical document structure maps naturally to FHIR / HL7 clinical standards and nested medical reports"
        },
        {
            "app": "Smart Healthcare & Telemetry",
            "domain": "vital_signs_iot_telemetry",
            "description": "High-frequency streaming telemetry from ICU monitors, ECG patches, and pulse oximeters",
            "read_write_pattern": "Extreme append-only time-series stream, time-window aggregations",
            "recommended_family": "Wide-Column / Time-Series",
            "recommended_db": "Apache Cassandra / InfluxDB",
            "rationale": "Optimized time-partitioned storage compresses telemetry streams and handles millions of data points per second"
        },
        {
            "app": "Smart Healthcare & Telemetry",
            "domain": "emergency_alert_cache",
            "description": "Real-time clinician paging queues, critical arrhythmia notifications, and alert state machines",
            "read_write_pattern": "Sub-millisecond pub/sub, immediate in-memory deduplication and dispatch",
            "recommended_family": "Key-Value",
            "recommended_db": "Redis",
            "rationale": "Built-in Pub/Sub channels and in-memory speed ensure instantaneous routing of life-critical alerts"
        },
        {
            "app": "Smart Healthcare & Telemetry",
            "domain": "epidemiological_contact_tracing",
            "description": "Infectious disease transmission modeling, patient contact exposure chains, and hospital outbreak vectors",
            "read_write_pattern": "Deep multi-hop relationship traversals, cluster and community detection",
            "recommended_family": "Graph",
            "recommended_db": "Neo4j",
            "rationale": "Graph algorithms (shortest path, community detection) isolate infection clusters and track patient exposure paths"
        }
    ]

    all_domains = ecommerce_domains + healthcare_domains
    col.insert_many(all_domains)
    print(f"[OK] Inserted {len(all_domains)} enterprise domain mappings into 'app_domain_mapping_tryit'.\n")

    # Print tables per application
    for app_name in ["Global E-Commerce", "Smart Healthcare & Telemetry"]:
        table = Table(title=f"Activity 1.2 (Try It Yourself) - {app_name} Architecture", show_lines=True)
        table.add_column("Domain", style="cyan", width=24)
        table.add_column("Description", width=46)
        table.add_column("NoSQL Family", style="magenta", width=18)
        table.add_column("Recommended DB", style="green", width=22)
        table.add_column("Key Architectural Rationale", width=42)

        for d in col.find({"app": app_name}):
            table.add_row(
                d["domain"],
                d["description"],
                d["recommended_family"],
                d["recommended_db"],
                d["rationale"]
            )
        console.print(table)
        print()

    # Aggregation 1: Overall Family Distribution across Enterprise Architectures
    print("--- Pipeline 1: Enterprise Polyglot Family Distribution ---")
    pipeline_family = [
        {"$group": {"_id": "$recommended_family", "count": {"$sum": 1}, "domains": {"$push": "$domain"}}},
        {"$sort": {"count": -1}}
    ]
    for g in col.aggregate(pipeline_family):
        print(f"  {g['_id']:<26} : {g['count']} domain(s) -> {', '.join(g['domains'])}")

    # Aggregation 2: Access Pattern Category Breakdown
    print("\n--- Pipeline 2: Workload Profile Breakdown ---")
    pipeline_patterns = [
        {"$group": {"_id": "$recommended_family", "total": {"$sum": 1}, "apps": {"$addToSet": "$app"}}},
        {"$sort": {"total": -1}}
    ]
    for g in col.aggregate(pipeline_patterns):
        apps_str = ", ".join(g["apps"])
        print(f"  {g['_id']:<26} : {g['total']} domain(s) across [{apps_str}]")

    # Export collection to JSON file
    docs = list(col.find())
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab_02_try_yourself.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(docs, indent=2, default=json_util.default))
    print(f"\n[OK] Exported {len(docs)} documents to {os.path.basename(json_path)}")

    banner("Activity 1.2 (Try It Yourself) Complete")


if __name__ == "__main__":
    main()
