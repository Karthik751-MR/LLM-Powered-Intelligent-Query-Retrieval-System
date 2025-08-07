# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file into the container at /code
COPY ./requirements.txt /code/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of your application code to the container
COPY . /code/

# Expose the port that Hugging Face Spaces uses
EXPOSE 7860

# Define the command to run your app using gunicorn
# The --host 0.0.0.0 and --port 7860 flags are important for Hugging Face
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:7860", "api:app"]
