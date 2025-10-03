# ./api/Dockerfile
FROM python:3.10-slim

# Install system deps needed for building some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    libhdf5-dev\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency file first for caching
COPY api/requirements.txt /app/requirements.txt

# Upgrade pip + add longer timeout for heavy packages like TensorFlow
RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir --default-timeout=100 -r /app/requirements.txt

# Copy application code
COPY api/ /app/

# Env + expose
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]