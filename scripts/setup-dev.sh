#!/usr/bin/env bash
# Luminote Development Environment Setup Script
# For Linux and macOS systems
# This script sets up the complete development environment for Luminote

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Compare version numbers
version_ge() {
    [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$2" ]
}

# Main setup process
main() {
    print_header "Luminote Development Environment Setup"
    
    # Step 1: Check prerequisites
    print_header "Step 1: Checking Prerequisites"
    
    # Check Python version
    if ! command_exists python3; then
        print_error "Python 3 is not installed"
        echo "Please install Python 3.12 or higher from https://www.python.org/downloads/"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_info "Found Python $PYTHON_VERSION"
    
    if ! version_ge "$PYTHON_VERSION" "3.12.0"; then
        print_error "Python 3.12+ is required, but found $PYTHON_VERSION"
        echo "Please upgrade Python from https://www.python.org/downloads/"
        exit 1
    fi
    print_success "Python version check passed"
    
    # Check Node.js version
    if ! command_exists node; then
        print_error "Node.js is not installed"
        echo "Please install Node.js 22+ from https://nodejs.org/"
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2)
    print_info "Found Node.js v$NODE_VERSION"
    
    if ! version_ge "$NODE_VERSION" "22.0.0"; then
        print_error "Node.js 22+ is required, but found v$NODE_VERSION"
        echo "Please upgrade Node.js from https://nodejs.org/"
        exit 1
    fi
    print_success "Node.js version check passed"
    
    # Check if npm is available
    if ! command_exists npm; then
        print_error "npm is not installed"
        echo "Please install npm (usually comes with Node.js)"
        exit 1
    fi
    print_success "npm is available"
    
    # Step 2: Backend setup
    print_header "Step 2: Setting Up Backend"
    
    cd backend || exit 1
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv .venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists, skipping creation"
    fi
    
    # Activate virtual environment
    print_info "Activating virtual environment..."
    # shellcheck disable=SC1091
    source .venv/bin/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    print_info "Upgrading pip..."
    python -m pip install --upgrade pip > /dev/null 2>&1
    print_success "pip upgraded"
    
    # Install backend dependencies
    print_info "Installing backend dependencies..."
    if [ -f "pyproject.toml" ]; then
        # Try to install with uv first (faster), fall back to pip
        if command_exists uv; then
            print_info "Using uv for dependency installation (faster)..."
            uv pip install -e ".[dev]"
        else
            print_info "Using pip for dependency installation..."
            pip install -e ".[dev]"
        fi
    elif [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        print_error "No dependency file found (requirements.txt or pyproject.toml)"
        exit 1
    fi
    print_success "Backend dependencies installed"
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_info "Creating .env file from .env.example..."
            cp .env.example .env
            print_success ".env file created"
            print_warning "Please edit backend/.env and configure your API keys"
        else
            print_warning "No .env.example file found, skipping .env creation"
        fi
    else
        print_warning ".env file already exists, skipping creation"
    fi
    
    cd .. || exit 1
    
    # Step 3: Frontend setup
    print_header "Step 3: Setting Up Frontend"
    
    cd frontend || exit 1
    
    # Install frontend dependencies
    print_info "Installing frontend dependencies..."
    npm install
    print_success "Frontend dependencies installed"
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_info "Creating .env file from .env.example..."
            cp .env.example .env
            print_success ".env file created"
        else
            print_warning "No .env.example file found, skipping .env creation"
        fi
    else
        print_warning ".env file already exists, skipping creation"
    fi
    
    cd .. || exit 1
    
    # Step 4: Install pre-commit hooks
    print_header "Step 4: Installing Pre-commit Hooks"
    
    # Install pre-commit if not already installed
    if ! command_exists pre-commit; then
        print_info "Installing pre-commit..."
        if command_exists uv; then
            cd backend && source .venv/bin/activate && uv pip install pre-commit && cd ..
        else
            cd backend && source .venv/bin/activate && pip install pre-commit && cd ..
        fi
        print_success "pre-commit installed"
    else
        print_success "pre-commit already installed"
    fi
    
    # Install pre-commit hooks
    print_info "Installing pre-commit hooks..."
    cd backend && source .venv/bin/activate && pre-commit install && cd ..
    print_success "Pre-commit hooks installed"
    
    # Step 5: Verify setup
    print_header "Step 5: Verifying Setup"
    
    # Test backend
    print_info "Testing backend setup..."
    cd backend || exit 1
    # shellcheck disable=SC1091
    source .venv/bin/activate
    
    # Check if pytest is available
    if python -c "import pytest" 2>/dev/null; then
        # Just check that tests can be collected (don't run them)
        if pytest --collect-only -q > /dev/null 2>&1; then
            print_success "Backend tests can be collected successfully"
        else
            print_warning "Backend test collection had issues (this might be expected)"
        fi
    else
        print_warning "pytest not installed, skipping backend test verification"
    fi
    
    cd .. || exit 1
    
    # Test frontend
    print_info "Testing frontend setup..."
    cd frontend || exit 1
    
    # Check if npm test works (just check if the command exists)
    if npm run test -- --version > /dev/null 2>&1; then
        print_success "Frontend test environment is ready"
    else
        print_warning "Frontend test command check had issues"
    fi
    
    cd .. || exit 1
    
    # Final success message
    print_header "Setup Complete!"
    
    echo -e "${GREEN}✓ Development environment setup completed successfully!${NC}\n"
    
    echo "Next steps:"
    echo ""
    echo "1. Configure your API keys in backend/.env"
    echo ""
    echo "2. Start the backend server:"
    echo "   cd backend && source .venv/bin/activate && luminote serve"
    echo ""
    echo "3. In a new terminal, start the frontend:"
    echo "   cd frontend && npm run dev"
    echo ""
    echo "4. Visit http://localhost:5000 to see Luminote in action"
    echo ""
    echo "For more information, see CONTRIBUTING.md"
    echo ""
}

# Run main function
main
