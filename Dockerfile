# Dockerfile for Railway Deployment

# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Set all known Hugging Face cache variables to a single writable directory (/tmp)
# This is our robust fix for the 'Permission denied' error.
ENV HF_HOME=/tmp/huggingface_cache
ENV HUGGINGFACE_HUB_CACHE=/tmp/huggingface_cache
ENV TRANSFORMERS_CACHE=/tmp/huggingface_cache

# Copy the requirements file into the container
COPY ./requirements.txt .

# Install packages
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of your application code
COPY . .

# --- Railway Specific Part ---
# The CMD instruction uses the $PORT variable that Railway provides automatically.
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:${PORT}", "api:app"]
