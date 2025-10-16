#!/bin/bash

# Local Testing Runner Script
# This script runs all tests for the MLOps pipeline

set -e  # Exit on any error

echo "🚀 Starting MLOps Local Testing Pipeline"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to run a test and report status
run_test() {
    local test_name=$1
    local test_command=$2
    
    print_status $BLUE "🔄 Running: $test_name"
    
    if eval $test_command; then
        print_status $GREEN "✅ $test_name: PASSED"
        return 0
    else
        print_status $RED "❌ $test_name: FAILED"
        return 1
    fi
}

# Initialize counters
total_tests=0
passed_tests=0
failed_tests=0

# Change to project directory
cd "$(dirname "$0")"

print_status $BLUE "📍 Working directory: $(pwd)"

# Determine python command early
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    print_status $RED "❌ No Python interpreter found (tried python3 and python)"
fi

# Check for dependency issues before running tests
print_status $YELLOW "\n0️⃣ Dependency Check"
if [ -n "$PYTHON_CMD" ]; then
    if $PYTHON_CMD -c "import numpy, pandas" 2>/dev/null; then
        print_status $GREEN "✅ Dependencies look good"
    else
        print_status $YELLOW "⚠️  Dependency issues detected. Run: $PYTHON_CMD fix_dependencies.py"
        print_status $BLUE "   Attempting to continue anyway..."
    fi
else
    print_status $RED "❌ No Python interpreter found for dependency check"
fi

# Test 1: Code Quality Check (flake8)
print_status $YELLOW "\n1️⃣ Code Quality Check"
if command -v flake8 &> /dev/null; then
    if run_test "flake8 linting" "flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
else
    print_status $YELLOW "⚠️  flake8 not installed, skipping linting check"
fi

# Test 2: Unit Tests
print_status $YELLOW "\n2️⃣ Unit Tests"
if [ -n "$PYTHON_CMD" ]; then
    if run_test "unit tests" "$PYTHON_CMD -m pytest tests/ -v --tb=short"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
else
    print_status $RED "❌ Python not found, cannot run unit tests"
    ((failed_tests++))
    ((total_tests++))
fi

# Test 3: Integration Test
print_status $YELLOW "\n3️⃣ Integration Test"
if [ -n "$PYTHON_CMD" ]; then
    if run_test "integration test" "$PYTHON_CMD test_local.py"; then
        ((passed_tests++))
    else
        ((failed_tests++))
    fi
    ((total_tests++))
else
    print_status $RED "❌ Python not found, cannot run integration test"
    ((failed_tests++))
    ((total_tests++))
fi

# Test 4: Check Required Files
print_status $YELLOW "\n4️⃣ Required Files Check"
required_files=(
    "src/main.py"
    "src/deployment.yml"
    "src/model/train.py"
    "test_model/test_data.csv"
    "requirements.txt"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        print_status $GREEN "✅ Found: $file"
    else
        print_status $RED "❌ Missing: $file"
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -eq 0 ]]; then
    print_status $GREEN "✅ All required files present"
    ((passed_tests++))
else
    print_status $RED "❌ Missing required files: ${missing_files[*]}"
    ((failed_tests++))
fi
((total_tests++))

# Final Summary
print_status $BLUE "\n" "=" * 50
print_status $BLUE "📊 TEST SUMMARY"
print_status $BLUE "=" * 50

if [[ $total_tests -gt 0 ]]; then
    success_rate=$((passed_tests * 100 / total_tests))
    print_status $BLUE "Total Tests: $total_tests"
    print_status $GREEN "Passed: $passed_tests"
    print_status $RED "Failed: $failed_tests"
    print_status $BLUE "Success Rate: ${success_rate}%"
    
    if [[ $failed_tests -eq 0 ]]; then
        print_status $GREEN "\n🎉 All tests passed! Ready for deployment."
        exit 0
    else
        print_status $RED "\n❌ Some tests failed. Please fix issues before deployment."
        exit 1
    fi
else
    print_status $RED "❌ No tests were executed"
    exit 1
fi
