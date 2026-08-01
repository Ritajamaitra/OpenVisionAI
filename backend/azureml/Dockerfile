# Azure ML base image
FROM mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04

USER root

# Install Linux libraries required by OpenCV
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python -m pip install --upgrade pip

# Copy only requirements first (better Docker layer caching)
COPY src/requirements.txt /tmp/requirements.txt

# Install Python packages
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Set working directory
WORKDIR /app