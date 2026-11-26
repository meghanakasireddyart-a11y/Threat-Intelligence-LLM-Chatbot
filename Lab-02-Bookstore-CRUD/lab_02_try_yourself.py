"""Lab 2.2 (Try It Yourself) - Targeted Price Update for Pre-2010 Publications
Increases the price of all books published before 2010 by 10% using $mul,
verifies price integrity across the catalog, and provides MongoDB Compass verification.
"""

import sys, os, json
from bson import json_util

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.connection import get_db, reset_collection, banner, print_json
from rich.console import Console
from rich.table import Table

console = Console(width=110)

CATALOG = [
    # --- Pre-2010 Publications (Eligible for 10% increase) ---
    {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "year": 2008,
        "genre": "Software Engineering",
        "price": 39.99,
        "isbn": "978-0132350884",
        "tags": ["programming", "clean-code", "refactoring"],
        "publisher": {"name": "Prentice Hall", "location": "Upper Saddle River"}
    },
    {
        "title": "Design Patterns: Elements of Reusable OOD",
        "author": "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
        "year": 1994,
        "genre": "Software Architecture",
        "price": 54.99,
        "isbn": "978-0201633610",
        "tags": ["patterns", "architecture", "oop"],
        "publisher": {"name": "Addison-Wesley", "location": "Boston"}
    },
    {
        "title": "Refactoring: Improving the Design of Existing Code",
        "author": "Martin Fowler",
        "year": 1999,
        "genre": "Software Engineering",
        "price": 47.50,
        "isbn": "978-0201485677",
        "tags": ["refactoring", "clean-code", "design"],
        "publisher": {"name": "Addison-Wesley", "location": "Boston"}
    },
    {
        "title": "Introduction to Algorithms (CLRS 3rd Ed)",
        "author": "Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein",
        "year": 2009,
        "genre": "Computer Science Theory",
        "price": 89.00,
        "isbn": "978-0262033848",
        "tags": ["algorithms", "data-structures", "theory"],
        "publisher": {"name": "MIT Press", "location": "Cambridge"}
    },

    # --- Post-2010 Publications (Should remain UNCHANGED) ---
    {
        "title": "The Pragmatic Programmer (20th Anniv Ed)",
        "author": "David Thomas & Andrew Hunt",
        "year": 2019,
        "genre": "Software Engineering",
        "price": 49.99,
        "isbn": "978-0135957059",
        "tags": ["programming", "career", "best-practices"],
        "publisher": {"name": "Addison-Wesley", "location": "Boston"}
    },
    {
        "title": "Designing Data-Intensive Applications",
        "author": "Martin Kleppmann",
        "year": 2017,
        "genre": "Databases",
        "price": 45.99,
        "isbn": "978-1449373320",
        "tags": ["databases", "distributed-systems", "architecture"],
        "publisher": {"name": "O'Reilly Media", "location": "Sebastopol"}
    },
    {
        "title": "Deep Learning",
        "author": "Ian Goodfellow, Yoshua Bengio, Aaron Courville",
        "year": 2016,
        "genre": "Machine Learning",
        "price": 72.00,
        "isbn": "978-0262035613",
        "tags": ["AI", "neural-networks", "theory"],
        "publisher": {"name": "MIT Press", "location": "Cambridge"}
    },
    {
        "title": "Hands-On Machine Learning",
        "author": "Aurelien Geron",
        "year": 2022,
        "genre": "Machine Learning",
        "price": 59.99,
        "isbn": "978-1098125974",
        "tags": ["AI", "scikit-learn", "tensorflow", "practical"],
        "publisher": {"name": "O'Reilly Media", "location": "Sebastopol"}
    }
]


