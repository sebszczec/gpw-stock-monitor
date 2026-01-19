"""
Test runner script for GPW Stock Monitor.
Run all tests with coverage report.

Usage:
    python run_tests.py
    python -m pytest tests/
    python -m pytest tests/test_calculations.py  # Run specific test file
    python -m pytest -v                          # Verbose output
    python -m pytest --cov-report=html          # Generate HTML coverage report
"""

import sys
import subprocess


def run_tests():
    """Run all tests with pytest."""
    print("=" * 70)
    print("Running GPW Stock Monitor Test Suite")
    print("=" * 70)
    print()
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--cov=.",
        "--cov-report=term-missing",
        "--cov-report=html"
    ]
    
    result = subprocess.run(cmd)
    
    print()
    print("=" * 70)
    if result.returncode == 0:
        print("✓ All tests passed!")
        print("Coverage report generated in htmlcov/index.html")
    else:
        print("✗ Some tests failed!")
    print("=" * 70)
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
