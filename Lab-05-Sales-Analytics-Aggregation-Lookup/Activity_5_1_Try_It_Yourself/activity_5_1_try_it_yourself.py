"""Activity 5.1 Try It Yourself - Advanced Multi-Stage Analytics & Conditional Logic
Course: NoSQL Databases (MongoDB)
Author: Kasireddy Meghana (USN: 24BTRCL119)
Branch: CSE (AIML), Section B - Jain University

Tasks:
1. Sketch and verify the 3-Stage Pipeline: $match -> $group -> $sort for regional and category revenue.
2. Advanced conditional bucketing ($switch / $cond) with VIP Customer Segmentation.
3. Statistical metrics ($min, $max, $avg, $stdDevPop) across product categories.
4. Dynamic discount eligibility tagging using $addFields and $cond expressions.
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

EXTENDED_ORDERS = [
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
    {"order_id": "ORD-111", "customer": "Manish", "status": "completed", "total": 6200, "items": 7, "date": "2024-03-20", "region": "East", "category": "Electronics"},
    {"order_id": "ORD-112", "customer": "Pooja", "status": "completed", "total": 850, "items": 1, "date": "2024-03-22", "region": "South", "category": "Books"},
]


def run_try_it_yourself():
    banner("Activity 5.1 Try It Yourself: Advanced Aggregations")
    print("Author: Kasireddy Meghana (USN: 24BTRCL119)")
    print("Course: NoSQL Databases (MongoDB)\n")

    db = get_db("nosql_labs")
    col = reset_collection("nosql_labs", "orders_extended")
    col.insert_many(EXTENDED_ORDERS)
    print(f"[OK] Seeded {len(EXTENDED_ORDERS)} extended orders.\n")

    output_data = {}

    # --- TASK 1: Regional Sales Pipeline (Exact 3-Stage: $match -> $group -> $sort) ---
    print("=== 1. Regional Sales Performance (3-Stage: $match -> $group -> $sort) ===")
    pipeline_region = [
        {"$match": {"status": "completed"}},
        {"$group": {
            "_id": "$region",
            "total_revenue": {"$sum": "$total"},
            "order_count": {"$sum": 1},
            "avg_spend": {"$avg": "$total"},
            "total_items": {"$sum": "$items"}
        }},
        {"$sort": {"total_revenue": -1}}
    ]
    reg_res = list(col.aggregate(pipeline_region))
    output_data["regional_revenue"] = reg_res
    for r in reg_res:
        print(f"  Region: {r['_id']:<8} | Revenue: ${r['total_revenue']:>7,.0f} | Orders: {r['order_count']} | Avg: ${r['avg_spend']:>7,.2f}")

    # --- TASK 2: Customer Tier Classification using $switch ---
    print("\n=== 2. Customer Spending Tier Classification ($switch / $cond) ===")
    pipeline_tiers = [
        {"$match": {"status": "completed"}},
        {"$group": {
            "_id": "$customer",
            "total_spent": {"$sum": "$total"},
            "order_count": {"$sum": 1},
            "total_items": {"$sum": "$items"}
        }},
        {"$project": {
            "customer": "$_id",
            "total_spent": 1,
            "order_count": 1,
            "tier": {
                "$switch": {
                    "branches": [
                        {"case": {"$gte": ["$total_spent", 6000]}, "then": "VIP Platinum"},
                        {"case": {"$gte": ["$total_spent", 3000]}, "then": "Gold Member"}
                    ],
                    "default": "Standard Silver"
                }
            }
        }},
        {"$sort": {"total_spent": -1}}
    ]
    tier_res = list(col.aggregate(pipeline_tiers))
    output_data["customer_tier_segmentation"] = tier_res
    for t in tier_res:
        print(f"  {t['customer']:<10} | Spent: ${t['total_spent']:>7,.0f} | Orders: {t['order_count']} | Tier: [{t['tier']}]")

    # --- TASK 3: Statistical Aggregations by Category ($min, $max, $avg, $stdDevPop) ---
    print("\n=== 3. Category Statistical Metrics ($min, $max, $avg, $stdDevPop) ===")
    pipeline_stats = [
        {"$match": {"status": "completed"}},
        {"$group": {
            "_id": "$category",
            "count": {"$sum": 1},
            "min_order": {"$min": "$total"},
            "max_order": {"$max": "$total"},
            "avg_order": {"$avg": "$total"},
            "std_dev": {"$stdDevPop": "$total"}
        }},
        {"$project": {
            "category": "$_id",
            "count": 1,
            "min_order": 1,
            "max_order": 1,
            "avg_order": {"$round": ["$avg_order", 2]},
            "std_dev": {"$round": [{"$ifNull": ["$std_dev", 0]}, 2]}
        }},
        {"$sort": {"count": -1}}
    ]
    stat_res = list(col.aggregate(pipeline_stats))
    output_data["statistical_metrics"] = stat_res
    for s in stat_res:
        print(f"  {s['category']:<15} Count: {s['count']} | Min: ${s['min_order']} | Max: ${s['max_order']} | Avg: ${s['avg_order']} | StdDev: ${s['std_dev']}")

    # --- TASK 4: Dynamic VIP Discount Calculation ($addFields + $cond) ---
    print("\n=== 4. Dynamic VIP Discount & Effective Revenue ($addFields + $cond) ===")
    pipeline_discounts = [
        {"$match": {"status": "completed"}},
        {"$addFields": {
            "discount_pct": {
                "$cond": {
                    "if": {"$gte": ["$total", 5000]},
                    "then": 0.15,
                    "else": {
                        "$cond": {
                            "if": {"$gte": ["$total", 2500]},
                            "then": 0.08,
                            "else": 0.0
                        }
                    }
                }
            }
        }},
        {"$addFields": {
            "discount_amount": {"$multiply": ["$total", "$discount_pct"]},
            "net_total": {"$subtract": ["$total", {"$multiply": ["$total", "$discount_pct"]}]}
        }},
        {"$project": {
            "order_id": 1,
            "customer": 1,
            "category": 1,
            "total": 1,
            "discount_pct": {"$multiply": ["$discount_pct", 100]},
            "net_total": {"$round": ["$net_total", 2]}
        }},
        {"$sort": {"net_total": -1}},
        {"$limit": 5}
    ]
    disc_res = list(col.aggregate(pipeline_discounts))
    output_data["discounted_orders"] = disc_res
    for d in disc_res:
        print(f"  {d['order_id']:<10} {d['customer']:<10} Gross: ${d['total']:>6,.0f} | Disc: {d['discount_pct']:>2.0f}% | Net: ${d['net_total']:>7,.2f}")

    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conditional_bucketing_output.json")
    with open(out_file, "w") as f:
        json.dump(output_data, f, indent=2, default=str)
    print(f"\n[OK] Try It Yourself analytics saved to {out_file}")

    banner("Activity 5.1 Try It Yourself Complete")


if __name__ == "__main__":
    run_try_it_yourself()
