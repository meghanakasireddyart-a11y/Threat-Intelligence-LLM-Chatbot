"""Lab 7.1 - Analyze a Production Schema
Author: Kasireddy Meghana (USN: 24BTRCL119)
Course: NoSQL Databases (MongoDB) - Lab 7

Embed vs reference analysis with $bsonSize operator and unbounded growth modeling.
"""

import sys, os, json
import bson
from bson import json_util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.connection import get_db, reset_collection, banner
from rich.table import Table
from rich.console import Console

console = Console()

BLOG_POSTS = [
    {
        "title": "Getting Started with MongoDB",
        "author": "arjun", "slug": "getting-started-mongodb",
        "tags": ["mongodb", "nosql", "beginner"],
        "comments": [
            {"author": "reader1", "text": "Great intro!", "created": "2024-01-16"},
            {"author": "reader2", "text": "More on aggregation please", "created": "2024-01-17"},
        ]
    },
    {
        "title": "Advanced Aggregation Pipelines",
        "author": "sneha", "slug": "advanced-aggregation",
        "tags": ["mongodb", "aggregation", "intermediate"],
        "comments": [
            {"author": "reader1", "text": "$facet is amazing", "created": "2024-02-01"},
            {"author": "reader3", "text": "Very well explained", "created": "2024-02-02"},
            {"author": "reader4", "text": "Bookmarking this", "created": "2024-02-03"},
        ]
    },
    {
        "title": "Vector Search with MongoDB Atlas",
        "author": "kavya", "slug": "vector-search-atlas",
        "tags": ["mongodb", "ai", "vector-search", "advanced"],
        "comments": [
            {"author": "reader5", "text": "When is IVF better than HNSW?", "created": "2024-03-01"},
        ]
    },
]


def main():
    banner("Lab 7.1: Analyze a Production Schema")
    db = get_db("nosql_labs")
    col = reset_collection("nosql_labs", "blog_posts")
    col.insert_many(BLOG_POSTS)

    # Calculate document sizes with aggregation pipeline using $bsonSize
    print("=== Document Size Analysis ($bsonSize) ===")
    table = Table(title="Blog Post Document Sizes")
    table.add_column("Post", style="cyan", width=35)
    table.add_column("Comments", justify="right")
    table.add_column("BSON Size (bytes)", justify="right")
    table.add_column("Pattern", style="green")

    pipeline = [
        {
            "$project": {
                "title": 1,
                "author": 1,
                "slug": 1,
                "tags": 1,
                "comments": 1,
                "comments_count": {"$size": {"$ifNull": ["$comments", []]}},
                "bson_size": {"$bsonSize": "$$ROOT"}
            }
        }
    ]

    analyzed_posts = list(col.aggregate(pipeline))
    for post in analyzed_posts:
        size = post["bson_size"]
        table.add_row(
            post["title"][:35],
            str(post["comments_count"]),
            str(size),
            "Embedded comments" if post["comments_count"] <= 5 else "Consider referencing"
        )
    console.print(table)

    # Analyze embed vs reference patterns
    print("\n=== Embed vs Reference Pattern Analysis ===")
    avg_comments = sum(len(p['comments']) for p in BLOG_POSTS) / len(BLOG_POSTS)
    print(f"  Average comments per post: {avg_comments:.1f}")
    print(f"  Max comments: {max(len(p['comments']) for p in BLOG_POSTS)}")
    print(f"  Min comments: {min(len(p['comments']) for p in BLOG_POSTS)}")
    print()
    print("  Recommendation:")
    print("  - Comments < 100 per post -> EMBED (fewer queries, faster reads)")
    print("  - Comments > 100 per post -> REFERENCE (avoid 16MB doc limit)")
    print("  - Comments > 1000 per post -> PAGINATED REFERENCE (bucket pattern)")

    # Simulate Large Document Growth
    print("\n=== Simulating Large Document Growth ===")
    big_post = {"title": "Popular Post", "author": "celebrity"}
    growth_results = []

    for comment_count in [100, 1000, 10000, 50000]:
        text_payload = "Comment text: " + ("x" * (300 if comment_count == 50000 else 15))
        big_post["comments"] = [{"author": f"user{i}", "text": f"{text_payload} #{i}"} for i in range(comment_count)]
        doc_size = len(bson.encode(big_post))
        mb_size = doc_size / (1024 * 1024)
        pct_16mb = (doc_size / (16 * 1024 * 1024)) * 100
        growth_results.append({
            "comment_count": comment_count,
            "bytes": doc_size,
            "mb": round(mb_size, 3),
            "percent_of_16mb": round(pct_16mb, 2),
            "exceeds_limit": doc_size > 16 * 1024 * 1024
        })
        print(f"  {comment_count:>6,} comments -> {doc_size:>10,} bytes ({mb_size:>6.2f} MB - {pct_16mb:>5.1f}% of limit)")

    max_limit = 16 * 1024 * 1024
    print(f"  16 MB limit     -> {max_limit:>10,} bytes ( 16.00 MB)")
    if any(r["exceeds_limit"] for r in growth_results):
        print(f"  [WARN] 50K comments EXCEEDS 16MB limit! (MongoDB rejects document writes)")

    # Export output JSON
    output_data = {
        "lab": "Lab 7.1 - Analyze a Production Schema",
        "student": "Kasireddy Meghana",
        "usn": "24BTRCL119",
        "seeded_posts": analyzed_posts,
        "growth_simulation": growth_results,
        "limit_bytes": max_limit
    }
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema_analysis_output.json")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(output_data, indent=2, default=json_util.default))
    print(f"\n[OK] Results saved to {output_path}")

    banner("Lab 7.1 Complete")


if __name__ == "__main__":
    main()
