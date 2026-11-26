"""
Lab 4.1: Build a Product Query API
Course: NoSQL Databases (MongoDB)
Author: Kasireddy Meghana (USN: 24BTRCL119)
Branch: CSE (AIML), Section B - Jain University

Covers:
1. Schema Validation (name: string, price: > 0, stock: >= 0 int, tags: [string])
2. At least 10 varied products
3. Comparison operators ($gte, $lte, $eq)
4. Logical operators ($or, $and)
5. Array operators ($all, $size)
6. Pagination function sorted by name
7. Export to JSON
"""

import os
import sys
import json
from bson import json_util
from pymongo.errors import WriteError, OperationFailure

# Add parent directory for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.connection import get_db, banner


# Product Catalog (12 diverse products meeting varied test criteria)
SAMPLE_PRODUCTS = [
    {
        "sku": "AUD-001",
        "name": "Wireless Noise-Canceling Earbuds",
        "category": "Audio",
        "price": 49.99,
        "stock": 45,
        "tags": ["electronics", "wireless", "audio", "premium"],
        "rating": 4.7,
        "is_active": True
    },
    {
        "sku": "AUD-002",
        "name": "Bluetooth Pocket Speaker",
        "category": "Audio",
        "price": 29.99,
        "stock": 0,
        "tags": ["electronics", "wireless"],
        "rating": 4.1,
        "is_active": False
    },
    {
        "sku": "KBD-001",
        "name": "Mechanical RGB Gaming Keyboard",
        "category": "Peripherals",
        "price": 129.99,
        "stock": 18,
        "tags": ["electronics", "gaming", "premium"],
        "rating": 4.8,
        "is_active": True
    },
    {
        "sku": "MOU-001",
        "name": "Ergonomic Optical Wireless Mouse",
        "category": "Peripherals",
        "price": 34.50,
        "stock": 60,
        "tags": ["electronics", "wireless"],
        "rating": 4.4,
        "is_active": True
    },
    {
        "sku": "LAP-001",
        "name": "UltraSlim Carbon Laptop 14-inch",
        "category": "Computers",
        "price": 1199.00,
        "stock": 12,
        "tags": ["electronics", "wireless", "premium"],
        "rating": 4.9,
        "is_active": True
    },
    {
        "sku": "ACC-001",
        "name": "Braided USB-C Fast Charging Cable",
        "category": "Accessories",
        "price": 14.99,
        "stock": 120,
        "tags": ["accessories", "cables"],
        "rating": 4.5,
        "is_active": True
    },
    {
        "sku": "ACC-002",
        "name": "Aluminum Multiport USB-C Hub",
        "category": "Accessories",
        "price": 45.00,
        "stock": 0,
        "tags": ["electronics", "accessories"],
        "rating": 4.2,
        "is_active": False
    },
    {
        "sku": "WRB-001",
        "name": "ProTrack GPS Smartwatch",
        "category": "Wearables",
        "price": 249.99,
        "stock": 25,
        "tags": ["electronics", "wireless", "fitness", "premium"],
        "rating": 4.6,
        "is_active": True
    },
    {
        "sku": "WRB-002",
        "name": "Basic Step-Tracker Fitness Band",
        "category": "Wearables",
        "price": 24.99,
        "stock": 80,
        "tags": ["fitness", "wearable"],
        "rating": 3.9,
        "is_active": True
    },
    {
        "sku": "MON-001",
        "name": "Curved 34-inch Ultrawide Monitor",
        "category": "Displays",
        "price": 549.99,
        "stock": 0,
        "tags": ["electronics", "displays", "premium"],
        "rating": 4.8,
        "is_active": False
    },
    {
        "sku": "GAM-001",
        "name": "Wireless Gamepad Controller",
        "category": "Gaming",
        "price": 39.99,
        "stock": 55,
        "tags": ["electronics", "wireless"],
        "rating": 4.3,
        "is_active": True
    },
    {
        "sku": "ACC-003",
        "name": "Memory Foam Ergonomic Mousepad",
        "category": "Accessories",
        "price": 19.99,
        "stock": 90,
        "tags": ["accessories", "ergonomic"],
        "rating": 4.2,
        "is_active": True
    }
]


