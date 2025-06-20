#!/usr/bin/env python3
"""
Test runner for Jeeves AI Assistant.
Comprehensive testing framework with multiple test categories and options.
"""
import os
import sys
import argparse
import subprocess
import time
import shutil
from pathlib import Path

# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RESET = '\033[0m'


def get_python_executable():
    """Get the appropriate Python executable, preferring uv if available."""
    # Check if uv is available
    if shutil.which("uv"):
        return "uv"
    else:
        return sys.executable


def run_command(cmd, description=""):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"{BLUE}{BOLD}{description}{RESET}")
    print(f"{CYAN}Command: {' '.join(cmd)}{RESET}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    duration = end_time - start_time
    
    if result.returncode == 0:
        print(f"{GREEN}{BOLD}{description} - PASSED ({duration:.2f}s){RESET}")
        if result.stdout:
            print(f"{WHITE}Output:{RESET}")
            print(result.stdout)
    else:
        print(f"{RED}{BOLD}{description} - FAILED ({duration:.2f}s){RESET}")
        if result.stderr:
            print(f"{RED}Error:{RESET}")
            print(result.stderr)
        if result.stdout:
            print(f"{WHITE}Output:{RESET}")
            print(result.stdout)
    
    return result.returncode == 0


def run_unit_tests():
    """Run unit tests."""
    python_exe = get_python_executable()
    if python_exe == "uv":
        return run_command(
            ["uv", "run", "pytest", "tests/test_ai_providers.py", "-v"],
            "Running Unit Tests (AI Providers)"
        )
    else:
        return run_command(
            [python_exe, "-m", "pytest", "tests/test_ai_providers.py", "-v"],
            "Running Unit Tests (AI Providers)"
        )


def run_integration_tests():
    """Run integration tests."""
    python_exe = get_python_executable()
    if python_exe == "uv":
        return run_command(
            ["uv", "run", "pytest", "tests/test_integration.py", "-v"],
            "Running Integration Tests"
        )
    else:
        return run_command(
            [python_exe, "-m", "pytest", "tests/test_integration.py", "-v"],
            "Running Integration Tests"
        )


def run_api_tests():
    """Run API tests."""
    python_exe = get_python_executable()
    if python_exe == "uv":
        return run_command(
            ["uv", "run", "pytest", "tests/test_api.py", "-m", "api", "-v"],
            "Running API Tests"
        )
    else:
        return run_command(
            [python_exe, "-m", "pytest", "tests/test_api.py", "-m", "api", "-v"],
            "Running API Tests"
        )


def run_all_tests():
    """Run all tests."""
    python_exe = get_python_executable()
    if python_exe == "uv":
        return run_command(
            ["uv", "run", "pytest", "tests/", "-v"],
            "Running All Tests"
        )
    else:
        return run_command(
            [python_exe, "-m", "pytest", "tests/", "-v"],
            "Running All Tests"
        )


def run_fast_tests():
    """Run fast tests (exclude slow and API tests)."""
    python_exe = get_python_executable()
    if python_exe == "uv":
        return run_command(
            ["uv", "run", "pytest", "tests/", "-v", "-m", "not slow and not api"],
            "Running Fast Tests (Excluding Slow and API Tests)"
        )
    else:
        return run_command(
            [python_exe, "-m", "pytest", "tests/", "-v", "-m", "not slow and not api"],
            "Running Fast Tests (Excluding Slow and API Tests)"
        )


def run_coverage():
    """Run tests with coverage report."""
    python_exe = get_python_executable()
    if python_exe == "uv":
        return run_command(
            ["uv", "run", "pytest", "tests/", "--cov=src", "--cov-report=html", "--cov-report=term"],
            "Running Tests with Coverage Report"
        )
    else:
        return run_command(
            [python_exe, "-m", "pytest", "tests/", "--cov=src", "--cov-report=html", "--cov-report=term"],
            "Running Tests with Coverage Report"
        )


def run_linting():
    """Run code linting."""
    python_exe = get_python_executable()
    if python_exe == "uv":
        return run_command(
            ["uv", "run", "flake8", "src/", "--max-line-length=100"],
            "Running Code Linting"
        )
    else:
        return run_command(
            [python_exe, "-m", "flake8", "src/", "--max-line-length=100"],
            "Running Code Linting"
        )


def run_type_checking():
    """Run type checking."""
    python_exe = get_python_executable()
    if python_exe == "uv":
        return run_command(
            ["uv", "run", "mypy", "src/"],
            "Running Type Checking"
        )
    else:
        return run_command(
            [python_exe, "-m", "mypy", "src/"],
            "Running Type Checking"
        )


def run_security_checks():
    """Run security checks."""
    python_exe = get_python_executable()
    if python_exe == "uv":
        return run_command(
            ["uv", "run", "bandit", "-r", "src/"],
            "Running Security Checks"
        )
    else:
        return run_command(
            [python_exe, "-m", "bandit", "-r", "src/"],
            "Running Security Checks"
        )


def run_performance_tests():
    """Run performance tests."""
    python_exe = get_python_executable()
    if python_exe == "uv":
        return run_command(
            ["uv", "run", "pytest", "tests/test_api.py", "-m", "slow", "-v"],
            "Running Performance Tests"
        )
    else:
        return run_command(
            [python_exe, "-m", "pytest", "tests/test_api.py", "-m", "slow", "-v"],
            "Running Performance Tests"
        )


def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        "pytest",
        "pytest-cov",
        "flake8",
        "mypy",
        "bandit",
        # "google-genai"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"{RED}Missing required packages:{RESET}")
        for package in missing_packages:
            print(f"   - {package}")
        print(f"\n{YELLOW}Install missing packages with:{RESET}")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print(f"{GREEN}All required packages are installed{RESET}")
    return True


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Jeeves AI Assistant Test Runner")
    parser.add_argument(
        "--type", "-t",
        choices=["unit", "integration", "api", "all", "fast", "coverage", "lint", "types", "security", "performance"],
        default="fast",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check dependencies only"
    )
    
    args = parser.parse_args()
    
    print(f"{MAGENTA}{BOLD}Jeeves AI Assistant Test Runner{RESET}")
    print(f"{'=' * 60}")
    
    # Check dependencies first
    if args.check_deps:
        check_dependencies()
        return
    
    if not check_dependencies():
        print(f"\n{RED}Please install missing dependencies before running tests{RESET}")
        return
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Run tests based on type
    success = False
    
    if args.type == "unit":
        success = run_unit_tests()
    elif args.type == "integration":
        success = run_integration_tests()
    elif args.type == "api":
        success = run_api_tests()
    elif args.type == "all":
        success = run_all_tests()
    elif args.type == "fast":
        success = run_fast_tests()
    elif args.type == "coverage":
        success = run_coverage()
    elif args.type == "lint":
        success = run_linting()
    elif args.type == "types":
        success = run_type_checking()
    elif args.type == "security":
        success = run_security_checks()
    elif args.type == "performance":
        success = run_performance_tests()
    
    # Summary
    print(f"\n{'=' * 60}")
    if success:
        print(f"{GREEN}{BOLD}All tests completed successfully!{RESET}")
    else:
        print(f"{RED}{BOLD}Some tests failed. Please check the output above.{RESET}")
    print(f"{'=' * 60}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 