#!/bin/bash

# Set default port if not specified
export PORT=${PORT:-8000}

# Ensure PORT is an integer
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "Error: PORT must be a number" >&2
    exit 1
fi

# Start the application
echo "Starting application on port $PORT"
uvicorn main:app --host 0.0.0.0 --port $PORT