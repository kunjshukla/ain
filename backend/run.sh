#!/bin/bash
set -e

# Check if .env exists, if not create from template
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "Please edit the .env file with your configuration and run this script again."
    exit 1
fi

# Stop and remove any existing container
echo "Stopping and removing any existing container..."
docker rm -f ai-ninjacoach-backend 2>/dev/null || true

# Build the Docker image
echo "Building Docker image..."
docker build -t ai-ninjacoach-backend .

# Create the database directory if it doesn't exist
mkdir -p database

# Run the container with environment variables
echo "Starting container..."
docker run -d \
    --name ai-ninjacoach-backend \
    -p 8000:8000 \
    --env-file .env \
    -e GOOGLE_API_KEY="$GOOGLE_API_KEY" \
    -e GOOGLE_CLOUD_PROJECT_ID="$GOOGLE_CLOUD_PROJECT_ID" \
    -e GOOGLE_CLOUD_LOCATION="$GOOGLE_CLOUD_LOCATION" \
    -v $(pwd)/database:/app/database \
    ai-ninjacoach-backend

echo "Container started. You can access the API at http://localhost:8000"
echo "To view logs: docker logs -f ai-ninjacoach-backend"
echo "To stop the container: docker stop ai-ninjacoach-backend"
