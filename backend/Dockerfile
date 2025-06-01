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

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Ensure line endings are correct and make executable
RUN sed -i 's/\r$//' start.sh && chmod +x start.sh

# Use the start script
CMD ["./start.sh"]