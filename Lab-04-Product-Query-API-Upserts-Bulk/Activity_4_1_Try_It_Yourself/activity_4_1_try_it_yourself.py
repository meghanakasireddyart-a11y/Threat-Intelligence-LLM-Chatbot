"""
Lab 4.1 Try It Yourself: Text Search Capability using MongoDB $regex Operator
Course: NoSQL Databases (MongoDB)
Author: Kasireddy Meghana (USN: 24BTRCL119)
Branch: CSE (AIML), Section B - Jain University

Objective:
Implement a case-insensitive text search engine for the products collection using
the MongoDB $regex operator, demonstrating substring matching, prefix anchoring,
multi-criteria search, and exporting search results to JSON.
"""

import os
import sys
import json
from bson import json_util

# Add parent directory for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.connection import get_db, banner


def search_by_name_regex(col, search_term, case_insensitive=True, sort_field="name"):
    """
    Search products whose 'name' contains the search string using $regex.
    Uses $options: 'i' for case-insensitive matching.
    """
    options = "i" if case_insensitive else ""
    query = {
        "name": {
            "$regex": search_term,
            "$options": options
        }
    }
    cursor = col.find(query, {"_id": 0}).sort(sort_field, 1)
    results = list(cursor)
    return results, query


def search_multi_field_regex(col, search_term, fields=None):
    """Search across multiple fields (e.g. name, category, brand) using $or with $regex."""
    fields = fields or ["name", "category"]
    or_clauses = [{field: {"$regex": search_term, "$options": "i"}} for field in fields]
    query = {"$or": or_clauses}
    cursor = col.find(query, {"_id": 0}).sort("name", 1)
    return list(cursor), query


def search_regex_with_filter(col, search_term, max_price=None, in_stock_only=True):
    """Combine $regex text search with comparison and boolean operators."""
    conditions = [
        {"name": {"$regex": search_term, "$options": "i"}}
    ]
    if in_stock_only:
        conditions.append({"stock": {"$gt": 0}})
    if max_price is not None:
        conditions.append({"price": {"$lte": max_price}})
        
    query = {"$and": conditions}
    cursor = col.find(query, {"_id": 0}).sort("price", 1)
    return list(cursor), query


def print_search_results(test_title, search_pattern, query_used, results):
    """Display tabular search results and MongoDB query executed."""
    print(f"\n{'='*90}")
    print(f" {test_title}")
    print(f"{'='*90}")
    print(f" Pattern Searched: '{search_pattern}'")
    print(f" MongoDB Filter:   {json.dumps(query_used, default=json_util.default)}")
    print(f" Matches Found:    {len(results)}")
    print(f"{'-'*90}")
    if not results:
        print("  (No products matched the given criteria)")
        return
        
    header = f"{'SKU':<10} {'Name':<36} {'Category':<14} {'Price ($)':<10} {'Stock':<8} {'Tags'}"
    print(header)
    print("-" * len(header))
    for p in results:
        tags_str = ", ".join(p.get("tags", []))
        print(f"{p.get('sku', 'N/A'):<10} {p.get('name', 'N/A'):<36} {p.get('category', 'N/A'):<14} ${p.get('price', 0):<9.2f} {p.get('stock', 0):<8} [{tags_str}]")