def setup_collection_with_validation(db, col_name="products"):
    """
    Instruction 1: Create a products collection with JSON schema validation.
    Enforces:
    - name: string (required)
    - price: positive number (> 0) (required)
    - stock: non-negative integer (>= 0) (required)
    - tags: array of strings (required)
    """
    if col_name in db.list_collection_names():
        db.drop_collection(col_name)
        print(f"[OK] Cleaned up existing collection: {col_name}")

    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["name", "price", "stock", "tags"],
            "properties": {
                "sku": {
                    "bsonType": "string",
                    "description": "Product unique SKU identifier"
                },
                "name": {
                    "bsonType": "string",
                    "description": "Product title - must be a string"
                },
                "price": {
                    "bsonType": ["double", "int", "decimal"],
                    "minimum": 0.01,
                    "description": "Price must be a positive number greater than 0"
                },
                "stock": {
                    "bsonType": "int",
                    "minimum": 0,
                    "description": "Stock must be a non-negative integer >= 0"
                },
                "tags": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "string"
                    },
                    "description": "Tags must be an array of strings"
                },
                "category": {
                    "bsonType": "string"
                },
                "rating": {
                    "bsonType": ["double", "int"]
                },
                "is_active": {
                    "bsonType": "bool"
                }
            }
        }
    }

    col = db.create_collection(
        col_name,
        validator=validator,
        validationLevel="strict",
        validationAction="error"
    )
    print(f"[OK] Collection '{col_name}' created with schema validation rules.")
    return col


def test_validation_enforcement(col):
    """Demonstrate that documents violating schema validation are strictly rejected."""
    print("\n--- Verifying Schema Validation Enforcement ---")
    
    # Negative Price violation
    invalid_doc_1 = {
        "sku": "BAD-001",
        "name": "Invalid Price Item",
        "price": -10.00,  # Violates minimum: 0.01
        "stock": 5,
        "tags": ["invalid"]
    }
    try:
        col.insert_one(invalid_doc_1)
        print("  [ERROR] Validation failed to catch negative price!")
    except (WriteError, OperationFailure) as e:
        print("  [PASS] Correctly rejected document with negative price (-10.00)")

    # Negative Stock violation
    invalid_doc_2 = {
        "sku": "BAD-002",
        "name": "Invalid Stock Item",
        "price": 25.00,
        "stock": -5,  # Violates minimum: 0
        "tags": ["invalid"]
    }
    try:
        col.insert_one(invalid_doc_2)
        print("  [ERROR] Validation failed to catch negative stock!")
    except (WriteError, OperationFailure) as e:
        print("  [PASS] Correctly rejected document with negative stock (-5)")

    # Missing required tags field
    invalid_doc_3 = {
        "sku": "BAD-003",
        "name": "Missing Tags Item",
        "price": 30.00,
        "stock": 10
        # tags omitted
    }
    try:
        col.insert_one(invalid_doc_3)
        print("  [ERROR] Validation failed to catch missing tags!")
    except (WriteError, OperationFailure) as e:
        print("  [PASS] Correctly rejected document missing required 'tags' field\n")


def paginate_products(col, query_filter=None, sort_field="name", sort_dir=1, page=1, page_size=3):
    """
    Instruction 5: Paginated product query function.
    Returns: (list_of_documents, total_count, total_pages)
    """
    query_filter = query_filter or {}
    skip = (page - 1) * page_size
    
    cursor = col.find(
        query_filter,
        {"_id": 0, "sku": 1, "name": 1, "category": 1, "price": 1, "stock": 1, "tags": 1}
    )
    cursor = cursor.sort(sort_field, sort_dir).skip(skip).limit(page_size)
    
    results = list(cursor)
    total_count = col.count_documents(query_filter)
    total_pages = (total_count + page_size - 1) // page_size
    
    return results, total_count, total_pages


def print_product_table(title, products):
    """Format and display product query output clearly."""
    print(f"\n=========================================================================================")
    print(f" {title} (Count: {len(products)})")
    print(f"=========================================================================================")
    header = f"{'SKU':<10} {'Name':<36} {'Category':<14} {'Price ($)':<10} {'Stock':<8} {'Tags'}"
    print(header)
    print("-" * len(header))
    for p in products:
        tags_str = ", ".join(p.get("tags", []))
        print(f"{p.get('sku', 'N/A'):<10} {p.get('name', 'N/A'):<36} {p.get('category', 'N/A'):<14} ${p.get('price', 0):<9.2f} {p.get('stock', 0):<8} [{tags_str}]")


def export_collection_to_json(col, file_path):
    """Export all collection documents to JSON formatted file."""
    docs = list(col.find({}, {"_id": 0}).sort("sku", 1))
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(docs, indent=2, default=json_util.default))
    print(f"\n[OK] Successfully exported {len(docs)} products to: {file_path}")


