# Local Testing Guide

This guide explains how to run the local testing suite for the MLOps diabetes prediction pipeline.

## Quick Start

1. **Fix Dependencies** (if you encounter numpy/pandas errors):
   ```bash
   python3 fix_dependencies.py
   ```

2. **Run All Tests**:
   ```bash
   ./run_tests.sh
   ```

## Individual Test Components

### Unit Tests
```bash
python3 -m pytest tests/ -v
```

### Integration Test
```bash
python3 test_local.py
```

### Code Quality Check
```bash
flake8 src/
```

## Common Issues and Solutions

### "Python not found" error
If you see "❌ Python not found" errors when running the test script, make sure you have Python installed:

```bash
# Check if python3 is available
python3 --version

# If not available, try python
python --version
```

The script automatically detects `python3` first, then falls back to `python`.

### numpy.dtype size changed error
This error occurs when there's a version mismatch between numpy and pandas. 

**Solution:**
```bash
# Run the dependency fixer
python3 fix_dependencies.py

# Or manually reinstall compatible versions
pip3 uninstall numpy pandas -y
pip3 install numpy>=1.21.0,<2.0.0
pip3 install pandas>=1.4.3,<2.0.0
```

### Import errors in tests
If you see import errors when running tests, make sure you're in the correct directory and have installed all requirements:

```bash
pip3 install -r requirements.txt
```

### Virtual Environment
It's recommended to use a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
./run_tests.sh
```

## Test Structure

- `tests/test_train.py` - Tests for training pipeline functions
- `tests/test_scoring.py` - Tests for scoring script (`main.py`)
- `test_local.py` - End-to-end integration test
- `run_tests.sh` - Automated test runner

## Success Criteria

All tests should pass before deploying to Azure:
- ✅ Code quality (flake8 passes)
- ✅ Unit tests (pytest passes)
- ✅ Integration test (model trains and predicts)
- ✅ Required files present
