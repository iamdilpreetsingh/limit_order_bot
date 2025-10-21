# ========================================
# Titan Trading Bot - Dockerfile
# ========================================
# This creates a Docker image for the limit order trading bot

# Start from official Python 3.13 slim image
# "slim" = smaller size, includes only essentials
FROM python:3.13-slim

# Set metadata labels
LABEL maintainer="dilpreetsingh3682@gmail.com"
LABEL description="Ethereum Limit Order Trading Bot with Titan Builder"
LABEL version="1.0"

# Set working directory inside container
# All commands will run from /app
WORKDIR /app

# Install build dependencies needed for some Python packages
# gcc, g++, make = compile C code
# These will be removed after installation to keep image small
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first (Docker layer optimization)
# By copying requirements.txt separately, Docker can cache this layer
# If requirements don't change, Docker won't reinstall packages
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir = don't store pip cache (reduces image size)
RUN pip install --no-cache-dir -r requirements.txt

# Remove build dependencies to reduce image size
# Runtime doesn't need these tools
RUN apt-get purge -y --auto-remove gcc g++ make

# Copy the main trading script
COPY limit_order_script.py .

# Create a directory for configs (will be mounted as volume)
RUN mkdir -p /app/configs

# Set environment variables (can be overridden at runtime)
ENV PYTHONUNBUFFERED=1
# ^ This ensures Python output is immediately visible in docker logs

# Default command: run the trading bot
# Note: CONFIG_FILE will be set via docker-compose for each container
CMD ["python", "-u", "limit_order_script.py"]

# Health check (optional but recommended)
# Docker will periodically check if the container is healthy
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#   CMD python -c "import sys; sys.exit(0)" || exit 1

