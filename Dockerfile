FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY scraper/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy scraper code
COPY scraper/ /app/scraper/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create data directories
RUN mkdir -p /app/data /app/scraper/raw_data /app/scraper/normalized_data

# Default command
CMD ["python", "-m", "scraper.cli", "--help"]
