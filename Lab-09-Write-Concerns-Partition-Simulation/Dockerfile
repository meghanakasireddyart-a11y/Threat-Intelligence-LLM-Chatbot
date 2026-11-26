# ==============================================================================
# Dockerfile for NoSQL Lab 9 Demonstration Image
# Student: Kasireddy Meghana (24BTRCL119)
# Course: NoSQL Databases Using MongoDB
# Docker Hub Image: kasireddymeghana/nosql-lab09:latest
# ==============================================================================

FROM python:3.11-slim

LABEL maintainer="Kasireddy Meghana <24BTRCL119>"
LABEL description="MongoDB Lab 9 CAP Theorem, Write Concerns & Network Partition Demonstration"
LABEL version="1.0"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8009

WORKDIR /app

# Install system utilities and MongoDB shell tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    iputils-ping \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

EXPOSE 8009

# Entrypoint script starts the interactive web portal and demonstration service
CMD ["python", "website/server.py"]
