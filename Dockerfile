# Threat Intelligence Web Application & Vulnerability Mitigator Platform
FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy and install core runtime Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pymongo mongomock numpy python-dotenv requests reportlab

# Copy application source files
COPY web_ui.py /app/
COPY threat_data.py /app/
COPY scanner_bot.py /app/
COPY demo_exercises_1_to_18.py /app/
COPY index.html /app/
COPY test.txt /app/

# Expose web server port
EXPOSE 5000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/status || exit 1

# Launch server
CMD ["python", "-u", "web_ui.py"]
