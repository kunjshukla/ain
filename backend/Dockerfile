# Use the official Python 3.10 image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    python3-dev \
    libssl-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port (Railway assigns the port via $PORT)
EXPOSE 8000

# Set environment variable with default value
ENV PORT=8000

# Use shell form to ensure environment variable substitution
RUN chmod +x start.sh
CMD ["./start.sh"]