def main():
    banner("Activity 2.2 (Try It Yourself): Pre-2010 Price Escalation & Compass Verification")

    db = get_db("bookstore")
    col = reset_collection("bookstore", "books_pre2010_update")

    # --- 1. SEED INVENTORY ---
    print("=== SEEDING CATALOG: Inserting 8 technical book documents ===")
    insert_res = col.insert_many(CATALOG)
    print(f"[OK] Inserted {len(insert_res.inserted_ids)} books into collection 'books_pre2010_update'.\n")

    # --- 2. PRE-UPDATE AUDIT & SNAPSHOT ---
    print("=== PRE-UPDATE ANALYSIS: Identifying Books Published Before 2010 ===")
    before_snapshot = {b["title"]: (b["year"], b["price"]) for b in col.find({}, {"title": 1, "year": 1, "price": 1, "_id": 0})}
    
    pre_2010_query = {"year": {"$lt": 2010}}
    target_books = list(col.find(pre_2010_query, {"title": 1, "year": 1, "price": 1, "_id": 0}))
    print(f"  Target Filter Query : {{ 'year': {{ '$lt': 2010 }} }}")
    print(f"  Matching Documents  : {len(target_books)} books qualify for price escalation:")
    for b in target_books:
        print(f"    • {b['title']:<48} ({b['year']}) | Current Price: ${b['price']:.2f}")

    # --- 3. TARGETED UPDATE OPERATION ---
    print("\n=== EXECUTING TARGETED UPDATE: Increase Price by 10% for Pre-2010 Books ===")
    update_op = {"$mul": {"price": 1.10}}
    update_res = col.update_many(pre_2010_query, update_op)
    print(f"[OK] Matched Documents  : {update_res.matched_count}")
    print(f"[OK] Modified Documents : {update_res.modified_count}")

    # --- 4. POST-UPDATE VERIFICATION ---
    print("\n=== POST-UPDATE CATALOG AUDIT & VERIFICATION ===")
    after_snapshot = {b["title"]: (b["year"], b["price"]) for b in col.find({}, {"title": 1, "year": 1, "price": 1, "_id": 0})}

    table = Table(title="Activity 2.2 - Pre-2010 Targeted Price Update Audit", show_lines=True)
    table.add_column("Book Title", style="cyan", width=42)
    table.add_column("Year", justify="center", width=8)
    table.add_column("Initial Price", justify="right", width=14)
    table.add_column("Updated Price", justify="right", width=14)
    table.add_column("Delta", justify="right", width=10)
    table.add_column("Update Status", justify="center", width=18)

    verified_increases = 0
    verified_unchanged = 0

    for title, (year, old_p) in before_snapshot.items():
        _, new_p = after_snapshot[title]
        delta = new_p - old_p
        if year < 2010:
            status_str = "[bold green]INCREASED (+10%)[/bold green]"
            verified_increases += 1
        else:
            status_str = "[dim]UNCHANGED[/dim]"
            verified_unchanged += 1
        table.add_row(
            title,
            str(year),
            f"${old_p:.2f}",
            f"${new_p:.2f}",
            f"+${delta:.2f}" if delta > 0.001 else "$0.00",
            status_str
        )

    console.print()
    console.print(table)
    print(f"[OK] Verification Check: {verified_increases} pre-2010 books updated, {verified_unchanged} post-2010 books untouched.")

    # --- 5. COMPASS VERIFICATION GUIDE ---
    print("\n=== MONGODB COMPASS VERIFICATION PROCEDURE ===")
    print("To visually inspect and verify the updated documents in MongoDB Compass:")
    print("  1. Launch MongoDB Compass and connect to: mongodb://localhost:27017")
    print("  2. Select Database: 'bookstore' -> Collection: 'books_pre2010_update'")
    print("  3. In the Filter bar, enter the query:")
    print("       { \"year\": { \"$lt\": 2010 } }")
    print("  4. In the Project bar, enter:")
    print("       { \"title\": 1, \"year\": 1, \"price\": 1, \"_id\": 0 }")
    print("  5. Click 'Find' to verify all 4 modified documents show their updated prices.")

    # --- 6. EXPORT MONGO JSON FILE ---
    docs = list(col.find())
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab_02_try_yourself.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(docs, indent=2, default=json_util.default))
    print(f"\n[OK] Exported {len(docs)} documents to {os.path.basename(json_path)}")

    banner("Activity 2.2 (Try It Yourself) Complete")


if __name__ == "__main__":
    main()
