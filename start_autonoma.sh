#!/bin/bash

# Autonoma App Startup Script
# Ensures all services start correctly and the Chrome Extension Generator is ready

set -e

echo "🚀 Starting Autonoma Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required directories exist
check_directories() {
    print_status "Checking project structure..."
    
    if [ ! -d "backend" ]; then
        print_error "Backend directory not found!"
        exit 1
    fi
    
    if [ ! -d "frontend-nextjs" ]; then
        print_error "Frontend directory not found!"
        exit 1
    fi
    
    print_status "✅ Project structure verified"
}

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found! Please install Python 3.8+"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js not found! Please install Node.js 18+"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm not found! Please install npm"
        exit 1
    fi
    
    print_status "✅ Dependencies verified"
}

# Setup Python environment
setup_backend() {
    print_status "Setting up backend environment..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    cd ..
    print_status "✅ Backend environment ready"
}

# Setup frontend dependencies
setup_frontend() {
    print_status "Setting up frontend environment..."
    
    cd frontend-nextjs
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    cd ..
    print_status "✅ Frontend environment ready"
}

# Start backend server
start_backend() {
    print_status "Starting backend server..."
    
    cd backend
    source venv/bin/activate
    
    # Start the backend server in background
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    cd ..
    
    # Wait for backend to start
    print_status "Waiting for backend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
            print_status "✅ Backend server started (PID: $BACKEND_PID)"
            return 0
        fi
        sleep 1
    done
    
    print_error "Backend server failed to start!"
    exit 1
}

# Start frontend server
start_frontend() {
    print_status "Starting frontend server..."
    
    cd frontend-nextjs
    
    # Start the frontend server in background
    npm run dev &
    FRONTEND_PID=$!
    
    cd ..
    
    # Wait for frontend to start
    print_status "Waiting for frontend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            print_status "✅ Frontend server started (PID: $FRONTEND_PID)"
            return 0
        fi
        sleep 1
    done
    
    print_error "Frontend server failed to start!"
    exit 1
}

# Health checks
run_health_checks() {
    print_status "Running health checks..."
    
    # Check main API health
    if curl -s http://localhost:8000/api/health | grep -q "healthy"; then
        print_status "✅ Main API health check passed"
    else
        print_warning "⚠️  Main API health check failed"
    fi
    
    # Check Chrome Extension API health
    if curl -s http://localhost:8000/api/chrome-extension/health | grep -q "healthy"; then
        print_status "✅ Chrome Extension API health check passed"
    else
        print_warning "⚠️  Chrome Extension API health check failed"
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_status "✅ Frontend health check passed"
    else
        print_warning "⚠️  Frontend health check failed"
    fi
}

# Display startup summary
display_summary() {
    echo ""
    echo "🎉 Autonoma Application Started Successfully!"
    echo ""
    echo "📊 Service Status:"
    echo "  • Backend API: http://localhost:8000"
    echo "  • Frontend App: http://localhost:3000"
    echo "  • API Docs: http://localhost:8000/docs"
    echo ""
    echo "🔧 Chrome Extension Generator:"
    echo "  • Navigate to: http://localhost:3000"
    echo "  • Click on 'Chrome Extension' tab"
    echo "  • Follow the 3-step process to create extensions"
    echo ""
    echo "🛠️  Debug Tools:"
    echo "  • Health Check: http://localhost:8000/api/health"
    echo "  • Extension API: http://localhost:8000/api/chrome-extension/health"
    echo "  • Browser Console: debug.checkBackendHealth()"
    echo ""
    echo "📋 Process IDs:"
    echo "  • Backend PID: $BACKEND_PID"
    echo "  • Frontend PID: $FRONTEND_PID"
    echo ""
    echo "🛑 To stop the application:"
    echo "  • Press Ctrl+C or run: ./stop_autonoma.sh"
    echo ""
}

# Cleanup function
cleanup() {
    print_status "Shutting down services..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_status "Backend server stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_status "Frontend server stopped"
    fi
    
    print_status "Autonoma application stopped"
}

# Set up trap for cleanup
trap cleanup EXIT

# Main execution
main() {
    echo "🚀 Autonoma Application Startup"
    echo "================================"
    
    check_directories
    check_dependencies
    
    # Setup environments (only if --setup flag is passed)
    if [ "$1" = "--setup" ]; then
        setup_backend
        setup_frontend
    fi
    
    start_backend
    start_frontend
    
    # Give services time to fully start
    sleep 3
    
    run_health_checks
    display_summary
    
    # Keep the script running
    print_status "Application is running. Press Ctrl+C to stop."
    
    # Wait for user interrupt
    while true; do
        sleep 1
    done
}

# Run main function
main "$@"