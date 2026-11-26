# NoSQL Lab 17 — Docker Hub Deployment Guide

## 🐳 Docker Hub Image

**Primary Repository:** `meghanakasireddy/nosql-lab17`  
**URL:** https://hub.docker.com/r/meghanakasireddy/nosql-lab17  
**Secondary Tag:** `kasireddymeghana/nosql-lab17`

## Quick Start

```bash
# Pull the latest image from Docker Hub
docker pull meghanakasireddy/nosql-lab17:latest

# Run the interactive web platform on port 8017
docker run -d -p 8017:8000 --name nosql-lab17 meghanakasireddy/nosql-lab17:latest

# Open in browser:
# → http://localhost:8017
```

## What's Inside

The container hosts the complete **NoSQL Lab interactive website** extended with the **Lab 17 tab** covering:

### Activity 1 — Build a Simple RAG Pipeline (`lab_01_rag_pipeline.py`)
- **Document Chunking & Vector Embeddings:** Demonstrates passage chunking (50 words per chunk), unit-normalized pseudo-random Gaussian mock embeddings (384 dimensions), and MongoDB storage in `nosql_labs.rag_documents`.
- **Cosine Similarity Dot Product:** Calculates cosine similarity efficiently via unit-vector dot product ($A \cdot B = \sum A_i B_i$).
- **Context Retrieval & Augmented Prompt Generation:** Retrieves top-$K$ most similar passages, constructs conversational prompts with memory, and synthesizes answers.
- **Mock vs. Real Embeddings Analysis:** Illustrates why hash-based mock embeddings can occasionally match unrelated passages vs. production semantic models (OpenAI `text-embedding-3-small`, Voyage AI `voyage-3`).

### Activity 2 — Compare HNSW and IVF Vector Index Types (`lab_02_hnsw_vs_ivf.py`)
- **ANN Search Fundamentals:** Demonstrates why brute-force linear search $\mathcal{O}(N \cdot D)$ breaks down at web scale and how Approximate Nearest Neighbor (ANN) indexes trade controlled accuracy for exponential retrieval speedups.
- **IVF (Inverted File Index):** Partitions vectors into $nlist$ clusters via k-means centroids. Queries only scan $nprobe$ closest clusters, discarding the rest of the dataset.
- **HNSW / Simplified NSW (Navigable Small World):** Forms a navigable graph traversed greedily from random entry points toward query vector proximity.
- **Interactive Benchmarks & Visualization:**
  - Dynamic parameter tuning ($N$, dimension, $K$, $nlist$, $nprobe$, $ef\_search$).
  - Metric comparison: Build Time (ms), Vectors Compared / Query (% of dataset), Avg Query Time (ms), and Recall@K.
  - 2D SVG cluster and graph traversal topology.
  - In-depth architectural analysis explaining why **Vectors Compared per Query** is the definitive scaling metric.

## Build and Push from Source

```bash
# Navigate to the Lab 17 directory
cd "c:\Users\Prajwal\OneDrive\Desktop\NoSQL LAB 17"

# Run the automated build and push batch script
.\build_and_push.bat
```

Or manually:

```bash
docker build -t meghanakasireddy/nosql-lab17:latest -t kasireddymeghana/nosql-lab17:latest .
docker push meghanakasireddy/nosql-lab17:latest
docker push kasireddymeghana/nosql-lab17:latest
```

## Stop & Remove Container

```bash
docker stop nosql-lab17 && docker rm nosql-lab17
```
