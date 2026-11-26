"""
Lab 3.2: Migrate from Referenced to Embedded Design
Objective: Convert a referenced design to an embedded design and compare performance characteristics.

Instructions:
1. Create a blog system with separate collections for posts and comments (referenced design).
   Insert 5 posts and at least 10 comments.
2. Write a query using $lookup to retrieve a post with its comments in a single query.
3. Redesign the system using embedding (comments as an array within the post document).
   Migrate the data from the referenced design to the embedded design using an aggregation pipeline / Python script.
4. Compare the number of database queries required to display a post with its comments in both designs.
5. Export the collections to JSON files.
"""

import os
import json
import time
from datetime import datetime, timezone
from pymongo import MongoClient
from bson import json_util, ObjectId

def banner(text, char="=", width=65):
    print("\n" + char * width)
    print(f"  {text}")
    print(char * width + "\n")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "nosql_labs_3_2"

def export_to_json(collection, output_path):
    docs = list(collection.find())
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(docs, indent=2, default=json_util.default))
    print(f"[OK] Exported {len(docs)} documents to: {output_path}")

def main():
    banner("LAB 3.2: MIGRATE FROM REFERENCED TO EMBEDDED DESIGN")

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    print(f"[OK] Connected to MongoDB database: '{DB_NAME}'")

    # Clean existing collections
    for col_name in ["posts_referenced", "comments_referenced", "posts_embedded"]:
        if col_name in db.list_collection_names():
            db.drop_collection(col_name)

    posts_col = db["posts_referenced"]
    comments_col = db["comments_referenced"]

    # =========================================================================
    # STEP 1: CREATE REFERENCED DESIGN (Separate Posts and Comments)
    # =========================================================================
    banner("Step 1: Inserting 5 Posts and 12 Comments (Referenced Design)")

    posts_data = [
        {
            "title": "Demystifying MongoDB Document Modeling",
            "author": "Dr. Priya Sharma",
            "tags": ["mongodb", "nosql", "architecture"],
            "published_at": "2026-01-10T10:00:00Z"
        },
        {
            "title": "Scaling Distributed Databases with Sharding",
            "author": "Arjun Mehta",
            "tags": ["distributed-systems", "sharding", "scalability"],
            "published_at": "2026-01-15T14:30:00Z"
        },
        {
            "title": "Building Real-time Pipelines with Change Streams",
            "author": "Sneha Reddy",
            "tags": ["real-time", "kafka", "mongodb"],
            "published_at": "2026-01-20T09:15:00Z"
        },
        {
            "title": "CAP Theorem Tradeoffs in Modern Cloud NoSQL",
            "author": "Dr. Priya Sharma",
            "tags": ["cap-theorem", "cloud", "consistency"],
            "published_at": "2026-01-25T11:45:00Z"
        },
        {
            "title": "Vector Search and Generative AI Integrations",
            "author": "Vikram Singh",
            "tags": ["ai", "vector-search", "embeddings"],
            "published_at": "2026-02-01T16:00:00Z"
        }
    ]

    post_insert_result = posts_col.insert_many(posts_data)
    post_ids = post_insert_result.inserted_ids
    print(f"[OK] Inserted {len(post_ids)} posts into 'posts_referenced'.")

    # Insert 12 comments linked via foreign key 'post_id'
    comments_data = [
        {"post_id": post_ids[0], "author": "Arjun Mehta", "text": "Brilliant explanation of embedding vs referencing!", "likes": 12},
        {"post_id": post_ids[0], "author": "Sneha Reddy", "text": "Very clear guidelines on 16MB document boundary.", "likes": 5},
        {"post_id": post_ids[0], "author": "Rahul Kumar", "text": "Can you provide more examples on $lookup performance?", "likes": 3},
        {"post_id": post_ids[1], "author": "Dr. Priya Sharma", "text": "Great overview of chunk balancing and shard keys.", "likes": 14},
        {"post_id": post_ids[1], "author": "Vikram Singh", "text": "Ranged vs hashed sharding trade-offs are super relevant.", "likes": 8},
        {"post_id": post_ids[2], "author": "Kavya Nair", "text": "We implemented change streams in our microservices last month!", "likes": 9},
        {"post_id": post_ids[2], "author": "Arjun Mehta", "text": "How do change streams handle resume tokens during network partitions?", "likes": 7},
        {"post_id": post_ids[3], "author": "Rahul Kumar", "text": "PACELC theorem explains latency tradeoffs even better.", "likes": 11},
        {"post_id": post_ids[3], "author": "Sneha Reddy", "text": "Tunable consistency in MongoDB (majority write concern) is a lifesaver.", "likes": 6},
        {"post_id": post_ids[4], "author": "Divya Patel", "text": "Vector search with HNSW indexes in MongoDB Atlas is fast!", "likes": 15},
        {"post_id": post_ids[4], "author": "Arjun Mehta", "text": "Are embeddings stored as BSON Binary arrays?", "likes": 4},
        {"post_id": post_ids[4], "author": "Sneha Reddy", "text": "Yes, binary float32 arrays yield the lowest memory footprint.", "likes": 8}
    ]

    comment_insert_result = comments_col.insert_many(comments_data)
    print(f"[OK] Inserted {len(comment_insert_result.inserted_ids)} comments into 'comments_referenced'.")

    # =========================================================================
    # STEP 2: QUERY USING $lookup TO RETRIEVE POST WITH COMMENTS IN SINGLE QUERY
    # =========================================================================
    banner("Step 2: Single Query Join Using $lookup Aggregation")
    target_post_id = post_ids[0]

    lookup_pipeline = [
        {"$match": {"_id": target_post_id}},
        {
            "$lookup": {
                "from": "comments_referenced",
                "localField": "_id",
                "foreignField": "post_id",
                "as": "comments"
            }
        }
    ]

    joined_post = list(posts_col.aggregate(lookup_pipeline))[0]
    print(f"Retrieved Post: '{joined_post['title']}' by {joined_post['author']}")
    print(f"Total Comments Joined: {len(joined_post['comments'])}")
    for i, c in enumerate(joined_post["comments"], 1):
        print(f"   [{i}] {c['author']}: \"{c['text']}\" ({c['likes']} likes)")

    # =========================================================================
    # STEP 3: MIGRATE REFERENCED DESIGN TO EMBEDDED DESIGN
    # =========================================================================
    banner("Step 3: Migrating Data from Referenced to Embedded Design")

    # Perform migration using an Aggregation Pipeline with $out stage
    migration_pipeline = [
        {
            "$lookup": {
                "from": "comments_referenced",
                "let": {"pid": "$_id"},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$post_id", "$$pid"]}}},
                    {"$project": {"_id": 1, "author": 1, "text": 1, "likes": 1}}
                ],
                "as": "comments"
            }
        },
        {"$out": "posts_embedded"}
    ]

    posts_col.aggregate(migration_pipeline)
    embedded_col = db["posts_embedded"]
    migrated_count = embedded_col.count_documents({})
    print(f"[OK] Migration completed! Created 'posts_embedded' with {migrated_count} documents.")

    # Verify an embedded document
    sample_embedded = embedded_col.find_one({"_id": target_post_id})
    print(f"[OK] Sample Embedded Document Verified:")
    print(f"     Title: {sample_embedded['title']}")
    print(f"     Embedded comments array length: {len(sample_embedded['comments'])}")

    # =========================================================================
    # STEP 4: PERFORMANCE & QUERY COUNT COMPARISON
    # =========================================================================
    banner("Step 4: Query Count and Architectural Comparison")

    print("Retrieving post with all comments:")
    print("  * REFERENCED DESIGN (Two Approaches):")
    print("      Option A: 2 separate round-trip queries:")
    print("                1. posts_col.find_one({'_id': post_id})")
    print("                2. comments_col.find({'post_id': post_id})")
    print("      Option B: 1 query with $lookup aggregation stage (server-side join)")
    print()
    print("  * EMBEDDED DESIGN:")
    print("      Option A: Exactly 1 single find_one() query:")
    print("                embedded_col.find_one({'_id': post_id})")
    print("                (Direct index seek on _id, zero joins, single disk block read)")
    print()

    comparison_table = """
+-----------------------+-----------------------------+-----------------------------+
| Feature / Metric      | Referenced Design           | Embedded Design             |
+-----------------------+-----------------------------+-----------------------------+
| Collections           | 2 (posts, comments)         | 1 (posts_embedded)          |
| Number of DB Queries  | 2 queries (or 1 $lookup)    | 1 query (simple find_one)   |
| Database Joins        | Required ($lookup stage)    | None (Zero joins required)  |
| Read Latency          | Higher (Foreign key lookup) | Lowest (Single BSON fetch)  |
| Data Atomicity        | Multi-document / non-atomic | Fully atomic (single doc)   |
| Document Size Growth  | Fixed / Static posts        | Grows with comment count    |
| Maximum Scale Limit   | Virtually unbounded         | Limited by 16MB BSON limit  |
| Best Use Case         | Comments > 1,000 / Unbounded| Moderate comments (< 100)   |
+-----------------------+-----------------------------+-----------------------------+
"""
    print(comparison_table)

    # Export collections to JSON
    script_dir = os.path.dirname(os.path.abspath(__file__))
    export_to_json(embedded_col, os.path.join(script_dir, "posts_embedded.json"))
    export_to_json(posts_col, os.path.join(script_dir, "posts_referenced.json"))
    export_to_json(comments_col, os.path.join(script_dir, "comments.json"))

    banner("Lab 3.2 Completed Successfully")

if __name__ == "__main__":
    main()
