# NoSQL Lab 16: Polyglot Persistence & Hybrid Query Services
# Self-contained interactive website image
# Maintainer: kasireddymeghana / meghanakasireddy

FROM python:3.11-slim

LABEL maintainer="kasireddymeghana"
LABEL description="NoSQL Lab 16 - Polyglot Persistence & Hybrid Query Service (MongoDB + Cassandra + Neo4j)"
LABEL version="1.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir pymongo bson rich neo4j

# Copy Lab 16 core scripts and components
COPY lab_01_polyglot_modeling.py ./
COPY lab_02_hybrid_query_service.py ./
COPY config/ ./config/
COPY website/ ./website/

# Expose the web server port
EXPOSE 8000

# Start the web server
CMD ["python", "website/server.py", "8000"]
