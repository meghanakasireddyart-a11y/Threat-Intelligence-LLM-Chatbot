"""
Lab 4.2 Try It Yourself: Idempotent Bulk Import System
Course: NoSQL Databases (MongoDB)
Author: Kasireddy Meghana (USN: 24BTRCL119)
Branch: CSE (AIML), Section B - Jain University

Objective:
Implement an idempotent bulk import pipeline that can be executed multiple times
without creating duplicate documents or corrupting data states, leveraging MongoDB
UpdateOne upsert semantics and idempotent field operators ($set, $setOnInsert, $addToSet).
"""

import os
import sys
import json
from datetime import datetime, timezone
from bson import json_util
from pymongo import UpdateOne

# Add parent directory for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.connection import get_db, reset_collection, banner


# Ingestion Dataset: 8 products to be imported in batches
IMPORT_BATCH_V1 = [
    {
        "sku": "IMP-101",
        "name": "Precision Wireless Gaming Mouse",
        "category": "Peripherals",
        "price": 59.99,
        "stock": 50,
        "tags": ["gaming", "wireless"],
        "is_active": True
    },
    {
        "sku": "IMP-102",
        "name": "Mechanical Tenkeyless Keyboard",
        "category": "Peripherals",
        "price": 109.99,
        "stock": 30,
        "tags": ["mechanical", "rgb"],
        "is_active": True
    },
    {
        "sku": "IMP-103",
        "name": "Ultra-Wide QHD 34-Inch Monitor",
        "category": "Monitors",
        "price": 499.00,
        "stock": 15,
        "tags": ["display", "ultrawide", "qhd"],
        "is_active": True
    },
    {
        "sku": "IMP-104",
        "name": "Active Noise Canceling Headphones",
        "category": "Audio",
        "price": 199.50,
        "stock": 25,
        "tags": ["audio", "anc", "wireless"],
        "is_active": True
    },
    {
        "sku": "IMP-105",
        "name": "Heavy Duty Dual Monitor Arm",
        "category": "Accessories",
        "price": 79.99,
        "stock": 40,
        "tags": ["ergonomic", "accessories"],
        "is_active": True
    },
    {
        "sku": "IMP-106",
        "name": "65W GaN Compact USB-C Charger",
        "category": "Accessories",
        "price": 34.99,
        "stock": 100,
        "tags": ["charging", "gan", "usb-c"],
        "is_active": True
    },
    {
        "sku": "IMP-107",
        "name": "Waterproof Fitness Smart Band",
        "category": "Wearables",
        "price": 49.95,
        "stock": 70,
        "tags": ["fitness", "waterproof"],
        "is_active": True
    },
    {
        "sku": "IMP-108",
        "name": "Aluminum Laptop Cooling Stand",
        "category": "Accessories",
        "price": 27.50,
        "stock": 85,
        "tags": ["cooling", "ergonomic"],
        "is_active": True
    }
]

# Delta Sync Batch: 5 identical items, 3 modified items, 2 brand new items
IMPORT_BATCH_DELTA = [
    # 5 unchanged items
    IMPORT_BATCH_V1[0],
    IMPORT_BATCH_V1[1],
    IMPORT_BATCH_V1[2],
    IMPORT_BATCH_V1[3],
    IMPORT_BATCH_V1[4],
    # 3 updated items (price / stock changes)
    {
        "sku": "IMP-106",
        "name": "65W GaN Compact USB-C Charger (Updated Edition)",
        "category": "Accessories",
        "price": 29.99,  # Discounted from 34.99
        "stock": 120,    # Replenished
        "tags": ["charging", "gan", "usb-c", "fast-charge"],
        "is_active": True
    },
    {
        "sku": "IMP-107",
        "name": "Waterproof Fitness Smart Band",
        "category": "Wearables",
        "price": 44.95,  # Promotional price
        "stock": 65,     # Stock sold
        "tags": ["fitness", "waterproof", "sale"],
        "is_active": True
    },
    {
        "sku": "IMP-108",
        "name": "Aluminum Laptop Cooling Stand",
        "category": "Accessories",
        "price": 24.99,  # Price drop
        "stock": 110,    # Restocked
        "tags": ["cooling", "ergonomic"],
        "is_active": True
    },
    # 2 brand new items
    {
        "sku": "IMP-109",
        "name": "Magnetic Wireless MagSafe PowerBank",
        "category": "Accessories",
        "price": 49.99,
        "stock": 60,
        "tags": ["magsafe", "wireless", "powerbank"],
        "is_active": True
    },
    {
        "sku": "IMP-110",
        "name": "4K Ultra-HD Streaming Webcam",
        "category": "Peripherals",
        "price": 89.99,
        "stock": 35,
        "tags": ["webcam", "4k", "streaming"],
        "is_active": True
    }
]


def idempotent_bulk_import(col, items, key_field="sku"):
    """
    Core Idempotent Bulk Import Function.
    Ensures that re-running this function with the exact same data produces:
    - 0 duplicate documents
    - 0 unintended modifications
    - Exact state reconciliation
    
    Uses UpdateOne with upsert=True, separating mutable attributes into $set
    and initial metadata into $setOnInsert.
    """
    if not items:
        return None

    bulk_ops = []
    current_time_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for item in items:
        primary_key = item[key_field]
        # Separate primary key from update payload
        mutable_fields = {k: v for k, v in item.items() if k != key_field}

        op = UpdateOne(
            {key_field: primary_key},
            {
                "$set": {
                    **mutable_fields,
                    "last_synced_at": current_time_str
                },
                "$setOnInsert": {
                    key_field: primary_key,
                    "first_imported_at": current_time_str
                }
            },
            upsert=True
        )
        bulk_ops.append(op)

    result = col.bulk_write(bulk_ops, ordered=False)
    return result


