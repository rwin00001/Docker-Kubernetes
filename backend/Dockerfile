FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including wait-for-it
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a non-root user for security
RUN useradd -m -u 1000 user && chown -R user:user /app
USER user

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use wait script before starting the application
CMD ["sh", "-c", "python /app/wait_for_db.py && gunicorn app:app -b 0.0.0.0:8000 --workers 4 --threads 2"]
