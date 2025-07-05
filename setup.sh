#!/bin/bash

# Autonoma AI Webapp Creator - Setup Script
# This script sets up the modern fullstack AI webapp creator

set -e

echo "🚀 Setting up Autonoma AI Webapp Creator..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/"
        exit 1
    fi
    
    # Check if Node.js version is 18+
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js version 18+ required. Current version: $(node -v)"
        exit 1
    fi
    
    # Check pnpm
    if ! command -v pnpm &> /dev/null; then
        print_warning "pnpm not found. Installing pnpm..."
        npm install -g pnpm
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3.8+ is required. Please install Python from https://python.org/"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_warning "Docker not found. You can still run without Docker, but some features may not work."
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_warning "Docker Compose not found. Some deployment features may not work."
    fi
    
    print_success "System requirements check completed"
}

# Create environment files
setup_environment() {
    print_status "Setting up environment configuration..."
    
    # Backend environment
    if [ ! -f "backend/.env" ]; then
        cat > backend/.env << EOF
# Database
DATABASE_URL=postgresql://autonoma:autonoma123@localhost:5432/autonoma_db

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Services
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
PINECONE_API_KEY=your-pinecone-api-key-here

# Security
SECRET_KEY=your-super-secret-key-change-in-production

# MCP Server
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8001

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Development
ENVIRONMENT=development
DEBUG=true
EOF
        print_success "Created backend/.env"
    else
        print_warning "backend/.env already exists, skipping..."
    fi
    
    # Frontend environment
    if [ ! -f "frontend-nextjs/.env.local" ]; then
        cat > frontend-nextjs/.env.local << EOF
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# AI Features
NEXT_PUBLIC_ENABLE_AI_CHAT=true
NEXT_PUBLIC_ENABLE_REALTIME_PREVIEW=true

# Web3 Configuration (optional)
NEXT_PUBLIC_ENABLE_WEB3=false
NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID=your-wallet-connect-project-id

# Analytics (optional)
NEXT_PUBLIC_POSTHOG_KEY=your-posthog-key
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn

# Development
NODE_ENV=development
EOF
        print_success "Created frontend-nextjs/.env.local"
    else
        print_warning "frontend-nextjs/.env.local already exists, skipping..."
    fi
    
    # Docker environment
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# AI API Keys (required)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
PINECONE_API_KEY=your-pinecone-api-key-here

# Security
SECRET_KEY=your-super-secret-key-change-in-production

# Database
POSTGRES_USER=autonoma
POSTGRES_PASSWORD=autonoma123
POSTGRES_DB=autonoma_db

# Environment
ENVIRONMENT=development
EOF
        print_success "Created .env for Docker"
    else
        print_warning ".env already exists, skipping..."
    fi
}

# Install backend dependencies
setup_backend() {
    print_status "Setting up Python backend..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    print_success "Backend setup completed"
    cd ..
}

# Install frontend dependencies
setup_frontend() {
    print_status "Setting up Next.js frontend..."
    
    cd frontend-nextjs
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    pnpm install
    
    print_success "Frontend setup completed"
    cd ..
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p generated_projects
    mkdir -p logs
    mkdir -p uploads
    mkdir -p nginx/ssl
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    
    print_success "Directories created"
}

# Setup database (if running locally)
setup_database() {
    print_status "Setting up database..."
    
    # Check if PostgreSQL is running locally
    if command -v psql &> /dev/null; then
        print_status "PostgreSQL found locally. Setting up database..."
        
        # Create database if it doesn't exist
        createdb autonoma_db 2>/dev/null || true
        
        # Run migrations
        cd backend
        source venv/bin/activate
        alembic upgrade head
        cd ..
        
        print_success "Database setup completed"
    else
        print_warning "PostgreSQL not found locally. Use Docker or install PostgreSQL manually."
    fi
}

# Start services
start_services() {
    print_status "Starting development services..."
    
    # Check if user wants to use Docker
    read -p "Start services with Docker? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v docker-compose &> /dev/null; then
            docker-compose up -d postgres redis chromadb
            print_success "Docker services started"
        elif docker compose version &> /dev/null; then
            docker compose up -d postgres redis chromadb
            print_success "Docker services started"
        else
            print_error "Docker Compose not available"
            exit 1
        fi
    else
        print_warning "Make sure PostgreSQL and Redis are running locally"
    fi
}

# Create development start script
create_dev_script() {
    print_status "Creating development start script..."
    
    cat > start-dev.sh << 'EOF'
#!/bin/bash

# Start Autonoma in development mode

echo "🚀 Starting Autonoma AI Webapp Creator..."

# Start backend
echo "Starting FastAPI backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start MCP server
echo "Starting MCP server..."
python -m app.mcp_servers.webapp_creator_server &
MCP_PID=$!

cd ..

# Start frontend
echo "Starting Next.js frontend..."
cd frontend-nextjs
pnpm dev &
FRONTEND_PID=$!

cd ..

echo "✅ All services started!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🤖 MCP Server: http://localhost:8001"

# Wait for services
wait $BACKEND_PID $FRONTEND_PID $MCP_PID
EOF
    
    chmod +x start-dev.sh
    print_success "Created start-dev.sh script"
}

# Main setup function
main() {
    echo "🎯 Autonoma AI Webapp Creator Setup"
    echo "===================================="
    echo
    
    check_requirements
    echo
    
    setup_environment
    echo
    
    create_directories
    echo
    
    setup_backend
    echo
    
    setup_frontend
    echo
    
    create_dev_script
    echo
    
    # Optional database setup
    read -p "Setup local database? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_database
        echo
    fi
    
    # Optional Docker services
    read -p "Start Docker services? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_services
        echo
    fi
    
    print_success "🎉 Setup completed successfully!"
    echo
    echo "📋 Next steps:"
    echo "1. Configure your AI API keys in the .env files"
    echo "2. Run './start-dev.sh' to start all services"
    echo "3. Visit http://localhost:3000 to start creating apps!"
    echo
    echo "� What you can create:"
    echo "• Full-stack web applications (Next.js + FastAPI)"
    echo "• Chrome browser extensions (all types)"
    echo "• Web3 decentralized applications"
    echo "• Real-time applications with WebSockets"
    echo "• AI-powered applications with agent coordination"
    echo
    echo "�📖 Documentation: https://github.com/your-org/autonoma"
    echo "💬 Support: https://discord.gg/autonoma"
}

# Run main function
main "$@"