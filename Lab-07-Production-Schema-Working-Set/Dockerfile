FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

RUN pip install --no-cache-dir pymongo

COPY . /app/

EXPOSE 8000

CMD ["python", "-u", "website/server.py", "8000"]
