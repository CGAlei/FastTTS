# FastTTS Docker Container
# Multi-stage build for production-ready Chinese TTS with MFA support

# ================================================
# Stage 1: Base System with MFA Dependencies
# ================================================
FROM continuumio/miniconda3:latest as base

# Set working directory
WORKDIR /app

# Install system dependencies for MFA and audio processing
RUN apt-get update && apt-get install -y \
    # Audio processing tools
    ffmpeg \
    sox \
    # Build tools for compilation
    build-essential \
    cmake \
    # System utilities
    wget \
    curl \
    git \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create conda environment for FastTTS with MFA
COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml -n fasttts-mfa \
    && conda clean -afy

# Activate conda environment for subsequent commands
SHELL ["conda", "run", "-n", "fasttts-mfa", "/bin/bash", "-c"]

# ================================================
# Stage 2: Application Setup
# ================================================
FROM base as app

# Copy application code
COPY . /app/

# Install Python dependencies
RUN conda run -n fasttts-mfa pip install -r requirements.txt

# Download MFA models (optional - can be done at runtime)
RUN conda run -n fasttts-mfa mfa model download acoustic mandarin_mfa || true
RUN conda run -n fasttts-mfa mfa model download dictionary mandarin_mfa || true

# Create necessary directories
RUN mkdir -p /app/db /app/sessions /app/logs

# Set correct permissions
RUN chmod +x /app/start_fasttts_mfa.sh || true

# ================================================
# Stage 3: Production Configuration
# ================================================
FROM app as production

# Create non-root user for security
RUN useradd -m -u 1000 fasttts && \
    chown -R fasttts:fasttts /app

# Switch to non-root user
USER fasttts

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Set environment variables
ENV PYTHONPATH=/app
ENV FASTTTS_HOST=0.0.0.0
ENV FASTTTS_PORT=5001
ENV FASTTTS_LOG_LEVEL=INFO

# Expose port
EXPOSE 5001

# Create volume mount points for persistent data
VOLUME ["/app/db", "/app/sessions", "/app/logs"]

# Entry point
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "fasttts-mfa"]
CMD ["python", "main.py"]

# ================================================
# Build Labels (Docker metadata)
# ================================================
LABEL maintainer="CGAlei <serinoac@gmail.com>"
LABEL version="1.0.0"
LABEL description="FastTTS - Advanced Chinese Text-to-Speech with AI Vocabulary Learning"
LABEL org.opencontainers.image.title="FastTTS"
LABEL org.opencontainers.image.description="Chinese TTS with karaoke-style learning and AI vocabulary"
LABEL org.opencontainers.image.url="https://github.com/CGAlei/FastTTS"
LABEL org.opencontainers.image.source="https://github.com/CGAlei/FastTTS"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.created="2025-08-05"
LABEL org.opencontainers.image.revision=""
LABEL org.opencontainers.image.licenses="MIT"