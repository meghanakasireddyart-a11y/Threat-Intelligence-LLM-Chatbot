"""Activity 5.2 - Join Data with $lookup
Course: NoSQL Databases (MongoDB)
Author: Kasireddy Meghana (USN: 24BTRCL119)
Branch: CSE (AIML), Section B - Jain University

Demonstrates MongoDB Joins:
1. Basic $lookup: 1:1 join between Orders and Customers, unwinding single subdocument.
2. Left Outer Join for Non-Matches: Pipeline-style $lookup to identify never-ordered products.
3. Nested Array Unwind & Join: Orders referencing multiple product IDs joined to Products collection.
4. Customer Spending Portfolio: $lookup from Customers to Orders, computing aggregate spending.
"""

import sys
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from config.connection import get_db, reset_collection, banner

ORDERS = [
    {"order_id": "ORD-201", "customer_id": "C001", "product_ids": ["P001", "P002"], "total": 350},
    {"order_id": "ORD-202", "customer_id": "C002", "product_ids": ["P003"], "total": 150},
    {"order_id": "ORD-203", "customer_id": "C003", "product_ids": ["P001", "P004", "P005"], "total": 680},
    {"order_id": "ORD-204", "customer_id": "C001", "product_ids": [], "total": 0},  # empty order
]

CUSTOMERS = [
    {"customer_id": "C001", "name": "Arjun", "tier": "Gold", "city": "Bangalore"},
    {"customer_id": "C002", "name": "Sneha", "tier": "Silver", "city": "Mumbai"},
    {"customer_id": "C003", "name": "Rahul", "tier": "Platinum", "city": "Delhi"},
]

PRODUCTS = [
    {"product_id": "P001", "name": "Widget A", "category": "Electronics", "price": 200},
    {"product_id": "P002", "name": "Gadget B", "category": "Accessories", "price": 150},
    {"product_id": "P003", "name": "Widget C", "category": "Electronics", "price": 150},
    {"product_id": "P004", "name": "Gadget D", "category": "Tools", "price": 280},
    {"product_id": "P005", "name": "Widget E", "category": "Consumables", "price": 200},
    {"product_id": "P006", "name": "Sensor Pro F", "category": "Smart Home", "price": 420},  # Never ordered!
]


def run_activity():
    banner("Activity 5.2: $lookup Joins in MongoDB")
    print("Author: Kasireddy Meghana (USN: 24BTRCL119)")
    print("Course: NoSQL Databases (MongoDB)\n")

    db = get_db("nosql_labs")
    orders_col = reset_collection("nosql_labs", "orders_join")
    customers_col = reset_collection("nosql_labs", "customers_join")
    products_col = reset_collection("nosql_labs", "products_join")

    orders_col.insert_many(ORDERS)
    customers_col.insert_many(CUSTOMERS)
    products_col.insert_many(PRODUCTS)
    print(f"[OK] Seeded orders ({len(ORDERS)}), customers ({len(CUSTOMERS)}), products ({len(PRODUCTS)}).\n")

    join_results = {}

    # --- PIPELINE 1: Basic $lookup (Orders + Customers) ---
    print("=== 1. Orders Enriched with Customer Details ===")
    pipeline_cust = [
        {"$lookup": {
            "from": "customers_join",
            "localField": "customer_id",
            "foreignField": "customer_id",
            "as": "customer"
        }},
        {"$unwind": "$customer"},
        {"$project": {
            "order_id": 1,
            "total": 1,
            "customer_name": "$customer.name",
            "customer_tier": "$customer.tier",
            "city": "$customer.city"
        }}
    ]
    p1_res = list(orders_col.aggregate(pipeline_cust))
    join_results["orders_with_customers"] = p1_res
    for row in p1_res:
        print(f"  {row['order_id']:<10} {row['customer_name']:<10} [{row['customer_tier']}] ${row['total']} ({row['city']})")

    # --- PIPELINE 2: Left Join for Non-Matches (Products Never Ordered) ---
    print("\n=== 2. Products Never Ordered (Left Join + Empty Array Filter) ===")
    print("  Filter condition rationale: If a product was never ordered, the joined 'ordered'")
    print("  array produced by $lookup will have length 0: { $match: { 'ordered': { $size: 0 } } }.")
    pipeline_never = [
        {"$lookup": {
            "from": "orders_join",
            "let": {"pid": "$product_id"},
            "pipeline": [
                {"$unwind": "$product_ids"},
                {"$match": {"$expr": {"$eq": ["$product_ids", "$$pid"]}}},
                {"$limit": 1}
            ],
            "as": "ordered"
        }},
        {"$match": {"ordered": {"$size": 0}}},
        {"$project": {"product_id": 1, "name": 1, "category": 1, "price": 1, "_id": 0}}
    ]
    never_ordered = list(products_col.aggregate(pipeline_never))
    join_results["products_never_ordered"] = never_ordered
    if never_ordered:
        for p in never_ordered:
            print(f"  [UNORDERED] {p['product_id']:<8} {p['name']:<15} [{p['category']}] ${p['price']}")
    else:
        print("  All products have been ordered at least once.")

    # --- PIPELINE 3: Order Line Items (Unwind products + $lookup) ---
    print("\n=== 3. Order Line Items (Unwind products + $lookup) ===")
    pipeline_line = [
        {"$unwind": {"path": "$product_ids", "preserveNullAndEmptyArrays": True}},
        {"$lookup": {
            "from": "products_join",
            "localField": "product_ids",
            "foreignField": "product_id",
            "as": "product_info"
        }},
        {"$unwind": {"path": "$product_info", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "order_id": 1,
            "product_id": "$product_ids",
            "product_name": "$product_info.name",
            "product_price": "$product_info.price"
        }}
    ]
    p3_res = list(orders_col.aggregate(pipeline_line))
    join_results["order_line_items"] = p3_res
    for row in p3_res:
        pname = row.get("product_name") or "(no product)"
        pprice = row.get("product_price") or 0
        print(f"  {row['order_id']:<10} -> {pname:<15} ${pprice}")

    # --- PIPELINE 4: Customer Spending Portfolio ($lookup from Customers to Orders) ---
    print("\n=== 4. Customer Spending Portfolio (Customers -> Orders Join) ===")
    pipeline_cust_summary = [
        {"$lookup": {
            "from": "orders_join",
            "localField": "customer_id",
            "foreignField": "customer_id",
            "as": "customer_orders"
        }},
        {"$project": {
            "customer_id": 1,
            "name": 1,
            "tier": 1,
            "city": 1,
            "order_count": {"$size": "$customer_orders"},
            "total_spent": {"$sum": "$customer_orders.total"},
            "order_ids": "$customer_orders.order_id"
        }},
        {"$sort": {"total_spent": -1}}
    ]
    p4_res = list(customers_col.aggregate(pipeline_cust_summary))
    join_results["customer_spending_portfolio"] = p4_res
    for row in p4_res:
        print(f"  {row['name']:<10} [{row['tier']}] Orders: {row['order_count']} | Total Spent: ${row['total_spent']:>4} | Orders: {row['order_ids']}")

    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lookup_joins_output.json")
    with open(out_file, "w") as f:
        json.dump(join_results, f, indent=2, default=str)
    print(f"\n[OK] Join analytics exported to {out_file}")

    banner("Activity 5.2 Complete")


if __name__ == "__main__":
    run_activity()
