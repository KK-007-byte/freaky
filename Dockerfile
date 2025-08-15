# Base image with Python 3.11
FROM python:3.11-slim

# Install C++ build tools
RUN apt-get update && apt-get install -y g++ && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency file first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your repo into the container
COPY . .

# Expose the port (adjust if needed)
EXPOSE 5000

# Run your main Python app
CMD ["python", "stocks_upgrade.py"]


