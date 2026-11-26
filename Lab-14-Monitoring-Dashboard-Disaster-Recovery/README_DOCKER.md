# NoSQL Lab 14 — Docker Hub Deployment Guide

## 🐳 Docker Hub Image

**Repository:** `meghanakasireddy/nosql-lab14`  
**URL:** https://hub.docker.com/r/meghanakasireddy/nosql-lab14

## Quick Start

```bash
# Pull the latest image from Docker Hub
docker pull meghanakasireddy/nosql-lab14:latest

# Run the interactive web platform on port 8014
docker run -d -p 8014:8000 --name nosql-lab14 meghanakasireddy/nosql-lab14:latest

# Open in browser:
# → http://localhost:8014
```

## What's Inside

The container hosts the complete **NoSQL Lab interactive website** extended with the **Lab 14 tab** covering:

### Activity 1 — Production Monitoring Dashboard (`lab_01_monitoring_dashboard.py`)
- Real-time MongoDB `serverStatus` administrative telemetry
- WiredTiger memory cache residency & cache eviction pressures
- Active and available connection pool metrics
- Cumulative operation counters (Insert, Query, Update, Delete)
- Proactive alerting threshold evaluation (Cache > 80%, Connections > 80% limit)
- Append-only time-series logging to `logs/metrics.log` for post-incident root-cause analysis

### Activity 2 — Automated Backup and Restore Verification (`lab_02_backup_restore.py`)
- Automated disaster recovery pipeline with `mongodump` & `mongorestore`
- "A backup you haven't restored is a hope, not a guarantee"
- Dual-factor verification: Document count matching (weak check) vs Content Checksum (SHA-256)
- Independent document sorting and `_id` stripping for deterministic cryptographic verification
- Interactive silent data corruption injection simulator to prove why count matching alone is insufficient
- Real-world Recovery Point Objective (RPO) and Recovery Time Objective (RTO) benchmarking

## Build and Push from Source

```bash
# Navigate to the Lab 14 directory
cd "c:\Users\Prajwal\OneDrive\Desktop\NoSQL LAB 14"

# Run the automated build and push batch script
.\build_and_push.bat
```

Or manually:

```bash
docker build -t meghanakasireddy/nosql-lab14:latest .
docker push meghanakasireddy/nosql-lab14:latest
```

## Stop & Remove Container

```bash
docker stop nosql-lab14 && docker rm nosql-lab14
```