def export_results_to_json(data, file_path):
    """Export formatted search demonstration results to JSON."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2, default=json_util.default))
    print(f"\n[OK] Exported search results to: {file_path}")


def main():
    banner("Activity 4.1 Try It Yourself: Text Search with $regex")
    print("Student: Kasireddy Meghana | USN: 24BTRCL119 | Dept: CSE (AIML), Jain University\n")

    db = get_db("nosql_labs")
    col = db["products"]

    # Ensure collection exists; if not populated, run Activity 4.1 seed
    if col.count_documents({}) == 0:
        print("[!] Products collection empty. Re-seeding via Activity 4.1...")
        from Activity_4_1.activity_4_1 import setup_collection_with_validation, SAMPLE_PRODUCTS
        col = setup_collection_with_validation(db, "products")
        col.insert_many(SAMPLE_PRODUCTS)

    print(f"[OK] Connected to 'products' collection. Document count: {col.count_documents({})}")

    demonstration_records = {}

    # -------------------------------------------------------------------------
    # Test 1: Substring Case-Insensitive Search - "wireless"
    # -------------------------------------------------------------------------
    results_1, q1 = search_by_name_regex(col, "wireless", case_insensitive=True)
    print_search_results(
        "Search Test 1: Substring Search for 'wireless' (Case-Insensitive)",
        "wireless",
        q1,
        results_1
    )
    demonstration_records["test_1_wireless_substring"] = {
        "pattern": "wireless",
        "query": q1,
        "count": len(results_1),
        "results": results_1
    }

    # -------------------------------------------------------------------------
    # Test 2: Mixed Case / Acronym Search - "usb" (matches "USB-C")
    # -------------------------------------------------------------------------
    results_2, q2 = search_by_name_regex(col, "usb", case_insensitive=True)
    print_search_results(
        "Search Test 2: Lowercase Search 'usb' matching uppercase 'USB-C'",
        "usb",
        q2,
        results_2
    )
    demonstration_records["test_2_case_insensitivity_usb"] = {
        "pattern": "usb",
        "query": q2,
        "count": len(results_2),
        "results": results_2
    }

    # -------------------------------------------------------------------------
    # Test 3: Anchor Prefix Search - "^Ultra" (Starts with "Ultra")
    # -------------------------------------------------------------------------
    results_3, q3 = search_by_name_regex(col, r"^Ultra", case_insensitive=True)
    print_search_results(
        "Search Test 3: Prefix Anchored Search '^Ultra' (Name must start with Ultra)",
        "^Ultra",
        q3,
        results_3
    )
    demonstration_records["test_3_prefix_anchor"] = {
        "pattern": "^Ultra",
        "query": q3,
        "count": len(results_3),
        "results": results_3
    }

    # -------------------------------------------------------------------------
    # Test 4: Anchor Suffix Search - "Watch$" or "Pad$" (Ends with pattern)
    # -------------------------------------------------------------------------
    results_4, q4 = search_by_name_regex(col, r"(Watch|Mousepad)$", case_insensitive=True)
    print_search_results(
        "Search Test 4: Suffix Anchored Search '(Watch|Mousepad)$' (Ends with pattern)",
        "(Watch|Mousepad)$",
        q4,
        results_4
    )
    demonstration_records["test_4_suffix_anchor"] = {
        "pattern": "(Watch|Mousepad)$",
        "query": q4,
        "count": len(results_4),
        "results": results_4
    }

    # -------------------------------------------------------------------------
    # Test 5: Compound Query - Name contains "Wireless" AND Price <= $50 AND In-Stock
    # -------------------------------------------------------------------------
    results_5, q5 = search_regex_with_filter(col, "wireless", max_price=50.0, in_stock_only=True)
    print_search_results(
        "Search Test 5: Compound Search - 'wireless' AND Price <= $50 AND In Stock",
        "wireless",
        q5,
        results_5
    )
    demonstration_records["test_5_compound_search"] = {
        "pattern": "wireless",
        "query": q5,
        "count": len(results_5),
        "results": results_5
    }

    # -------------------------------------------------------------------------
    # Test 6: Multi-Field Search - Matches in 'name' OR 'category'
    # -------------------------------------------------------------------------
    results_6, q6 = search_multi_field_regex(col, "gaming", fields=["name", "category"])
    print_search_results(
        "Search Test 6: Multi-Field Search for 'gaming' across Name OR Category",
        "gaming",
        q6,
        results_6
    )
    demonstration_records["test_6_multi_field"] = {
        "pattern": "gaming",
        "query": q6,
        "count": len(results_6),
        "results": results_6
    }

    # Export to JSON
    out_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), "products_search_results.json")
    export_results_to_json(demonstration_records, out_json)

    banner("Activity 4.1 Try It Yourself Completed Successfully")


if __name__ == "__main__":
    main()
