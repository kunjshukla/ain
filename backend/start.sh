#!/bin/bash

# Set default port if not specified
PORT=${PORT:-8000}

# Force PORT to be a number (default to 8000 if invalid)
PORT=$((PORT + 0))
PORT=${PORT:-8000}

# Start the application
echo "Starting application on port $PORT"
exec uvicorn main:app --host 0.0.0.0 --port $PORT