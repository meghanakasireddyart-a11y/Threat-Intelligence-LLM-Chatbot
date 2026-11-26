# ==============================================================================
# Dockerfile for NoSQL Lab 12 Demonstration Image
# Student: Kasireddy Meghana (24BTRCL119)
# Course: NoSQL Databases Using MongoDB
# Chapter: Chapter 12 - Database Security, RBAC & TLS Encryption
# Docker Hub Image: kasireddymeghana/nosql-lab12:latest
# ==============================================================================

FROM python:3.11-slim

LABEL maintainer="Kasireddy Meghana <24BTRCL119>"
LABEL description="MongoDB Lab 12 Authentication, RBAC, Field Redaction & TLS Demonstration"
LABEL version="1.0"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8012
ENV MONGO_URI=mongodb://host.docker.internal:27017

WORKDIR /app

# Install system utilities, openssl for certificate generation, and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssl \
    curl \
    iputils-ping \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install --no-cache-dir "pymongo>=4.0.0" rich reportlab python-docx pillow

# Copy lab application files
COPY . /app/

# Generate TLS certificates inside the container if not already present
RUN python lab_02_tls_setup.py || true

EXPOSE 8012

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8012/api/status || exit 1

# Start the interactive web platform on port 8012
CMD ["python", "website/server.py", "8012"]
