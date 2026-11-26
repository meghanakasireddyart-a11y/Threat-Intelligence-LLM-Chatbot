"""Activity 5.1 - Build a Sales Analytics Pipeline
Course: NoSQL Databases (MongoDB)
Author: Kasireddy Meghana (USN: 24BTRCL119)
Branch: CSE (AIML), Section B - Jain University

Demonstrates multi-stage aggregation pipelines:
1. $match -> $group -> $sort -> $project for monthly revenue
2. 3-Stage Pipeline ($match -> $group -> $sort) for category revenue
3. Top N customers by total spend
4. Average order value by status
5. $bucket numerical categorization
6. Conditional logic bucketing ($switch / $cond)
"""

import sys
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from config.connection import get_db, reset_collection, banner
from rich.table import Table
from rich.console import Console

console = Console()

ORDERS = [
    {"order_id": "ORD-101", "customer": "Arjun", "status": "completed", "total": 2500, "items": 3, "date": "2024-01-15", "region": "North", "category": "Electronics"},
    {"order_id": "ORD-102", "customer": "Sneha", "status": "completed", "total": 1800, "items": 1, "date": "2024-01-20", "region": "South", "category": "Apparel"},
    {"order_id": "ORD-103", "customer": "Arjun", "status": "completed", "total": 3200, "items": 5, "date": "2024-02-01", "region": "North", "category": "Electronics"},
    {"order_id": "ORD-104", "customer": "Kavya", "status": "cancelled", "total": 900, "items": 2, "date": "2024-02-05", "region": "East", "category": "Books"},
    {"order_id": "ORD-105", "customer": "Rahul", "status": "completed", "total": 5600, "items": 8, "date": "2024-02-10", "region": "West", "category": "Appliances"},
    {"order_id": "ORD-106", "customer": "Arjun", "status": "completed", "total": 1200, "items": 2, "date": "2024-02-15", "region": "North", "category": "Books"},
    {"order_id": "ORD-107", "customer": "Sneha", "status": "completed", "total": 4100, "items": 6, "date": "2024-03-01", "region": "South", "category": "Apparel"},
    {"order_id": "ORD-108", "customer": "Kavya", "status": "completed", "total": 2900, "items": 4, "date": "2024-03-05", "region": "East", "category": "Electronics"},
    {"order_id": "ORD-109", "customer": "Rahul", "status": "pending", "total": 7800, "items": 10, "date": "2024-03-10", "region": "West", "category": "Appliances"},
    {"order_id": "ORD-110", "customer": "Divya", "status": "completed", "total": 1500, "items": 1, "date": "2024-03-15", "region": "North", "category": "Apparel"},
]


