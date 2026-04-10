FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Fix: Use shell form to expand $PORT environment variable
CMD gunicorn app:app --bind 0.0.0.0:${PORT:-5000}
