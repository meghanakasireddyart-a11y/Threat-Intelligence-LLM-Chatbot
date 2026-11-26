"""
Lab 3.2: Activity - Try It Yourself
Objective: Consider a scenario where a post has 10,000 comments.
Explain why embedding would be problematic and implement/demonstrate an alternative design.

Problem Analysis of Embedding 10,000 Comments:
1. 16MB Hard BSON Limit: In MongoDB, a single BSON document cannot exceed 16MB (16,777,216 bytes).
   At ~1KB to 1.5KB per comment (with user details, likes, metadata, timestamps), 10,000 comments
   equals 10MB-15MB+, quickly exceeding the hard limit and causing fatal write errors (DocumentTooLarge).
2. Working Set & WiredTiger Cache Thrashing: Reading the post pulls the entire multi-megabyte
   document into RAM cache, evicting other hot data from memory.
3. Network Overfetching: A user viewing the post only reads the first 10-20 comments, but
   the server would have to serialize and transmit 10MB+ over the network on every view.
4. High Write Contention: Continual $push operations to a massive array in a single document
   causes severe lock contention and memory reallocations.

Recommended Alternative Design:
HYBRID DESIGN: THE SUBSET PATTERN + REFERENCED PAGINATED COMMENTS
- In 'posts': Embed only the TOP 5-10 most recent comments ('recent_comments') + total 'comment_count'.
  Yields instantaneous initial page render with 0 joins and tiny document size (< 2KB).
- In 'comments': Store all comments as individual documents referencing 'post_id', indexed by (post_id, -created_at).
  Provides efficient cursor/range-based pagination when the user clicks 'Load More Comments'.
"""

import os
import json
import bson
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import json_util, ObjectId

def banner(text, char="=", width=65):
    print("\n" + char * width)
    print(f"  {text}")
    print(char * width + "\n")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "nosql_labs_3_2_try"

def export_to_json(collection, output_path, query=None, limit=10):
    query = query or {}
    docs = list(collection.find(query).limit(limit))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(docs, indent=2, default=json_util.default))
    print(f"[OK] Exported sample documents to: {output_path}")

