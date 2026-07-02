FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY rcm_module.py .
COPY rcm_generator.py .

# Create output directory
RUN mkdir -p /app/output

# Default command
CMD ["python", "rcm_module.py", "--output-dir", "/app/output"]
