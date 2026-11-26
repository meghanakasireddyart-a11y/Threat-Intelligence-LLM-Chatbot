"""
Lab 4.2: Implement Upsert and Bulk Operations
Course: NoSQL Databases (MongoDB)
Author: Kasireddy Meghana (USN: 24BTRCL119)
Branch: CSE (AIML), Section B - Jain University

Covers:
1. Upsert function taking SKU and price (updates if exists, inserts with defaults if not)
2. Bulk write processing 5 simultaneous updates (increase stock by 10 for A, B, C; set is_active to false for D, E)
3. BulkWriteResult verification (matched, modified, upserted counts and IDs)
4. Export inventory state to JSON
"""

import os
import sys
import json
from bson import json_util
from pymongo import UpdateOne

# Add parent directory for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.connection import get_db, reset_collection, banner


# Seed inventory containing items PROD-A through PROD-E
INITIAL_INVENTORY = [
    {"sku": "PROD-A", "name": "Wireless Ergonomic Mouse", "price": 29.99, "stock": 40, "is_active": True},
    {"sku": "PROD-B", "name": "Mechanical Gaming Keyboard", "price": 89.99, "stock": 25, "is_active": True},
    {"sku": "PROD-C", "name": "USB-C Fast Charging Hub", "price": 39.99, "stock": 15, "is_active": True},
    {"sku": "PROD-D", "name": "Legacy VGA to HDMI Adapter", "price": 12.50, "stock": 50, "is_active": True},
    {"sku": "PROD-E", "name": "Discontinued Bluetooth Dongle", "price": 8.00, "stock": 30, "is_active": True},
]


def upsert_product_price(col, sku, price, default_values=None):
    """
    Instruction 1:
    Takes product SKU and price.
    If SKU exists, update the price.
    If not, insert a new document with default values.
    Uses update_one with upsert=True.
    """
    defaults = default_values or {
        "name": f"Catalog Item {sku}",
        "stock": 0,
        "is_active": True,
        "category": "Uncategorized",
        "tags": ["auto-created", "upserted"]
    }

    update_payload = {
        "$set": {"price": float(price)},
        "$setOnInsert": {
            "sku": sku,
            **defaults
        }
    }

    result = col.update_one({"sku": sku}, update_payload, upsert=True)
    
    if result.upserted_id is not None:
        action = "INSERTED (UPSERT)"
        details = f"New document created with _id: {result.upserted_id}"
    elif result.matched_count > 0:
        action = "UPDATED (EXISTING)"
        details = f"Existing document matched. Modified: {result.modified_count}"
    else:
        action = "NO-OP"
        details = "No changes applied"

    print(f"  [{action}] SKU: {sku} | New Price: ${price:.2f} | {details}")
    return result


def display_inventory_table(title, docs):
    """Print tabular view of inventory documents."""
    print(f"\n=========================================================================================")
    print(f" {title} (Count: {len(docs)})")
    print(f"=========================================================================================")
    header = f"{'SKU':<10} {'Name':<34} {'Price ($)':<12} {'Stock':<10} {'is_active':<10}"
    print(header)
    print("-" * len(header))
    for d in docs:
        print(f"{d.get('sku', 'N/A'):<10} {d.get('name', 'N/A'):<34} ${d.get('price', 0):<11.2f} {d.get('stock', 0):<10} {str(d.get('is_active', 'N/A')):<10}")


def export_inventory_to_json(col, file_path):
    """Export current collection to JSON."""
    docs = list(col.find({}, {"_id": 0}).sort("sku", 1))
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(docs, indent=2, default=json_util.default))
    print(f"\n[OK] Exported {len(docs)} inventory documents to: {file_path}")


