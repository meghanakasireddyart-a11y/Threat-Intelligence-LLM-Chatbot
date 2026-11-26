# Docker Hub Deployment & Demonstration Guide: Lab 11

**Student:** Kasireddy Meghana  
**USN:** 24BTRCL119  
**Course:** NoSQL Databases Using MongoDB  
**Chapter:** Chapter 11 — Sharding Architectures & Shard Key Optimization  
**Docker Hub Repository:** [https://hub.docker.com/r/kasireddymeghana/nosql-lab11](https://hub.docker.com/r/kasireddymeghana/nosql-lab11)

---

## 1. Quick Start for Grading Demonstration

To evaluate and demonstrate the completed Lab 11 tasks using Docker, run:

```bash
# Pull the latest lab image
docker pull kasireddymeghana/nosql-lab11:latest

# Run the containerized interactive web platform on port 8011
docker run -d -p 8011:8011 --name nosql-lab11 kasireddymeghana/nosql-lab11:latest

# Open the interactive platform in your browser
# URL: http://localhost:8011
```

Navigate to the **🔀 Lab 11: Sharding & Shard Keys** tab on the navigation bar to interact with:
- **Lab 11.1 Shard Key Decision Matrix**: Interactive scoring calculator across Cardinality, Distribution Uniformity, Query Targeting, and Monotonicity Safety.
- **Lab 11.2 Hotspot Detection**: 10,000 document insert simulator comparing `{ts: 1}` (95% write hotspot) vs `{user_id: 'hashed'}` (50%/50% balanced distribution).
- **Live explain() Analysis**: Side-by-side execution plan visualizer demonstrating `SINGLE_SHARD` targeted routing vs `SHARD_MERGE` scatter-gather broadcast.
- **MongoDB 5.0+ Online Resharding Research**: Steps, internals, and operational trade-offs.

---

## 2. Docker Build & Push Instructions

```bash
# Navigate to the lab directory
cd "c:\Users\Prajwal\OneDrive\Desktop\NoSQL LAB 11"

# Build the Docker image
docker build -t kasireddymeghana/nosql-lab11:latest .

# Authenticate with Docker Hub
docker login

# Push the image to Docker Hub
docker push kasireddymeghana/nosql-lab11:latest
```

---

## 3. Two-Shard Cluster with Docker Compose (Optional Full Setup)

To launch a complete multi-container sharded cluster (config replica set, Shard A, Shard B, mongos router, and web portal):

```bash
docker-compose -f docker-compose-sharding.yml up -d
```
