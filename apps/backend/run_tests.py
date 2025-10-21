#!/usr/bin/env python
"""
Comprehensive test runner for TidyGen Django backend.
Supports running different types of tests: unit, integration, e2e, and static analysis.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def run_static_analysis():
    """Run static analysis tools."""
    print("\n🔍 Running Static Analysis...")
    
    commands = [
        ("flake8 apps/ --max-line-length=88 --exclude=migrations,venv", "Flake8 linting"),
        ("black --check apps/", "Black code formatting check"),
        ("mypy apps/ --ignore-missing-imports", "MyPy type checking"),
    ]
    
    results = []
    for command, description in commands:
        results.append(run_command(command, description))
    
    return all(results)


def run_unit_tests():
    """Run unit tests."""
    print("\n🧪 Running Unit Tests...")
    
    command = "python -m pytest apps/core/tests/ -v --tb=short --disable-warnings"
    return run_command(command, "Unit tests for core app")


def run_integration_tests():
    """Run integration tests."""
    print("\n🔗 Running Integration Tests...")
    
    command = "python -m pytest apps/ -v --tb=short --disable-warnings -m 'not e2e'"
    return run_command(command, "Integration tests")


def run_e2e_tests():
    """Run end-to-end tests."""
    print("\n🌐 Running E2E Tests...")
    
    # First install playwright browsers if needed
    subprocess.run("playwright install", shell=True, check=False)
    
    command = "python -m pytest e2e_tests/ -v --tb=short -m e2e"
    return run_command(command, "E2E tests with Playwright")


def run_all_tests():
    """Run all tests."""
    print("\n🚀 Running All Tests...")
    
    command = "python -m pytest apps/ e2e_tests/ -v --tb=short --disable-warnings"
    return run_command(command, "All tests")


def main():
    """Main function to run tests based on arguments."""
    parser = argparse.ArgumentParser(description="TidyGen Django Backend Test Runner")
    parser.add_argument(
        "test_type",
        choices=["static", "unit", "integration", "e2e", "all"],
        help="Type of tests to run"
    )
    
    args = parser.parse_args()
    
    # Ensure we're in the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print(f"🧪 TidyGen Django Backend Test Suite")
    print(f"📁 Working directory: {backend_dir}")
    
    success = False
    
    if args.test_type == "static":
        success = run_static_analysis()
    elif args.test_type == "unit":
        success = run_unit_tests()
    elif args.test_type == "integration":
        success = run_integration_tests()
    elif args.test_type == "e2e":
        success = run_e2e_tests()
    elif args.test_type == "all":
        success = (
            run_static_analysis() and
            run_unit_tests() and
            run_integration_tests() and
            run_e2e_tests()
        )
    
    if success:
        print(f"\n🎉 All {args.test_type} tests passed!")
        sys.exit(0)
    else:
        print(f"\n💥 Some {args.test_type} tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()