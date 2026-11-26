"""Activity 7.1 Try-It-Yourself: Embedded vs Referenced vs Bucket Pattern Benchmark
Author: Kasireddy Meghana (USN: 24BTRCL119)
Course: NoSQL Databases (MongoDB) - Lab 7

Empirically benchmarks:
1. Pure Embedded Schema: Read latency, BSON payload size, $push write cost
2. 1-to-N Referenced Schema: Query + $lookup join cost, modular insert cost
3. Bucket Pattern (Hybrid): Paginated 50-comment buckets with bounded document sizes
"""

import sys, os, time, json
import bson
from bson import json_util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.connection import get_db, reset_collection, banner
from rich.table import Table
from rich.console import Console

console = Console()


def run_benchmark():
    banner("Activity 7.1 Try-It-Yourself: Embed vs Reference vs Bucket")
    db = get_db("nosql_labs")

    col_embedded = reset_collection("nosql_labs", "bench_embedded")
    col_posts = reset_collection("nosql_labs", "bench_ref_posts")
    col_comments = reset_collection("nosql_labs", "bench_ref_comments")
    col_buckets = reset_collection("nosql_labs", "bench_buckets")

    col_comments.create_index([("post_id", 1)])
    col_buckets.create_index([("post_id", 1), ("bucket_num", 1)])

    num_comments = 500
    print(f"[*] Setting up benchmark with {num_comments} comments per post...")

    # 1. Setup Embedded Post
    comments_payload = [
        {"author": f"user_{i}", "text": f"Insightful comment #{i} regarding system architectures.", "date": "2024-03-01"}
        for i in range(num_comments)
    ]
    embedded_doc = {
        "_id": "post_embed_101",
        "title": "Scaling Distributed Systems with MongoDB",
        "author": "system_architect",
        "comments": comments_payload
    }
    col_embedded.insert_one(embedded_doc)

    # 2. Setup Referenced Post
    col_posts.insert_one({
        "_id": "post_ref_101",
        "title": "Scaling Distributed Systems with MongoDB",
        "author": "system_architect"
    })
    ref_comments = [
        {"post_id": "post_ref_101", "author": f"user_{i}", "text": f"Insightful comment #{i} regarding system architectures.", "date": "2024-03-01"}
        for i in range(num_comments)
    ]
    col_comments.insert_many(ref_comments)

    # 3. Setup Bucket Pattern (Buckets of 50 comments each -> 10 buckets)
    bucket_size = 50
    for b_idx in range(num_comments // bucket_size):
        slice_comments = comments_payload[b_idx*bucket_size : (b_idx+1)*bucket_size]
        col_buckets.insert_one({
            "post_id": "post_ref_101",
            "bucket_num": b_idx + 1,
            "count": len(slice_comments),
            "comments": slice_comments
        })

    # Benchmark Reads
    print("\n=== Read Performance Benchmark (100 iterations) ===")
    iterations = 100

    # Pattern A: Embedded single-doc read
    t0 = time.perf_counter()
    for _ in range(iterations):
        doc = col_embedded.find_one({"_id": "post_embed_101"})
    embedded_read_ms = ((time.perf_counter() - t0) / iterations) * 1000

    # Pattern B: Referenced read with $lookup join
    lookup_pipeline = [
        {"$match": {"_id": "post_ref_101"}},
        {"$lookup": {
            "from": "bench_ref_comments",
            "localField": "_id",
            "foreignField": "post_id",
            "as": "comments"
        }}
    ]
    t0 = time.perf_counter()
    for _ in range(iterations):
        doc = list(col_posts.aggregate(lookup_pipeline))[0]
    ref_lookup_read_ms = ((time.perf_counter() - t0) / iterations) * 1000

    # Pattern C: Bucket Pattern read (fetching page 1 = bucket 1)
    t0 = time.perf_counter()
    for _ in range(iterations):
        bucket = col_buckets.find_one({"post_id": "post_ref_101", "bucket_num": 1})
    bucket_read_ms = ((time.perf_counter() - t0) / iterations) * 1000

    # Benchmark Writes ($push to embedded vs insert to referenced collection)
    print("\n=== Write Performance Benchmark (50 writes) ===")
    write_iters = 50

    t0 = time.perf_counter()
    for i in range(write_iters):
        col_embedded.update_one(
            {"_id": "post_embed_101"},
            {"$push": {"comments": {"author": f"new_user_{i}", "text": "Appended comment", "date": "2024-03-02"}}}
        )
    embedded_write_ms = ((time.perf_counter() - t0) / write_iters) * 1000

    t0 = time.perf_counter()
    for i in range(write_iters):
        col_comments.insert_one({
            "post_id": "post_ref_101",
            "author": f"new_user_{i}",
            "text": "Appended comment",
            "date": "2024-03-02"
        })
    ref_write_ms = ((time.perf_counter() - t0) / write_iters) * 1000

    # Measure BSON sizes
    embed_doc_size = len(bson.encode(col_embedded.find_one({"_id": "post_embed_101"})))
    ref_post_size = len(bson.encode(col_posts.find_one({"_id": "post_ref_101"})))
    one_bucket_size = len(bson.encode(col_buckets.find_one({"post_id": "post_ref_101", "bucket_num": 1})))

    # Print Comparison Table
    table = Table(title=f"Schema Strategy Benchmark ({num_comments} Comments)")
    table.add_column("Pattern", style="cyan", width=22)
    table.add_column("Doc Size", justify="right")
    table.add_column("Read Latency", justify="right")
    table.add_column("Write Latency", justify="right")
    table.add_column("16MB Risk", style="bold")

    table.add_row(
        "Embedded Array",
        f"{embed_doc_size:,} B",
        f"{embedded_read_ms:.2f} ms",
        f"{embedded_write_ms:.2f} ms",
        "[red]High (Unbounded)[/red]"
    )
    table.add_row(
        "Referenced ($lookup)",
        f"{ref_post_size:,} B",
        f"{ref_lookup_read_ms:.2f} ms",
        f"{ref_write_ms:.2f} ms",
        "[green]None (1 doc/comment)[/green]"
    )
    table.add_row(
        "Bucket Pattern (50/doc)",
        f"{one_bucket_size:,} B",
        f"{bucket_read_ms:.2f} ms",
        "-",
        "[green]None (Bounded)[/green]"
    )
    console.print(table)

    results = {
        "benchmark": "Activity 7.1 Try It Yourself",
        "comments_per_post": num_comments,
        "metrics": {
            "embedded": {
                "doc_size_bytes": embed_doc_size,
                "avg_read_ms": round(embedded_read_ms, 3),
                "avg_write_push_ms": round(embedded_write_ms, 3)
            },
            "referenced": {
                "post_doc_size_bytes": ref_post_size,
                "avg_read_lookup_ms": round(ref_lookup_read_ms, 3),
                "avg_write_insert_ms": round(ref_write_ms, 3)
            },
            "bucket_pattern": {
                "bucket_doc_size_bytes": one_bucket_size,
                "avg_read_page1_ms": round(bucket_read_ms, 3)
            }
        }
    }

    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "embed_vs_reference_comparison.json")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(results, indent=2))
    print(f"\n[OK] Comparison results saved to {out_file}")
    banner("Activity 7.1 Try-It-Yourself Complete")


if __name__ == "__main__":
    run_benchmark()