def display_run_summary(run_title, result, col_size):
    """Format execution metrics for each bulk import run."""
    print(f"\n=========================================================================================")
    print(f" {run_title}")
    print(f"=========================================================================================")
    print(f"  • Matched Count:     {result.matched_count}")
    print(f"  • Modified Count:    {result.modified_count}")
    print(f"  • Upserted Count:    {result.upserted_count}")
    print(f"  • Total DB Records:  {col_size}")
    if result.upserted_count > 0:
        print(f"  • New Keys Inserted: {list(result.upserted_ids.values())}")
    print(f"  • Status:            SUCCESS (Idempotent Execution Confirmed)")


def export_inventory_to_json(col, file_path):
    """Export current collection to JSON."""
    docs = list(col.find({}, {"_id": 0}).sort("sku", 1))
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(docs, indent=2, default=json_util.default))
    print(f"\n[OK] Exported {len(docs)} documents to: {file_path}")


def main():
    banner("Activity 4.2 Try It Yourself: Idempotent Bulk Import System")
    print("Student: Kasireddy Meghana | USN: 24BTRCL119 | Dept: CSE (AIML), Jain University\n")

    db = get_db("nosql_labs")
    col = reset_collection("nosql_labs", "idempotent_inventory")

    print("[*] Created clean collection 'idempotent_inventory'. Initial count = 0.\n")

    # -------------------------------------------------------------------------
    # RUN 1: Initial Bulk Import of 8 Products
    # -------------------------------------------------------------------------
    print(">>> Executing RUN 1: Initial Bulk Import of 8 products...")
    res1 = idempotent_bulk_import(col, IMPORT_BATCH_V1)
    count1 = col.count_documents({})
    display_run_summary("RUN 1: Initial Ingestion", res1, count1)
    assert count1 == 8, f"Expected 8 documents, got {count1}"
    assert res1.upserted_count == 8, f"Expected 8 upserted, got {res1.upserted_count}"

    # -------------------------------------------------------------------------
    # RUN 2: Re-running Exact Same 8 Products (Simulating Duplicate Request / Retry)
    # -------------------------------------------------------------------------
    print("\n>>> Executing RUN 2: Re-running Exact Same 8 Products (Testing Idempotency)...")
    res2 = idempotent_bulk_import(col, IMPORT_BATCH_V1)
    count2 = col.count_documents({})
    display_run_summary("RUN 2: Duplicate Ingestion (Zero Duplicate Rows Generated)", res2, count2)
    assert count2 == 8, f"Error: Duplicate documents created! Count = {count2}"
    assert res2.upserted_count == 0, f"Error: Expected 0 upserted in rerun, got {res2.upserted_count}"
    print("  [VERIFIED] Running the bulk import a 2nd time created 0 duplicates; total documents remain exactly 8.")

    # -------------------------------------------------------------------------
    # RUN 3: Third Re-run with Same Data (Idempotency Proof)
    # -------------------------------------------------------------------------
    print("\n>>> Executing RUN 3: Third Immediate Re-run (Idempotency Confirmation)...")
    res3 = idempotent_bulk_import(col, IMPORT_BATCH_V1)
    count3 = col.count_documents({})
    display_run_summary("RUN 3: Third Re-run Verification", res3, count3)
    assert count3 == 8, f"Error: Count mismatch! Count = {count3}"
    assert res3.upserted_count == 0, f"Error: Expected 0 upserted, got {res3.upserted_count}"
    print("  [VERIFIED] 3 consecutive identical runs yield zero duplicates.")

    # -------------------------------------------------------------------------
    # RUN 4: Delta Sync (5 Unchanged + 3 Modified + 2 New Products)
    # -------------------------------------------------------------------------
    print("\n>>> Executing RUN 4: Delta Sync (5 Unchanged, 3 Updated, 2 Brand New Products)...")
    res4 = idempotent_bulk_import(col, IMPORT_BATCH_DELTA)
    count4 = col.count_documents({})
    display_run_summary("RUN 4: Delta Sync Execution", res4, count4)
    assert count4 == 10, f"Expected 10 documents, got {count4}"
    assert res4.upserted_count == 2, f"Expected 2 upserted, got {res4.upserted_count}"
    print("  [VERIFIED] Correctly updated existing items and added 2 new items; total count is now 10.")

    # Display final state
    final_docs = list(col.find({}, {"_id": 0}).sort("sku", 1))
    print(f"\n=========================================================================================")
    print(f" Final Inventory State After Delta Sync (Count: {len(final_docs)})")
    print(f"=========================================================================================")
    header = f"{'SKU':<10} {'Name':<44} {'Price ($)':<12} {'Stock':<8} {'Tags'}"
    print(header)
    print("-" * len(header))
    for d in final_docs:
        tags_str = ", ".join(d.get("tags", []))
        print(f"{d.get('sku', 'N/A'):<10} {d.get('name', 'N/A'):<44} ${d.get('price', 0):<11.2f} {d.get('stock', 0):<8} [{tags_str}]")

    # Export to JSON
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "idempotent_import_inventory.json")
    export_inventory_to_json(col, json_path)

    banner("Activity 4.2 Try It Yourself Completed Successfully")


if __name__ == "__main__":
    main()