def main():
    banner("Lab 4.1: Product Query API - MongoDB Query Operators")
    print("Student: Kasireddy Meghana | USN: 24BTRCL119 | Dept: CSE (AIML), Jain University\n")

    db = get_db("nosql_labs")

    # Step 1: Create collection with schema validation
    col = setup_collection_with_validation(db, "products")

    # Verify schema validation with invalid records
    test_validation_enforcement(col)

    # Insert 12 sample products
    insert_res = col.insert_many(SAMPLE_PRODUCTS)
    print(f"[OK] Inserted {len(insert_res.inserted_ids)} valid product documents into 'products' collection.")

    # -------------------------------------------------------------------------
    # Step 2: Comparison Operators
    # -------------------------------------------------------------------------
    banner("Comparison Operators", char="-")

    # Query 2a: Products with price between $20 and $50
    q_price_20_50 = {"price": {"$gte": 20.0, "$lte": 50.0}}
    res_price = list(col.find(q_price_20_50, {"_id": 0}))
    print_product_table("Comparison Query 1: Price Between $20 and $50 ($gte: 20, $lte: 50)", res_price)

    # Query 2b: Products with stock equal to 0 (out of stock)
    q_stock_zero = {"stock": {"$eq": 0}}
    res_stock_zero = list(col.find(q_stock_zero, {"_id": 0}))
    print_product_table("Comparison Query 2: Products Out of Stock ($eq: 0)", res_stock_zero)

    # -------------------------------------------------------------------------
    # Step 3: Logical Operators
    # -------------------------------------------------------------------------
    banner("Logical Operators", char="-")

    # Query 3a: Out of stock OR priced above $100
    q_out_or_expensive = {
        "$or": [
            {"stock": {"$eq": 0}},
            {"price": {"$gt": 100.0}}
        ]
    }
    res_or = list(col.find(q_out_or_expensive, {"_id": 0}))
    print_product_table("Logical Query 1: Out of Stock ($eq: 0) OR Price > $100 ($or)", res_or)

    # Query 3b: In stock AND tagged as 'premium'
    q_instock_premium = {
        "$and": [
            {"stock": {"$gt": 0}},
            {"tags": "premium"}
        ]
    }
    res_and = list(col.find(q_instock_premium, {"_id": 0}))
    print_product_table("Logical Query 2: In Stock (stock > 0) AND Tagged 'premium' ($and)", res_and)

    # -------------------------------------------------------------------------
    # Step 4: Array Operators
    # -------------------------------------------------------------------------
    banner("Array Operators", char="-")

    # Query 4a: Products having BOTH 'electronics' AND 'wireless' in tags
    q_both_tags = {"tags": {"$all": ["electronics", "wireless"]}}
    res_both_tags = list(col.find(q_both_tags, {"_id": 0}))
    print_product_table("Array Query 1: Tags Contain BOTH 'electronics' AND 'wireless' ($all)", res_both_tags)

    # Query 4b: Products with exactly 2 tags
    q_exact_2_tags = {"tags": {"$size": 2}}
    res_exact_2 = list(col.find(q_exact_2_tags, {"_id": 0}))
    print_product_table("Array Query 2: Products With Exactly 2 Tags ($size: 2)", res_exact_2)

    # -------------------------------------------------------------------------
    # Step 5: Pagination
    # -------------------------------------------------------------------------
    banner("Pagination Demonstration (Sorted by Name)", char="-")
    page_size = 3
    total_docs = col.count_documents({})
    total_pages = (total_docs + page_size - 1) // page_size
    print(f"Total Products: {total_docs} | Page Size: {page_size} | Total Pages: {total_pages}\n")

    for page_num in range(1, total_pages + 1):
        page_items, total, pages = paginate_products(col, {}, sort_field="name", sort_dir=1, page=page_num, page_size=page_size)
        print(f"--- Page {page_num} of {pages} (Showing items {(page_num-1)*page_size + 1} to {(page_num-1)*page_size + len(page_items)} of {total}) ---")
        for idx, item in enumerate(page_items, start=1):
            print(f"  {idx}. {item['name']:<36} | ${item['price']:<7.2f} | Stock: {item['stock']:<3} | SKU: {item['sku']}")
        print()

    # Step 6: Export to JSON
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "products_activity_4_1.json")
    export_collection_to_json(col, json_path)

    banner("Lab 4.1 Completed Successfully")


if __name__ == "__main__":
    main()
