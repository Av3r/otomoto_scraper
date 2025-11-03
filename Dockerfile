# Dockerfile for otomoto_scraper
# Build: docker build -t otomoto-scraper .
# Run:   docker run --rm -v $(pwd)/data:/app/data otomoto-scraper

FROM python:3.13-slim

# Metadata
LABEL maintainer="Otomoto Scraper <your@example.com>"
LABEL description="Web scraper for Otomoto car listings"

# Set working directory
WORKDIR /app

# Copy only requirements first for better layer caching
COPY requirements.txt .

# Install dependencies
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ ./src/
COPY tests/ ./tests/
COPY pytest.ini ./
COPY .env* ./

# Create data directory for output
RUN mkdir -p /app/data

# Set environment variables (can be overridden at runtime)
ENV PYTHONUNBUFFERED=1
ENV OTOMOTO_URL="https://www.otomoto.pl/osobowe/bmw/seria-5"

# Default command: run the scraper
CMD ["python", "-m", "src.scraper.main"]
