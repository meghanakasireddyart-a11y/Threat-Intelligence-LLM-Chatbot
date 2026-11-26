# NoSQL Lab 16 — Docker Hub Deployment Guide

## 🐳 Docker Hub Image

**Primary Repository:** `meghanakasireddy/nosql-lab16`  
**URL:** https://hub.docker.com/r/meghanakasireddy/nosql-lab16  
**Secondary Tag:** `kasireddymeghana/nosql-lab16`

## Quick Start

```bash
# Pull the latest image from Docker Hub
docker pull meghanakasireddy/nosql-lab16:latest

# Run the interactive web platform on port 8016
docker run -d -p 8016:8000 --name nosql-lab16 meghanakasireddy/nosql-lab16:latest

# Open in browser:
# → http://localhost:8016
```

## What's Inside

The container hosts the complete **NoSQL Lab interactive website** extended with the **Lab 16 tab** covering:

### Activity 1 — Model Data in Three Databases (`lab_01_polyglot_modeling.py`)
- **Side-by-Side Polyglot Schema Comparison:** Evaluates how the same fraud case is modeled across MongoDB, Cassandra, and Neo4j.
  - **MongoDB (Document):** Flexible BSON document in `fraud_cases` with embedded arrays (`tags`, `linked_accounts`), optimized for single-read entity retrieval and compound range filtering (`risk_score > 0.8 AND amount > 10000`).
  - **Cassandra (Wide-Column):** Partition-based table `fraud_events` with `PRIMARY KEY ((suspect_id), event_time) WITH CLUSTERING ORDER BY (event_time DESC)`. Enforces Cassandra's defining rule: *design the table around the query, not the entity*.
  - **Neo4j (Property Graph):** Nodes (`User`, `Merchant`, `Transaction`) connected by first-class relationships (`[:MADE]`, `[:RECEIVED]`, `[:SHARES_DEVICE_WITH]`, `[:TRANSFERRED_TO]`), optimized for multi-hop fraud ring traversal (`MATCH path = (u1:User)-[:SHARES_DEVICE_WITH*1..3]-(u2:User)`).
- **Architectural Bias & Awkward Queries Matrix:** Explains why each database struggles when queried outside its structural bias (e.g. MongoDB ballooning memory on recursive `$graphLookup`, Cassandra requiring cluster scans without partition keys, Neo4j incurring high overhead for raw unlinked append logs).

### Activity 2 — Build a Hybrid Query Service (`lab_02_hybrid_query_service.py`)
- **Intelligent Query Dispatcher:** Implements real-world *polyglot persistence* by dynamically routing queries to the most suitable engine:
  - **Point Lookup by Case ID (`FC-001`):** Routed to **MongoDB** (O(1)/O(log N) indexed single-document read).
  - **Attribute Range Filter (`risk_score > 0.8`):** Routed to **MongoDB** (native B-Tree range index scan).
  - **Multi-Hop Traversal (Suspect device sharing within 1-3 hops):** Routed to **Graph Engine** (Neo4j native Cypher or in-memory BFS fallback using index-free adjacency).
- **Interactive Visualizations:**
  - Real-time SVG topological graph visualizer with dynamic hop highlighting.
  - Interactive Query Router allowing custom parameter adjustments (risk score thresholds, suspect IDs, hop depths).
  - Live CLI execution terminal streaming the outputs of `lab_01_polyglot_modeling.py` and `lab_02_hybrid_query_service.py`.

## Build and Push from Source

```bash
# Navigate to the Lab 16 directory
cd "c:\Users\Prajwal\OneDrive\Desktop\NoSQL LAB 16"

# Run the automated build and push batch script
.\build_and_push.bat
```

Or manually:

```bash
docker build -t meghanakasireddy/nosql-lab16:latest -t kasireddymeghana/nosql-lab16:latest .
docker push meghanakasireddy/nosql-lab16:latest
```

## Stop & Remove Container

```bash
docker stop nosql-lab16 && docker rm nosql-lab16
```
