# NoSQL Lab 18: Comparative Capstone Lab & Technical Analysis Report
# Self-contained interactive website image
# Maintainer: kasireddymeghana / meghanakasireddy

FROM python:3.11-slim

LABEL maintainer="kasireddymeghana"
LABEL description="NoSQL Lab 18 - Comparative Capstone Lab (MongoDB vs Cassandra vs Neo4j Benchmark & Analysis Report)"
LABEL version="1.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir pymongo bson rich numpy

# Copy Lab 18 core scripts and components
COPY lab_01_comparative_capstone.py ./
COPY lab_02_comparative_report.py ./
COPY config/ ./config/
COPY website/ ./website/

# Expose the web server port
EXPOSE 8000

# Start the web server
CMD ["python", "website/server.py", "8000"]
