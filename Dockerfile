# ==========================================
# ForenSync Academy: IELTS & Cyber Prep
# Production Dockerfile for Oracle Cloud (OCI)
# ==========================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install minimal OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure audio cache directory exists
RUN mkdir -p /app/static/audio

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/exam-data/cyber || exit 1

# Start FastAPI production server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
