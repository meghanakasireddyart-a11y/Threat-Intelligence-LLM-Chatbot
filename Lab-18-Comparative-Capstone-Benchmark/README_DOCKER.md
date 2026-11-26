# NoSQL Lab 18: Comparative Capstone Lab & Technical Analysis Report

[![Docker Image](https://img.shields.io/badge/Docker%20Hub-meghanakasireddy%2Fnosql--lab18-blue.svg)](https://hub.docker.com/r/meghanakasireddy/nosql-lab18)
[![Version](https://img.shields.io/badge/version-1.0-green.svg)]()
[![Course](https://img.shields.io/badge/NoSQL-Lab%2018%20Capstone-orange.svg)]()

This repository contains the containerized deployment for **NoSQL Lab 18: Comparative Capstone Lab**, evaluating a realistic multi-pattern fraud detection workload across **MongoDB**, **Apache Cassandra**, and **Neo4j**.

---

## 🚀 Quick Start (Docker Hub)

You can pull and run the pre-built container directly from Docker Hub:

```bash
# Pull the latest image
docker pull meghanakasireddy/nosql-lab18:latest

# Run container on port 8018
docker run -d -p 8018:8000 --name nosql-lab18 meghanakasireddy/nosql-lab18:latest

# Open in your web browser:
# http://localhost:8018
```

Alternatively, use the mirror tag:
```bash
docker pull kasireddymeghana/nosql-lab18:latest
docker run -d -p 8018:8000 --name nosql-lab18 kasireddymeghana/nosql-lab18:latest
```

---

## 📋 Lab 18 Overview

This capstone synthesizes concepts from CRUD (Ch 4), aggregation (Ch 5), indexing (Ch 6), transactions (Ch 10), and polyglot architecture comparisons (Ch 16).

### 1. Why Fraud Detection?
A fair benchmark requires an unbiased workload stressing 4 orthogonal access patterns simultaneously:
- **Q1: Point Lookups:** User transaction history sorted by event timestamp.
- **Q2: Attribute Filtering:** Ad-hoc range scan on risk score (`risk_score > 0.8`).
- **Q3: Category Analytics:** Native aggregation pipeline calculating spending totals and counts.
- **Q4: Write Throughput:** High-throughput batch insertion (1,000+ transactions).
- *(Extended):* Multi-hop relationship traversal across accounts sharing devices.

### 2. Measured vs. Estimated Rigor
In real-world systems engineering, benchmarked and estimated numbers must **never be blended ambiguously**:
- **MongoDB:** Live measured latencies against a 10,000 document indexed collection (`idx_user_time`, `idx_risk`, `idx_category`).
- **Cassandra & Neo4j:** Rigorous architectural estimates derived from underlying storage engines (LSM-tree commit log vs index-free adjacency graph pointers).

---

## 📑 Generated Technical Report Structure

Executing `lab_02_comparative_report.py` generates a production-grade markdown report:
1. **Executive Summary:** High-level polyglot operational strategy.
2. **System Architecture:** ASCII & structural diagrams of MongoDB operational core with Neo4j specialized graph sidecar.
3. **Query Performance Comparison:** Explicitly segregated table distinguishing live measured numbers from architectural estimates.
4. **Data Modeling Analysis:** Document vs Wide-Column vs Property Graph trade-offs.
5. **Scalability Assessment Matrix:** Comparative capabilities across 1M, 10M, and 100M transaction tiers.
6. **Final Production Recommendation:** Defensible rationale for choosing MongoDB as the primary operational store, omitting Cassandra for ad-hoc queries, and adding Neo4j only when multi-hop fraud rings become a first-class requirement.

---

## 🛠️ Local Development & Scripts

### Run Activities Locally:
```bash
# Activity 1: Comparative Capstone Benchmark
python lab_01_comparative_capstone.py

# Activity 2: Comparative Analysis Report Generator
python lab_02_comparative_report.py
```

### Start Web Dashboard:
```bash
python website/server.py 8018
```

---

## 🐳 Docker Build & Push

To build and publish manually:
```bash
docker build -t meghanakasireddy/nosql-lab18:latest -t kasireddymeghana/nosql-lab18:latest .
docker push meghanakasireddy/nosql-lab18:latest
docker push kasireddymeghana/nosql-lab18:latest
```
