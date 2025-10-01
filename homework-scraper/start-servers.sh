#!/bin/bash
# Script to start both Django backend and Next.js frontend servers (Linux/Mac)

echo "🚀 Starting Homework Scraper Servers..."
echo ""

# Check if Python virtual environment exists
VENV_PATH="../../.venv"
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js first."
    exit 1
fi

echo "🔄 Stopping any existing servers..."
# Kill existing Node.js processes
pkill -f "next dev" 2>/dev/null

# Kill existing Django processes
pkill -f "manage.py runserver" 2>/dev/null

sleep 2

echo ""
echo "✅ Starting Django Backend (Port 8000)..."

# Start Django backend in background
cd backend
source "$VENV_PATH/bin/activate"
python manage.py runserver > ../logs/django.log 2>&1 &
DJANGO_PID=$!
echo "Django PID: $DJANGO_PID"
cd ..

sleep 3

echo "✅ Starting Next.js Frontend (Port 3000)..."

# Start Next.js frontend in background
cd frontend
npm run dev > ../logs/nextjs.log 2>&1 &
NEXTJS_PID=$!
echo "Next.js PID: $NEXTJS_PID"
cd ..

echo ""
echo "✅ Both servers are running!"
echo ""
echo "🌐 Django Backend:  http://127.0.0.1:8000"
echo "🌐 Next.js Frontend: http://localhost:3000"
echo ""
echo "📝 Server logs:"
echo "   Django:  logs/django.log"
echo "   Next.js: logs/nextjs.log"
echo ""
echo "🛑 To stop servers, run: kill $DJANGO_PID $NEXTJS_PID"
echo ""

# Save PIDs to file for easy stopping later
echo "DJANGO_PID=$DJANGO_PID" > .server-pids
echo "NEXTJS_PID=$NEXTJS_PID" >> .server-pids

echo "✅ Server PIDs saved to .server-pids"
