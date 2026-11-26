# Docker Hub Upload & Grading Verification Guide: NoSQL Lab 9

**Student Name:** Kasireddy Meghana  
**University USN:** 24BTRCL119  
**Course:** NoSQL Databases Using MongoDB  
**Chapter:** Chapter 09 - CAP Theorem, Consistency Guarantees & Network Partitions  
**Public Docker Hub Repository:** https://hub.docker.com/r/kasireddymeghana/nosql-lab09  

---

## 1. Quick Demonstration Commands for Evaluator / Grader

The container image is packaged to demonstrate all Lab 9 deliverables, benchmarks, and network partition simulations:

```bash
# Step 1: Pull the published demonstration container image
docker pull kasireddymeghana/nosql-lab09:latest

# Step 2: Run the demonstration container exposing port 8009
docker run -d -p 8009:8009 --name lab09-demonstration kasireddymeghana/nosql-lab09:latest

# Step 3: Access the interactive web portal in any browser:
# http://localhost:8009/
```

To run the automated terminal verification script inside the container:
```bash
docker exec -it lab09-demonstration python lab_01_write_concern_latency.py
docker exec -it lab09-demonstration python lab_02_simulate_partition.py
```

---

## 2. Docker Build & Push Instructions (Student Verification)

```bash
# 1. Authenticate to Docker Hub
docker login

# 2. Build the Docker image
docker build -t kasireddymeghana/nosql-lab09:latest .

# 3. Push to Docker Hub
docker push kasireddymeghana/nosql-lab09:latest
```

---

## 3. Deliverables Summary

| Deliverable | Description |
|---|---|
| **PDF Report** | `Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_09.pdf` (Includes Docker URL, tables, analysis & screenshots) |
| **DOCX Report** | `Kasireddy_Meghana_24BTRCL119_NoSQL_Lab_09.docx` |
| **Docker Hub URL** | https://hub.docker.com/r/kasireddymeghana/nosql-lab09 |
| **Lab 7 Integration** | Added Lab 9 interactive module tab and endpoints to Lab 7 Web Portal |
| **Submission Archive** | `Kasireddy_Meghana_24BTRCL119_Lab9_NoSQL.zip` |