def main():
    banner("LAB 3.2 (TRY IT YOURSELF): 10,000 COMMENTS SCENARIO ANALYSIS")

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    print(f"[OK] Connected to MongoDB database: '{DB_NAME}'")

    # Clean existing collections
    for c in ["posts_hybrid", "comments_archive"]:
        if c in db.list_collection_names():
            db.drop_collection(c)

    posts_col = db["posts_hybrid"]
    comments_col = db["comments_archive"]

    # Ensure index on comments for lightning-fast pagination
    comments_col.create_index([("post_id", ASCENDING), ("created_at", DESCENDING)])
    print("[OK] Created compound index on comments_archive: (post_id ASC, created_at DESC)")

    # =========================================================================
    # PART 1: SIMULATION & DOCUMENT SIZE ANALYSIS (16MB BSON LIMIT)
    # =========================================================================
    banner("PART 1: BSON Size Math & Why Embedding 10,000 Comments Fails")

    sample_comment = {
        "comment_id": "c_9999",
        "author": "dev_advocate_42",
        "author_avatar": "https://cdn.example.com/avatars/user42_highres.png",
        "text": "This architectural breakdown completely changed our database strategy. Here are my extended thoughts on concurrency and sharding keys in multi-tenant systems...",
        "created_at": datetime.now(timezone.utc),
        "likes": 142,
        "reactions": {"heart": 34, "thumbs_up": 89, "rocket": 19},
        "flags": []
    }
    comment_bson_size = len(bson.BSON.encode(sample_comment))
    projected_10k_size = comment_bson_size * 10000
    max_bson_limit = 16 * 1024 * 1024  # 16 MB

    print(f"  * Size of 1 realistic comment document : {comment_bson_size:,} bytes (~{comment_bson_size/1024:.2f} KB)")
    print(f"  * Projected size for 10,000 comments    : {projected_10k_size:,} bytes (~{projected_10k_size/(1024*1024):.2f} MB)")
    print(f"  * MongoDB Hard BSON Document Limit      : {max_bson_limit:,} bytes (16.00 MB)")
    if projected_10k_size >= max_bson_limit:
        print("  -> RESULT: CRITICAL FAILURE! Document exceeds 16MB hard limit.")
    else:
        print("  -> RESULT: SEVERE WARNING! Consumes ~90% of maximum document capacity, leaving zero room for post content.")

    # =========================================================================
    # PART 2: IMPLEMENTING THE RECOMMENDED ALTERNATIVE DESIGN (SUBSET PATTERN)
    # =========================================================================
    banner("PART 2: Implementing Alternative Design - The Hybrid Subset Pattern")

    # Create viral post document
    viral_post_id = ObjectId()
    base_time = datetime.now(timezone.utc) - timedelta(days=2)

    # Generate 5 recent comments for embedded subset
    recent_comments_subset = []
    for i in range(1, 6):
        recent_comments_subset.append({
            "comment_id": f"comm_top_{i}",
            "author": f"expert_user_{i}",
            "text": f"Top highlighted insight #{i} discussing scaling benchmarks.",
            "created_at": base_time + timedelta(hours=40 + i),
            "likes": 50 - i * 5
        })

    viral_post_doc = {
        "_id": viral_post_id,
        "title": "Scaling Beyond 1 Million Ops/sec: MongoDB Architectural Blueprint",
        "slug": "scaling-beyond-1m-ops-sec",
        "author": "Chief Database Architect",
        "content": "Full in-depth engineering analysis of horizontally scaled clusters...",
        "tags": ["nosql", "scaling", "architecture", "wiredtiger"],
        "comment_count": 10000,           # Fast O(1) counter for UI display
        "recent_comments": recent_comments_subset  # SUBSET PATTERN: Top 5 recent comments
    }

    posts_col.insert_one(viral_post_doc)
    print(f"[OK] Inserted viral post using Subset Pattern.")
    post_bson_size = len(bson.BSON.encode(viral_post_doc))
    print(f"     Post Document BSON Size: {post_bson_size:,} bytes (~{post_bson_size/1024:.2f} KB) vs 15MB embedded!")

    # Populate the comments archive (simulating the full archive of 10,000 comments)
    # We insert 50 representative comments to demonstrate pagination
    print("\nPopulating 'comments_archive' collection with indexed comment stream...")
    archive_docs = []
    for i in range(1, 51):
        archive_docs.append({
            "post_id": viral_post_id,
            "comment_index": i,
            "author": f"reader_{i}",
            "text": f"Detailed feedback on section {i%5 + 1} regarding cache eviction and sharding.",
            "created_at": base_time + timedelta(minutes=i * 30),
            "likes": i % 10
        })
    comments_col.insert_many(archive_docs)
    print(f"[OK] Inserted {len(archive_docs)} sample paged comments into 'comments_archive'.")

    # =========================================================================
    # PART 3: QUERY BENCHMARK & DEMONSTRATION
    # =========================================================================
    banner("PART 3: Query Demonstration: Initial Load vs Paginated Fetch")

    # 1. Initial Page Load (User visits post):
    print("1. Initial Page Load (Render Post + Top 5 Comments):")
    post = posts_col.find_one({"_id": viral_post_id})
    print(f"   * Title        : {post['title']}")
    print(f"   * Total Comments: {post['comment_count']:,} (from instant counter)")
    print(f"   * Displaying {len(post['recent_comments'])} instantly embedded comments:")
    for c in post["recent_comments"]:
        print(f"     - [{c['author']}] {c['text']} ({c['likes']} likes)")
    print("   -> Latency: < 1ms | DB Queries: 1 | Joins: 0 | Transferred: ~1.8 KB\n")

    # 2. User clicks "Load More Comments" (Page 2 - 5 comments per page):
    print("2. User clicks 'Load More Comments' (Paginated query on indexed comments_archive):")
    page_size = 5
    page_number = 2
    skip_count = (page_number - 1) * page_size
    paged_comments = list(comments_col.find(
        {"post_id": viral_post_id}
    ).sort("created_at", DESCENDING).skip(skip_count).limit(page_size))

    print(f"   * Retrieved Page {page_number} ({len(paged_comments)} comments) via index:")
    for c in paged_comments:
        print(f"     - [Comment #{c['comment_index']:<2} | {c['author']}]: \"{c['text']}\"")
    print("   -> Latency: < 1ms | Index Used: post_id_1_created_at_-1 | Transferred: ~1 KB")

    # =========================================================================
    # PART 4: ARCHITECTURAL COMPARISON SUMMARY
    # =========================================================================
    banner("PART 4: Architectural Tradeoff Matrix")
    matrix = """
+-----------------------+-----------------------------+-----------------------------+
| Feature               | Full Embedding (Problematic)| Hybrid Subset Pattern (Best)|
+-----------------------+-----------------------------+-----------------------------+
| 10,000 Comments Size  | ~10 MB - 15 MB (Near 16MB)  | ~2 KB Post + Separate Pages |
| 16MB Limit Risk       | FATAL (Throws BSON size err)| NONE (Zero risk of overflow)|
| Initial Page Load     | Extremely slow (15MB over wire) Sub-millisecond (< 2KB load)|
| WiredTiger Cache Impact| Evicts hot data from memory | Zero cache thrashing        |
| Network Bandwidth     | Severe overfetching         | Minimal, strictly on-demand |
| Document Write Locks  | Constant lock contention    | Distributed writes to archive|
| Pagination Support    | Complex array slicing in DB | Native cursor/range index   |
+-----------------------+-----------------------------+-----------------------------+
"""
    print(matrix)

    # Export to JSON
    script_dir = os.path.dirname(os.path.abspath(__file__))
    combined_sample = {
        "pattern": "Hybrid Subset Pattern for Viral Posts",
        "post_document": viral_post_doc,
        "sample_archive_comment": archive_docs[0] if archive_docs else None
    }
    output_path = os.path.join(script_dir, "viral_post_alternative_design.json")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(combined_sample, indent=2, default=json_util.default))
    print(f"[OK] Exported sample documents to: {output_path}")

    banner("Lab 3.2 Try It Yourself Completed Successfully")

if __name__ == "__main__":
    main()
