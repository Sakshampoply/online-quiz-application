#!/usr/bin/env python3
"""
Test runner script for the backend test suite.
Provides convenient commands for running different types of tests.
"""

import subprocess
import sys
import os
from pathlib import Path

# Get the backend directory
BACKEND_DIR = Path(__file__).parent
VENV_PYTHON = BACKEND_DIR / ".venv" / "bin" / "python"


def run_command(cmd, description):
    """Run a command and print results."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd, shell=True, cwd=BACKEND_DIR.parent, capture_output=False, text=True
        )
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
        else:
            print(f"❌ {description} - FAILED")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False


def main():
    """Main test runner function."""
    if len(sys.argv) < 2:
        print(
            """
🧪 Backend Test Suite Runner

Usage: python run_tests.py [command]

Commands:
  all         - Run all tests
  unit        - Run unit tests (test_backend.py)
  edge        - Run edge case tests (test_edge_cases.py) 
  api         - Run API integration tests (test_api.py)
  fast        - Run tests without verbose output
  help        - Show this help message

Examples:
  python run_tests.py all
  python run_tests.py unit
  python run_tests.py api
        """
        )
        return

    command = sys.argv[1].lower()

    # Check if virtual environment exists
    if not VENV_PYTHON.exists():
        print(
            "❌ Virtual environment not found. Please run 'python -m venv .venv' first."
        )
        return

    python_cmd = str(VENV_PYTHON)

    if command == "all":
        success = run_command(
            f"{python_cmd} -m pytest backend/tests/ -v", "Running All Tests"
        )
    elif command == "unit":
        success = run_command(
            f"{python_cmd} -m pytest backend/tests/test_backend.py -v",
            "Running Unit Tests",
        )
    elif command == "edge":
        success = run_command(
            f"{python_cmd} -m pytest backend/tests/test_edge_cases.py -v",
            "Running Edge Case Tests",
        )
    elif command == "api":
        success = run_command(
            f"{python_cmd} -m pytest backend/tests/test_api.py -v",
            "Running API Integration Tests",
        )
    elif command == "fast":
        success = run_command(
            f"{python_cmd} -m pytest backend/tests/", "Running All Tests (Fast Mode)"
        )
    elif command == "help":
        main()
        return
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python run_tests.py help' for available commands.")
        return

    print(f"\n{'='*60}")
    if success:
        print("🎉 All tests completed successfully!")
    else:
        print("💥 Some tests failed. Check output above.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
