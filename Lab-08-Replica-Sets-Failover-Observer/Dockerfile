FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8008

RUN pip install --no-cache-dir pymongo

COPY . /app/

EXPOSE 8008

CMD ["python", "-u", "website/server.py"]