def run_activity():
    banner("Activity 5.1: Sales Analytics Pipeline")
    print("Author: Kasireddy Meghana (USN: 24BTRCL119)")
    print("Course: NoSQL Databases (MongoDB)\n")

    db = get_db("nosql_labs")
    col = reset_collection("nosql_labs", "orders")
    col.insert_many(ORDERS)
    print(f"[OK] Seeded {len(ORDERS)} order documents into 'orders' collection.\n")

    analytics_summary = {}

    # --- PIPELINE 1: Monthly Revenue Report ---
    print("=== Pipeline 1: Monthly Revenue (Completed Orders Only) ===")
    pipeline_monthly = [
        {"$match": {"status": "completed"}},
        {"$group": {
            "_id": {"$substr": ["$date", 0, 7]},
            "total_revenue": {"$sum": "$total"},
            "order_count": {"$sum": 1},
            "avg_order_value": {"$avg": "$total"},
            "customers": {"$addToSet": "$customer"}
        }},
        {"$sort": {"_id": 1}},
        {"$project": {
            "month": "$_id",
            "total_revenue": 1,
            "order_count": 1,
            "avg_order_value": {"$round": ["$avg_order_value", 2]},
            "unique_customers": {"$size": "$customers"}
        }},
        {"$unset": "_id"},
    ]
    monthly_data = list(col.aggregate(pipeline_monthly))
    analytics_summary["monthly_revenue"] = monthly_data

    table = Table(title="Monthly Revenue Report")
    table.add_column("Month", style="cyan")
    table.add_column("Revenue", style="green", justify="right")
    table.add_column("Orders", justify="right")
    table.add_column("Avg Value", justify="right")
    table.add_column("Customers", justify="right")
    for row in monthly_data:
        table.add_row(
            row["month"], f"${row['total_revenue']:,.0f}",
            str(row["order_count"]), f"${row['avg_order_value']:,.2f}",
            str(row["unique_customers"])
        )
    console.print(table)

    # --- PIPELINE 2: Total Revenue by Category (3-Stage: $match -> $group -> $sort) ---
    print("\n=== Pipeline 2: Category Revenue (Highest First - 3 Stages) ===")
    pipeline_category = [
        {"$match": {"status": "completed"}},
        {"$group": {
            "_id": "$category",
            "total_revenue": {"$sum": "$total"},
            "order_count": {"$sum": 1},
            "avg_order_value": {"$avg": "$total"}
        }},
        {"$sort": {"total_revenue": -1}}
    ]
    category_data = list(col.aggregate(pipeline_category))
    analytics_summary["category_revenue"] = category_data
    for row in category_data:
        print(f"  {row['_id']:<15} ${row['total_revenue']:>8,.0f} across {row['order_count']} orders (avg: ${row['avg_order_value']:,.2f})")

    # --- PIPELINE 3: Top 3 Customers by Total Spend ---
    print("\n=== Pipeline 3: Top 3 Customers by Total Spending ===")
    pipeline_top = [
        {"$match": {"status": "completed"}},
        {"$group": {
            "_id": "$customer",
            "total_spent": {"$sum": "$total"},
            "orders": {"$sum": 1},
            "items_bought": {"$sum": "$items"}
        }},
        {"$sort": {"total_spent": -1}},
        {"$limit": 3}
    ]
    top_data = list(col.aggregate(pipeline_top))
    analytics_summary["top_customers"] = top_data
    for row in top_data:
        print(f"  {row['_id']:<12} ${row['total_spent']:>8,.0f} across {row['orders']} orders ({row['items_bought']} items)")

    # --- PIPELINE 4: Average Order Value by Status ---
    print("\n=== Pipeline 4: Avg Order Value by Status ===")
    pipeline_status = [
        {"$group": {
            "_id": "$status",
            "avg_value": {"$avg": "$total"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"avg_value": -1}}
    ]
    status_data = list(col.aggregate(pipeline_status))
    analytics_summary["order_status_breakdown"] = status_data
    for row in status_data:
        print(f"  {row['_id']:<12} avg=${row['avg_value']:>8,.2f} ({row['count']} orders)")

    # --- PIPELINE 5: $bucket Categorization ---
    print("\n=== Pipeline 5: Order Value Buckets ($bucket stage) ===")
    pipeline_bucket = [
        {"$bucket": {
            "groupBy": "$total",
            "boundaries": [0, 1000, 3000, 5000, 10000],
            "default": "Very High",
            "output": {"count": {"$sum": 1}, "total": {"$sum": "$total"}}
        }}
    ]
    labels = ["$0 - $1K", "$1K - $3K", "$3K - $5K", "$5K - $10K", "Very High"]
    bucket_data = []
    for i, row in enumerate(col.aggregate(pipeline_bucket)):
        label = labels[i] if i < len(labels) else str(row["_id"])
        bucket_data.append({"bucket": label, "count": row["count"], "total": row["total"]})
        print(f"  {label:<15} {row['count']} orders, total=${row['total']:,.0f}")
    analytics_summary["bucket_analysis"] = bucket_data

    # --- PIPELINE 6: Conditional Bucketing ($switch / $cond) ---
    print("\n=== Pipeline 6: Conditional Order Sizing ($switch / $cond) ===")
    pipeline_conditional = [
        {"$match": {"status": "completed"}},
        {"$project": {
            "order_id": 1,
            "customer": 1,
            "total": 1,
            "order_size": {
                "$switch": {
                    "branches": [
                        {"case": {"$lt": ["$total", 2000]}, "then": "Small (< $2,000)"},
                        {"case": {"$and": [{"$gte": ["$total", 2000]}, {"$lt": ["$total", 4000]}]}, "then": "Medium ($2,000 - $4,000)"}
                    ],
                    "default": "Large (>= $4,000)"
                }
            }
        }},
        {"$group": {
            "_id": "$order_size",
            "count": {"$sum": 1},
            "total_revenue": {"$sum": "$total"},
            "avg_order_value": {"$avg": "$total"},
            "sample_orders": {"$push": "$order_id"}
        }},
        {"$sort": {"total_revenue": -1}}
    ]
    cond_data = list(col.aggregate(pipeline_conditional))
    analytics_summary["conditional_sizing"] = cond_data
    for row in cond_data:
        print(f"  {row['_id']:<25} {row['count']} orders | Total: ${row['total_revenue']:>7,.0f} | Orders: {', '.join(row['sample_orders'])}")

    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sales_analytics_output.json")
    with open(out_file, "w") as f:
        json.dump(analytics_summary, f, indent=2, default=str)
    print(f"\n[OK] Pipeline analytics exported to {out_file}")

    banner("Activity 5.1 Complete")


if __name__ == "__main__":
    run_activity()
