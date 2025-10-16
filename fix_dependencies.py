#!/usr/bin/env python3
"""Script to fix dependency issues for testing."""

import subprocess
import sys

def run_command(cmd):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    """Fix dependency issues."""
    print("🔧 Fixing dependency issues for testing...")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if not in_venv:
        print("⚠️  Warning: Not in a virtual environment. Consider using one.")
    
    # Install/upgrade numpy and pandas
    print("📦 Installing compatible numpy and pandas versions...")
    
    pip_cmd = "pip3" if sys.platform != "win32" else "pip"
    
    # First, uninstall and reinstall numpy and pandas to ensure compatibility
    commands = [
        f"{pip_cmd} uninstall numpy pandas -y",
        f'"{pip_cmd}" install "numpy>=1.21.0,<2.0.0"',
        f'"{pip_cmd}" install "pandas>=1.4.3,<2.0.0"',
        f"{pip_cmd} install -r requirements.txt"
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        success, stdout, stderr = run_command(cmd)
        if not success and "not installed" not in stderr.lower():
            print(f"⚠️  Command failed: {stderr}")
        else:
            print("✅ Command completed")
    
    # Test the import
    print("🧪 Testing imports...")
    try:
        import numpy as np
        import pandas as pd
        from sklearn.linear_model import LogisticRegression
        print(f"✅ numpy version: {np.__version__}")
        print(f"✅ pandas version: {pd.__version__}")
        print("✅ All imports successful!")
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
