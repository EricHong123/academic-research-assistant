FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy application code
COPY src/ ./src/
COPY main.py .
COPY celery_worker.py .

# Create upload directories
RUN mkdir -p /app/uploads /app/storage/pdfs

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
