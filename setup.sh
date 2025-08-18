#!/bin/bash

# Research-to-Insights Agent Setup Script
# This script helps set up the development environment

set -e

echo "🚀 Setting up Research-to-Insights Agent..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.9+"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_success "Python $python_version found"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+"
        exit 1
    fi
    
    node_version=$(node --version)
    print_success "Node.js $node_version found"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    fi
    
    npm_version=$(npm --version)
    print_success "npm $npm_version found"
    
    # Check Git
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        exit 1
    fi
    
    git_version=$(git --version | cut -d' ' -f3)
    print_success "Git $git_version found"
}

# Setup Python environment
setup_python() {
    print_status "Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    pip install -r backend/requirements.txt
    
    print_success "Python environment setup complete"
}

# Setup Node.js environment
setup_node() {
    print_status "Setting up Node.js environment..."
    
    # Install frontend dependencies
    print_status "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    
    print_success "Node.js environment setup complete"
}

# Setup environment variables
setup_env() {
    print_status "Setting up environment variables..."
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        cp env.example .env
        print_warning "Please edit .env file with your API keys and configuration"
    else
        print_success ".env file already exists"
    fi
}

# Setup Git hooks
setup_git() {
    print_status "Setting up Git configuration..."
    
    # Initialize Git if not already initialized
    if [ ! -d ".git" ]; then
        git init
        print_status "Git repository initialized"
    fi
    
    # Add pre-commit hook for Python formatting
    if [ ! -f ".git/hooks/pre-commit" ]; then
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for Python formatting

# Activate virtual environment
source venv/bin/activate

# Format Python code
echo "Formatting Python code..."
black backend/
isort backend/

# Check for linting issues
echo "Checking Python code..."
flake8 backend/
EOF
        chmod +x .git/hooks/pre-commit
        print_success "Git pre-commit hook installed"
    fi
}

# Create development scripts
create_scripts() {
    print_status "Creating development scripts..."
    
    # Create start-backend script
    cat > start-backend.sh << 'EOF'
#!/bin/bash
# Start the FastAPI backend server

cd backend
source ../venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
EOF
    chmod +x start-backend.sh
    
    # Create start-frontend script
    cat > start-frontend.sh << 'EOF'
#!/bin/bash
# Start the React frontend development server

cd frontend
npm run dev
EOF
    chmod +x start-frontend.sh
    
    # Create start-all script
    cat > start-all.sh << 'EOF'
#!/bin/bash
# Start both backend and frontend servers

# Start backend in background
./start-backend.sh &
BACKEND_PID=$!

# Start frontend in background
./start-frontend.sh &
FRONTEND_PID=$!

echo "Backend started with PID: $BACKEND_PID"
echo "Frontend started with PID: $FRONTEND_PID"
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF
    chmod +x start-all.sh
    
    print_success "Development scripts created"
}

# Main setup function
main() {
    print_status "Starting Research-to-Insights Agent setup..."
    
    check_requirements
    setup_python
    setup_node
    setup_env
    setup_git
    create_scripts
    
    print_success "Setup complete! 🎉"
    echo ""
    print_status "Next steps:"
    echo "1. Edit .env file with your API keys"
    echo "2. Create a Supabase project and run the database migration"
    echo "3. Run './start-backend.sh' to start the backend server"
    echo "4. Run './start-frontend.sh' to start the frontend server"
    echo "5. Or run './start-all.sh' to start both servers"
    echo ""
    print_status "For detailed setup instructions, see the README.md file"
}

# Run main function
main "$@"
