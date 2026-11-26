# NoSQL Lab 13 — Docker Hub Deployment Guide

## 🐳 Docker Hub Image

**Repository:** `kasireddymeghana/nosql-lab13`  
**URL:** https://hub.docker.com/r/kasireddymeghana/nosql-lab13

## Quick Start

```bash
# Pull the latest image
docker pull kasireddymeghana/nosql-lab13:latest

# Run the interactive web console on port 8013
docker run -d -p 8013:8000 --name nosql-lab13 kasireddymeghana/nosql-lab13:latest

# Open the web interface
# → http://localhost:8013
```

## What's Inside

The container hosts the full **NoSQL Lab 7 interactive website** extended with a **Lab 13 tab** covering:

### Activity 1 — Production Replica Set (Docker Compose)
- keyFile authentication (inter-node trust)
- Admin user created before `rs.initiate()`
- Side-by-side comparison with Chapter 8's unauthenticated replica set
- Live deployment step simulator

### Activity 2 — Kubernetes StatefulSet
- 4 generated Kubernetes manifests:
  - `00-namespace.yaml` — nosql-labs Namespace
  - `01-headless-service.yaml` — clusterIP: None for stable pod DNS
  - `02-statefulset.yaml` — 3 mongo pods with readiness/liveness probes
  - `03-replicaset-init-job.yaml` — one-shot rs.initiate() Job
- Interactive manifest viewer
- Kubernetes deployment simulator explaining StatefulSet vs Deployment

## Build from Source

```bash
# From the NoSQL LAB 7 directory (contains website/ and config/)
docker build \
  -t kasireddymeghana/nosql-lab13:latest \
  -f "../NoSQL LAB 13/Dockerfile" \
  .

docker push kasireddymeghana/nosql-lab13:latest
```

## Stop & Remove

```bash
docker stop nosql-lab13 && docker rm nosql-lab13
```
