# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed by Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir makes the image smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code
COPY . .

# Add the Gunicorn server dependency
RUN pip install gunicorn

# Expose the port the app runs on
EXPOSE 8000

# Run the app. We use gunicorn as a production-ready WSGI server.
# The --bind 0.0.0.0:8000 makes the server accessible from outside the container.
# "app:create_app()" tells gunicorn to look for a callable named create_app in a file named app.py.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:create_app()"] 