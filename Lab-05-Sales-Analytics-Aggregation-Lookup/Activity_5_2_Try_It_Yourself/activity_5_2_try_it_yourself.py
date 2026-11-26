"""Activity 5.2 Try It Yourself - Multi-Collection Joins & Non-Match Filtering
Course: NoSQL Databases (MongoDB)
Author: Kasireddy Meghana (USN: 24BTRCL119)
Branch: CSE (AIML), Section B - Jain University

Tasks:
1. Double $lookup Pipeline: Join Orders -> Customers AND Orders -> Products for full invoice documents.
2. Inactive Customer Detection: Left Join from Customers to Orders to find customers with zero orders.
3. Product Category Sales Analytics: Join Orders -> Products and compute total sales and units per product category.
4. Export enriched join dataset to customer_orders_portfolio.json.
"""

import sys
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from config.connection import get_db, reset_collection, banner

EXTENDED_ORDERS = [
    {"order_id": "ORD-301", "customer_id": "C101", "product_ids": ["P001", "P002"], "total": 350, "date": "2024-03-01"},
    {"order_id": "ORD-302", "customer_id": "C102", "product_ids": ["P003"], "total": 150, "date": "2024-03-02"},
    {"order_id": "ORD-303", "customer_id": "C103", "product_ids": ["P001", "P004", "P005"], "total": 680, "date": "2024-03-05"},
    {"order_id": "ORD-304", "customer_id": "C101", "product_ids": ["P002", "P003"], "total": 300, "date": "2024-03-08"},
]

EXTENDED_CUSTOMERS = [
    {"customer_id": "C101", "name": "Arjun", "tier": "Gold", "city": "Bangalore"},
    {"customer_id": "C102", "name": "Sneha", "tier": "Silver", "city": "Mumbai"},
    {"customer_id": "C103", "name": "Rahul", "tier": "Platinum", "city": "Delhi"},
    {"customer_id": "C104", "name": "Vikram", "tier": "Bronze", "city": "Chennai"},  # Inactive customer!
]

EXTENDED_PRODUCTS = [
    {"product_id": "P001", "name": "Widget A", "category": "Electronics", "price": 200},
    {"product_id": "P002", "name": "Gadget B", "category": "Accessories", "price": 150},
    {"product_id": "P003", "name": "Widget C", "category": "Electronics", "price": 150},
    {"product_id": "P004", "name": "Gadget D", "category": "Tools", "price": 280},
    {"product_id": "P005", "name": "Widget E", "category": "Consumables", "price": 200},
    {"product_id": "P006", "name": "Smart Hub F", "category": "Smart Home", "price": 450},  # Never ordered!
]


def run_try_it_yourself():
    banner("Activity 5.2 Try It Yourself: Advanced Joins")
    print("Author: Kasireddy Meghana (USN: 24BTRCL119)")
    print("Course: NoSQL Databases (MongoDB)\n")

    db = get_db("nosql_labs")
    orders_col = reset_collection("nosql_labs", "ext_orders")
    customers_col = reset_collection("nosql_labs", "ext_customers")
    products_col = reset_collection("nosql_labs", "ext_products")

    orders_col.insert_many(EXTENDED_ORDERS)
    customers_col.insert_many(EXTENDED_CUSTOMERS)
    products_col.insert_many(EXTENDED_PRODUCTS)
    print(f"[OK] Seeded extended collections: orders ({len(EXTENDED_ORDERS)}), customers ({len(EXTENDED_CUSTOMERS)}), products ({len(EXTENDED_PRODUCTS)}).\n")

    output_portfolio = {}

    # --- TASK 1: Full Invoice Generation (Double $lookup: Orders -> Customers AND Orders -> Products) ---
    print("=== 1. Complete Order Invoices (Orders + Customers + Products Double Join) ===")
    pipeline_invoice = [
        # Join Customer details
        {"$lookup": {
            "from": "ext_customers",
            "localField": "customer_id",
            "foreignField": "customer_id",
            "as": "customer_doc"
        }},
        {"$unwind": "$customer_doc"},
        # Join Products array
        {"$lookup": {
            "from": "ext_products",
            "localField": "product_ids",
            "foreignField": "product_id",
            "as": "items_detail"
        }},
        {"$project": {
            "order_id": 1,
            "date": 1,
            "order_total": "$total",
            "customer_name": "$customer_doc.name",
            "customer_city": "$customer_doc.city",
            "item_count": {"$size": "$items_detail"},
            "item_names": "$items_detail.name"
        }},
        {"$sort": {"date": 1}}
    ]
    invoices = list(orders_col.aggregate(pipeline_invoice))
    output_portfolio["complete_invoices"] = invoices
    for inv in invoices:
        items_str = ", ".join(inv["item_names"])
        print(f"  {inv['order_id']} | {inv['customer_name']} ({inv['customer_city']}) | Total: ${inv['order_total']} | Items ({inv['item_count']}): [{items_str}]")

    # --- TASK 2: Non-Matches: Inactive Customers (Left Join Customers -> Orders) ---
    print("\n=== 2. Inactive Customers with Zero Orders (Left Join Non-Match Pattern) ===")
    pipeline_inactive = [
        {"$lookup": {
            "from": "ext_orders",
            "localField": "customer_id",
            "foreignField": "customer_id",
            "as": "placed_orders"
        }},
        {"$match": {"placed_orders": {"$size": 0}}},
        {"$project": {
            "customer_id": 1,
            "name": 1,
            "tier": 1,
            "city": 1,
            "_id": 0
        }}
    ]
    inactive_custs = list(customers_col.aggregate(pipeline_inactive))
    output_portfolio["inactive_customers"] = inactive_custs
    for ic in inactive_custs:
        print(f"  [INACTIVE] {ic['customer_id']} - {ic['name']} ({ic['city']}) | Tier: {ic['tier']} (Zero Orders Placed)")

    # --- TASK 3: Product Category Sales Performance via Joined Data ---
    print("\n=== 3. Product Category Revenue from Orders via $lookup ===")
    pipeline_cat_sales = [
        {"$unwind": "$product_ids"},
        {"$lookup": {
            "from": "ext_products",
            "localField": "product_ids",
            "foreignField": "product_id",
            "as": "product"
        }},
        {"$unwind": "$product"},
        {"$group": {
            "_id": "$product.category",
            "units_ordered": {"$sum": 1},
            "estimated_revenue": {"$sum": "$product.price"},
            "unique_products": {"$addToSet": "$product.name"}
        }},
        {"$sort": {"estimated_revenue": -1}}
    ]
    cat_sales = list(orders_col.aggregate(pipeline_cat_sales))
    output_portfolio["category_sales_performance"] = cat_sales
    for cs in cat_sales:
        prods_str = ", ".join(cs["unique_products"])
        print(f"  Category: {cs['_id']:<15} Units: {cs['units_ordered']} | Est. Revenue: ${cs['estimated_revenue']:>5} | Products: [{prods_str}]")

    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "customer_orders_portfolio.json")
    with open(out_file, "w") as f:
        json.dump(output_portfolio, f, indent=2, default=str)
    print(f"\n[OK] Portfolio analysis saved to {out_file}")

    banner("Activity 5.2 Try It Yourself Complete")


if __name__ == "__main__":
    run_try_it_yourself()
