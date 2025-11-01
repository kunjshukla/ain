#!/bin/bash

echo "🚀 Starting AI NinjaCoach Platform"
echo "=================================="
echo ""

# Change to project root
cd "$(dirname "$0")"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    pkill -f "uvicorn main:socket_app"
    pkill -f "http.server 8501"
    echo "✅ All services stopped"
    exit 0
}

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "❌ Error: backend directory not found"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo "❌ Error: frontend directory not found"
    exit 1
fi

echo "📦 Starting Backend Server..."
cd backend
nohup python -m uvicorn main:socket_app --host 0.0.0.0 --port 8000 > backend_server.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Backend started (PID: $BACKEND_PID)"
else
    echo "❌ Backend failed to start. Check backend/backend_server.log"
    exit 1
fi

echo ""
echo "🌐 Starting Frontend Server..."
cd frontend
nohup python3 -m http.server 8501 > frontend_server.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "⏳ Waiting for frontend to start..."
sleep 2

# Check if frontend is running
if ps -p $FRONTEND_PID > /dev/null; then
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
else
    echo "❌ Frontend failed to start. Check frontend/frontend_server.log"
    kill $BACKEND_PID
    exit 1
fi

echo ""
echo "=================================="
echo "✨ AI NinjaCoach is now running!"
echo "=================================="
echo ""
echo "🔗 Access Points:"
echo "   Frontend:  http://localhost:8501"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📱 Voice Interview:"
echo "   http://localhost:8501/voice_interview.html"
echo ""
echo "🔧 Services:"
echo "   - Backend PID:  $BACKEND_PID"
echo "   - Frontend PID: $FRONTEND_PID"
echo ""
echo "📊 Logs:"
echo "   - Backend:  backend/backend_server.log"
echo "   - Frontend: frontend/frontend_server.log"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=================================="
echo ""

# Keep script running and monitor processes
while true; do
    # Check if backend is still running
    if ! ps -p $BACKEND_PID > /dev/null; then
        echo "❌ Backend stopped unexpectedly"
        cleanup
    fi
    
    # Check if frontend is still running
    if ! ps -p $FRONTEND_PID > /dev/null; then
        echo "❌ Frontend stopped unexpectedly"
        cleanup
    fi
    
    sleep 5
done
