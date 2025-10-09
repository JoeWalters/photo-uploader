FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY photo_uploader.py .
COPY templates/ templates/
COPY static/ static/

# Create version file with build timestamp
ARG BUILD_DATE
RUN echo "${BUILD_DATE:-unknown}" > /app/version.txt

# Create directories for mounted volumes
RUN mkdir -p /app/config /app/uploads

# Create non-root user for security
RUN groupadd -r photoapp && useradd -r -g photoapp photoapp
RUN chown -R photoapp:photoapp /app

# Switch to non-root user
USER photoapp

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001', timeout=5)" || exit 1

# Default command
CMD ["python", "photo_uploader.py"]