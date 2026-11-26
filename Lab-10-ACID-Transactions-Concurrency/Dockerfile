FROM python:3.11-slim

LABEL maintainer="Kasireddy Meghana <24BTRCL119@jainuniversity.ac.in>"
LABEL description="NoSQL Lab 10: ACID Transactions with MongoDB"
LABEL version="1.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir pymongo==4.7.3

# Copy lab files
COPY . /app/

# Expose the web server port
EXPOSE 8010

# Environment variables
ENV MONGO_URI=mongodb://host.docker.internal:27017
ENV PORT=8010
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8010/api/status || exit 1

# Start the web server
CMD ["python", "website/server.py", "8010"]
