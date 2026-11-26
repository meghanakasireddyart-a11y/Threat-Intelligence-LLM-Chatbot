# Lab 13: Production Replica Set & Kubernetes StatefulSet
# Builds a self-contained interactive website image
# Build context: NoSQL LAB 13 directory
# Requires website/ and config/ to be copied from Lab 7 first (see build_and_push.bat)

FROM python:3.11-slim

LABEL maintainer="kasireddymeghana"
LABEL description="NoSQL Lab 13 - Production Replica Set with keyFile Auth & K8s StatefulSet"
LABEL version="1.0"

WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir pymongo bson

# Copy Lab 13 specific files
COPY k8s/ ./k8s/
COPY lab_01_deploy_prod.sh ./
COPY lab_02_k8s_statefulset.py ./
COPY main.tf ./
COPY docker-compose-production.yml ./

# Copy Lab 7 website (with Lab 13 tab) and shared config
# These must be present in the build context (see build_and_push.bat)
COPY website/ ./website/
COPY config/ ./config/

# Expose the web server port
EXPOSE 8000

# Start the web server
CMD ["python", "website/server.py", "8000"]
