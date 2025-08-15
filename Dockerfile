# Use an official Python runtime as the base image
FROM python:3.11-slim

# Create and set the working directory inside the container
WORKDIR /app

# Copy dependency file(s) first for better caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose the port your app listens on (adjust if needed)
EXPOSE 5000

# Default command to run your app (adjust as necessary)
CMD ["python", "app.py"]

