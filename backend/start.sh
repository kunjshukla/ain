#!/bin/sh
# Debug: Print the PORT value
echo "PORT is set to: $PORT"
# Use a default port if $PORT is not set
PORT=${PORT:-8000}
echo "Using PORT: $PORT"
exec uvicorn main:app --host 0.0.0.0 --port $PORT