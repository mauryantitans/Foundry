# Foundry - AI-Powered Dataset Creation
# Docker image for containerized execution

# Use official Python runtime as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR $APP_HOME

# Install system dependencies for Pillow and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    tcl-dev \
    tk-dev \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary data directories with proper permissions
RUN mkdir -p data/raw data/curated data/output data/debug && \
    chmod -R 755 data

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser $APP_HOME

# Switch to non-root user
USER appuser

# Health check (optional - checks if Python can import main modules)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import google.generativeai; import PIL; print('OK')" || exit 1

# Expose port for future web UI
EXPOSE 8080

# Set default entrypoint
ENTRYPOINT ["python", "pipeline.py"]

# Default command (shows help)
CMD ["--help"]
