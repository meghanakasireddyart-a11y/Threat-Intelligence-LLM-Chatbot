# Docker Hub Deployment & Demonstration Guide: Lab 12

**Student:** Kasireddy Meghana  
**USN:** 24BTRCL119  
**Course:** NoSQL Databases Using MongoDB  
**Chapter:** Chapter 12 — Database Security, Authentication, RBAC & TLS Encryption  
**Docker Hub Repository:** [https://hub.docker.com/r/kasireddymeghana/nosql-lab12](https://hub.docker.com/r/kasireddymeghana/nosql-lab12)

---

## 1. Quick Start for Grading Demonstration

To evaluate and demonstrate the completed Lab 12 tasks using Docker, run:

```bash
# Pull the latest lab image
docker pull kasireddymeghana/nosql-lab12:latest

# Run the containerized interactive web platform on port 8012
docker run -d -p 8012:8012 --name nosql-lab12 kasireddymeghana/nosql-lab12:latest

# Open the interactive platform in your browser
# URL: http://localhost:8012
```

Navigate to the **🛡️ Lab 12: Auth, RBAC & TLS** tab on the navigation bar to interact with:
- **Lab 12.1 RBAC Permission Simulator**: Test user roles (`admin`, `app_user_read`, `app_user_write`, `limited_writer`, `hr_user`, `standard_user`) across target operations, proving that unauthorized writes and cross-database reads are intercepted with MongoDB `Code 13 (Unauthorized)`.
- **Activity 12.1 Field-Level Redaction Console**: Switch between the HR Department perspective (unrestricted access to salaries and SSNs) and the General Staff perspective (sanitized view where `salary` is stripped via `$$REMOVE` and `ssn` is masked).
- **Lab 12.2 TLS / Encryption-in-Transit Console**: Test and verify the rejection of unencrypted plaintext connections (`ServerSelectionTimeoutError`) alongside successful PyMongo mutual TLS connections with certificate chain verification (`CN=NoSQL-Labs-CA`, SAN `DNS:localhost, IP:127.0.0.1`).
- **Interactive Live Terminal**: Run the automated end-to-end Python security verification pipeline.

---

## 2. Docker Build & Push Instructions

```bash
# Navigate to the lab directory
cd "c:\Users\Prajwal\OneDrive\Desktop\NoSQL LAB 12"

# Build the Docker image
docker build -t kasireddymeghana/nosql-lab12:latest .

# Authenticate with Docker Hub
docker login

# Push the image to Docker Hub
docker push kasireddymeghana/nosql-lab12:latest
```

---

## 3. Multi-Container Secure Cluster with Docker Compose (Optional)

To launch MongoDB with authentication enabled and the web dashboard concurrently:

```bash
docker-compose up -d
```
