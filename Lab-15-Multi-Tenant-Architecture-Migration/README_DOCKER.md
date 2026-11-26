# NoSQL Lab 15 — Docker Hub Deployment Guide

## 🐳 Docker Hub Image

**Repository:** `meghanakasireddy/nosql-lab15`  
**URL:** https://hub.docker.com/r/meghanakasireddy/nosql-lab15

## Quick Start

```bash
# Pull the latest image from Docker Hub
docker pull meghanakasireddy/nosql-lab15:latest

# Run the interactive web platform on port 8015
docker run -d -p 8015:8000 --name nosql-lab15 meghanakasireddy/nosql-lab15:latest

# Open in browser:
# → http://localhost:8015
```

## What's Inside

The container hosts the complete **NoSQL Lab interactive website** extended with the **Lab 15 tab** covering:

### Activity 1 — Design a Multi-Tenant API (`lab_01_multitenant_api.py`)
- **Shared-Collection Isolation:** Storing tasks for all tenants in `saas_app.tasks` distinguished by `tenant_id`.
- **Critical Isolation Guard:** Mandatory compound filter `{"_id": task_id, "tenant_id": caller_tenant}` on every query, update, and delete.
- **Cross-Tenant Exploit Demonstration:** Live interactive simulation proving that omitting `tenant_id` from `update_task` allows an attacker tenant to overwrite other tenants' confidential data.
- **Database-Native Rate Limiting:** Sliding-window request counter directly in MongoDB (`saas_app.rate_limits`) rejecting requests exceeding 10 req / 60s without requiring external Redis infrastructure.
- **Multi-Tenant Architecture Comparison:** Tradeoffs between Document `tenant_id`, Collection-per-Tenant, and Database-per-Tenant models.

### Activity 2 — Data Migration Between Tenant Isolation Strategies (`lab_02_tenant_migration.py`)
- **Tier Escalation:** Moving enterprise tenants from shared collections (`saas_app.tasks`) to dedicated databases (`tenant_<id>.tasks`).
- **Safe Dry-Run Mode (`--dry-run`):** Audits source collection cardinality, target namespace, and payload structure with zero writes.
- **Idempotency Guarantee:** Upsert keyed on natural identifiers `(tenant_id, title)` ensures re-running the migration converges cleanly to the identical document count without duplicating records.
- **Dual Verification:** Automated document count matching and SHA-256 content checksum verification.
- **Zero-Risk Rollback (`--rollback`):** Follows the Copy-Verify-Deprecate pattern. Rollback simply drops `tenant_<id>`, leaving the shared collection 100% intact.

## Build and Push from Source

```bash
# Navigate to the Lab 15 directory
cd "c:\Users\Prajwal\OneDrive\Desktop\NoSQL LAB 15"

# Run the automated build and push batch script
.\build_and_push.bat
```

Or manually:

```bash
docker build -t meghanakasireddy/nosql-lab15:latest .
docker push meghanakasireddy/nosql-lab15:latest
```

## Stop & Remove Container

```bash
docker stop nosql-lab15 && docker rm nosql-lab15
```
