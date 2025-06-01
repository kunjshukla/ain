#!/bin/bash

# Debug: Show environment
echo "Environment variables:"
printenv

# Get port from Railway's PORT or default to 8000
ACTUAL_PORT=$(printenv PORT || echo 8000)

# Force numeric port
ACTUAL_PORT=$((ACTUAL_PORT + 0))
[ "$ACTUAL_PORT" -gt 0 ] 2>/dev/null || ACTUAL_PORT=8000

# Debug: Show final port
echo "Using port: $ACTUAL_PORT"

# Start the app directly with the numeric port
exec uvicorn main:app --host 0.0.0.0 --port $ACTUAL_PORT