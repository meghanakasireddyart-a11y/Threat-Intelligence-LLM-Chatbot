# ==============================================================================
# Dockerfile for NoSQL Lab 11 Demonstration Image
# Student: Kasireddy Meghana (24BTRCL119)
# Course: NoSQL Databases Using MongoDB
# Docker Hub Image: kasireddymeghana/nosql-lab11:latest
# ==============================================================================

FROM python:3.11-slim

LABEL maintainer="Kasireddy Meghana <24BTRCL119>"
LABEL description="MongoDB Lab 11 Sharding, Shard Key Evaluation & Hotspot Detection Demonstration"
LABEL version="1.0"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8011
ENV MONGO_URI=mongodb://host.docker.internal:27017

WORKDIR /app

# Install system utilities and curl for health check
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    iputils-ping \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install --no-cache-dir "pymongo>=4.0.0" rich reportlab python-docx pillow

# Copy lab application files
COPY . /app/

EXPOSE 8011

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8011/api/status || exit 1

# Start the interactive web platform on port 8011
CMD ["python", "website/server.py", "8011"]
