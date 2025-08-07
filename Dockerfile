# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Set a writable directory for Hugging Face to cache models
ENV HF_HOME=/tmp/huggingface_cache
ENV TRANSFORMERS_CACHE=/tmp/huggingface_cache
ENV HUGGINGFACE_HUB_CACHE=/tmp/huggingface_cache

# Copy the requirements file into the container's working directory
COPY ./requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of your application code to the container's working directory
COPY . .

# Expose the port that Hugging Face Spaces uses
EXPOSE 7860

# Define the command to run your app using gunicorn
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:7860", "api:app"]
