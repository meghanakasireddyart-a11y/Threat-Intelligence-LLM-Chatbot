# NoSQL Lab 15: Multi-Tenant Architecture & Data Migration Strategies
# Self-contained interactive website image
# Maintainer: kasireddymeghana / meghanakasireddy

FROM python:3.11-slim

LABEL maintainer="kasireddymeghana"
LABEL description="NoSQL Lab 15 - Multi-Tenant SaaS Architecture & Tenant Migration Strategies"
LABEL version="1.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir pymongo bson rich

# Copy Lab 15 core scripts and components
COPY lab_01_multitenant_api.py ./
COPY lab_02_tenant_migration.py ./
COPY config/ ./config/
COPY website/ ./website/

# Expose the web server port
EXPOSE 8000

# Start the web server
CMD ["python", "website/server.py", "8000"]
