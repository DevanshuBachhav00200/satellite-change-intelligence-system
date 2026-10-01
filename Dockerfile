# Production Dockerfile for Satellite Change Intelligence Backend
FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffer outputs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8000

WORKDIR /app

# Install system dependencies required for OpenCV and Matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies file first for caching
COPY requirements.txt /app/requirements.txt

# Install PyTorch CPU-only build for lightweight deployment & Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY backend /app/backend
COPY models /app/models
COPY analysis /app/analysis
COPY misc /app/misc
COPY data_config.py /app/data_config.py
COPY utils.py /app/utils.py

# Create checkpoints directory mountpoint
RUN mkdir -p /app/checkpoints/ChangeFormer_LEVIR

EXPOSE 8000

# Healthcheck endpoint check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Start FastAPI backend with Uvicorn
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
