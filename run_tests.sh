#!/bin/bash

# Quick test runner for Raspberry Pi Dashboard
# This script provides common test execution scenarios

set -e

echo "=========================================="
echo "🧪 Raspberry Pi Dashboard Test Runner"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}$1${NC}"
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

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Parse command line arguments
COMMAND=${1:-"all"}

case $COMMAND in
    "quick")
        print_status "Running quick validation tests..."
        python test_runner.py --type unit --no-coverage
        ;;
    
    "full")
        print_status "Running full test suite with coverage..."
        python test_runner.py --type all --report html
        ;;
    
    "unit")
        print_status "Running unit tests..."
        python test_runner.py --type unit
        ;;
    
    "integration")
        print_status "Running integration tests..."
        python test_runner.py --type integration
        ;;
    
    "config")
        print_status "Running configuration tests..."
        python test_runner.py --type config
        ;;
    
    "api")
        print_status "Running API tests..."
        python test_runner.py --type api
        ;;
    
    "screens")
        print_status "Running screen tests..."
        python test_runner.py --type screens
        ;;
    
    "validate")
        print_status "Validating application structure..."
        python test_runner.py --validate-only
        ;;
    
    "report")
        print_status "Generating test reports..."
        python test_runner.py --report-only
        ;;
    
    "install-deps")
        print_status "Installing test dependencies..."
        pip install pytest pytest-cov pytest-mock responses
        print_success "Test dependencies installed"
        ;;
    
    "help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  quick       - Run quick validation tests (no coverage)"
        echo "  full        - Run full test suite with HTML coverage report"
        echo "  unit        - Run only unit tests"
        echo "  integration - Run only integration tests"
        echo "  config      - Run only configuration tests"
        echo "  api         - Run only API tests"
        echo "  screens     - Run only screen tests"
        echo "  validate    - Validate application structure only"
        echo "  report      - Generate test coverage reports"
        echo "  install-deps - Install test dependencies"
        echo "  help        - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 quick           # Quick test before commit"
        echo "  $0 full            # Full test with coverage"
        echo "  $0 unit            # Just unit tests"
        echo ""
        exit 0
        ;;
    
    "all"|*)
        print_status "Running all tests with coverage..."
        python test_runner.py --type all
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    print_success "Tests completed successfully!"
    echo ""
    echo "📊 Test Reports:"
    if [ -d "test_reports" ]; then
        echo "  Coverage: test_reports/coverage/index.html"
        echo "  XML Reports: test_reports/"
    fi
    echo ""
    echo "🚀 Dashboard is ready to run!"
else
    print_error "Tests failed!"
    echo ""
    echo "❌ Please fix the failing tests before proceeding."
    echo "💡 Run with specific test types to isolate issues:"
    echo "   ./run_tests.sh unit"
    echo "   ./run_tests.sh integration"
    exit 1
fi 