def main():
    banner("Lab 4.2: Implement Upsert and Bulk Operations")
    print("Student: Kasireddy Meghana | USN: 24BTRCL119 | Dept: CSE (AIML), Jain University\n")

    db = get_db("nosql_labs")
    col = reset_collection("nosql_labs", "inventory")

    # Seed the initial products
    col.insert_many(INITIAL_INVENTORY)
    print(f"[OK] Seeded initial {len(INITIAL_INVENTORY)} products into 'inventory' collection.")
    
    current_docs = list(col.find({}, {"_id": 0}).sort("sku", 1))
    display_inventory_table("Initial Inventory State (Products PROD-A through PROD-E)", current_docs)

    # -------------------------------------------------------------------------
    # Step 1: Demonstrate Upsert Functionality
    # -------------------------------------------------------------------------
    banner("Instruction 1: Upsert Function (update_one with upsert=True)", char="-")

    print("Case 1: Updating Price for an Existing SKU ('PROD-A')...")
    res1 = upsert_product_price(col, "PROD-A", 34.99)
    doc_a = col.find_one({"sku": "PROD-A"}, {"_id": 0})
    print(f"    -> Verification: Matched={res1.matched_count}, Modified={res1.modified_count}, UpsertedId={res1.upserted_id}")
    print(f"    -> Stored Document: {doc_a}\n")

    print("Case 2: Upserting a Brand New SKU ('PROD-F')...")
    res2 = upsert_product_price(
        col,
        "PROD-F",
        59.99,
        default_values={
            "name": "Multi-Device Bluetooth Stylus",
            "stock": 20,
            "is_active": True,
            "category": "Peripherals",
            "tags": ["stylus", "wireless"]
        }
    )
    doc_f = col.find_one({"sku": "PROD-F"}, {"_id": 0})
    print(f"    -> Verification: Matched={res2.matched_count}, Modified={res2.modified_count}, UpsertedId={res2.upserted_id}")
    print(f"    -> Stored Document: {doc_f}")

    # -------------------------------------------------------------------------
    # Step 2: Bulk Write Operation with 5 Simultaneous Updates
    # -------------------------------------------------------------------------
    banner("Instruction 2: Bulk Write Operation (5 Simultaneous Updates)", char="-")
    print("Requirement:")
    print("  - Increase stock by 10 for products A, B, and C (PROD-A, PROD-B, PROD-C)")
    print("  - Set is_active to false for products D and E (PROD-D, PROD-E)")
    print("  - Use UpdateOne operations and verify bulk write result object\n")

    bulk_operations = [
        UpdateOne({"sku": "PROD-A"}, {"$inc": {"stock": 10}}),
        UpdateOne({"sku": "PROD-B"}, {"$inc": {"stock": 10}}),
        UpdateOne({"sku": "PROD-C"}, {"$inc": {"stock": 10}}),
        UpdateOne({"sku": "PROD-D"}, {"$set": {"is_active": False}}),
        UpdateOne({"sku": "PROD-E"}, {"$set": {"is_active": False}}),
    ]

    print("[*] Executing col.bulk_write(bulk_operations, ordered=True)...")
    bulk_result = col.bulk_write(bulk_operations, ordered=True)

    print("\n--- Verifying BulkWriteResult Object ---")
    print(f"  • Acknowledged:      {bulk_result.acknowledged}")
    print(f"  • Matched Count:     {bulk_result.matched_count}  (Expected: 5)")
    print(f"  • Modified Count:    {bulk_result.modified_count} (Expected: 5)")
    print(f"  • Upserted Count:    {bulk_result.upserted_count} (Expected: 0)")
    print(f"  • Upserted IDs:      {bulk_result.upserted_ids}")
    print(f"  • Inserted Count:    {bulk_result.inserted_count}")
    print(f"  • Deleted Count:     {bulk_result.deleted_count}")

    # Step 2b: Additional verification with an upsert in bulk write
    print("\n--- Demonstrating Upsert inside Bulk Write ---")
    bulk_ops_with_upsert = [
        UpdateOne({"sku": "PROD-B"}, {"$inc": {"stock": 5}}),
        UpdateOne(
            {"sku": "PROD-G"},
            {
                "$set": {"price": 19.99},
                "$setOnInsert": {"sku": "PROD-G", "name": "Magnetic Cable Clips", "stock": 50, "is_active": True}
            },
            upsert=True
        )
    ]
    bulk_res_upsert = col.bulk_write(bulk_ops_with_upsert)
    print(f"  • Matched Count:     {bulk_res_upsert.matched_count}")
    print(f"  • Modified Count:    {bulk_res_upsert.modified_count}")
    print(f"  • Upserted Count:    {bulk_res_upsert.upserted_count}  (Expected: 1 for PROD-G)")
    print(f"  • Upserted IDs:      {bulk_res_upsert.upserted_ids}")

    # Final Inventory State
    final_docs = list(col.find({}, {"_id": 0}).sort("sku", 1))
    display_inventory_table("Final Inventory State After Upserts & Bulk Write", final_docs)

    # Export to JSON
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory_activity_4_2.json")
    export_inventory_to_json(col, json_path)

    banner("Lab 4.2 Completed Successfully")


if __name__ == "__main__":
    main()
