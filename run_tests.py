#!/usr/bin/env python3
"""
Test Runner for Intel CPU Crawler

Runs comprehensive integration tests to verify system health.
Use this after any code changes to ensure everything still works.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --unit            # Run only unit tests
    python run_tests.py --verbose         # Run with verbose output
"""

import sys
import subprocess
import argparse
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))


def run_integration_tests(verbosity=1):
    """Run only integration tests."""
    print("🔬 Running Integration Tests...")
    print("=" * 50)
    
    verbosity_flag = '-v' if verbosity > 1 else ''
    cmd = [sys.executable, '-m', 'unittest', 'tests.test_integration']
    if verbosity_flag:
        cmd.append(verbosity_flag)
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode == 0


def run_unit_tests(verbosity=1):
    """Run only unit tests."""
    print("🧪 Running Unit Tests...")
    print("=" * 50)
    
    verbosity_flag = '-v' if verbosity > 1 else ''
    cmd = [sys.executable, '-m', 'unittest', 'tests.test_crawler']
    if verbosity_flag:
        cmd.append(verbosity_flag)
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode == 0


def run_all_tests(verbosity=1):
    """Run all available tests."""
    print("🚀 Running All Tests...")
    print("=" * 50)
    
    print("Running integration tests first...")
    integration_success = run_integration_tests(verbosity)
    
    print("\nRunning unit tests...")
    unit_success = run_unit_tests(verbosity)
    
    return integration_success and unit_success


def check_system_health():
    """Perform basic system health checks before running tests."""
    print("🏥 Checking System Health...")
    print("-" * 30)
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("⚠️  Warning: Python 3.8+ recommended")
    else:
        print("✅ Python version OK")
    
    # Check required directories
    required_dirs = ['src', 'config', 'data', 'tests']
    base_dir = Path(__file__).parent
    
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/ directory found")
        else:
            print(f"❌ {dir_name}/ directory missing")
            return False
    
    # Check core modules can be imported
    try:
        from crawler import IntelCpuCrawler
        from parser import IntelCpuParser
        from database_manager import PowerSpecDatabaseManager
        from data_manager import DataManager
        from utils import setup_logging
        print("✅ All core modules importable")
    except ImportError as e:
        print(f"❌ Module import failed: {e}")
        return False
    
    print("✅ System health check passed")
    print()
    return True


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Test runner for Intel CPU Crawler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_tests.py                    # Run all tests
    python run_tests.py --integration      # Integration tests only
    python run_tests.py --unit            # Unit tests only  
    python run_tests.py --verbose         # Verbose output
    python run_tests.py --no-health       # Skip health check
        """
    )
    
    parser.add_argument(
        '--integration',
        action='store_true',
        help='Run only integration tests'
    )
    
    parser.add_argument(
        '--unit',
        action='store_true',
        help='Run only unit tests'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Run tests with verbose output'
    )
    
    parser.add_argument(
        '--no-health',
        action='store_true',
        help='Skip system health check'
    )
    
    args = parser.parse_args()
    
    # Determine verbosity
    verbosity = 2 if args.verbose else 1
    
    # System health check
    if not args.no_health:
        if not check_system_health():
            print("❌ System health check failed. Aborting tests.")
            return 1
    
    # Determine which tests to run
    success = True
    
    if args.integration:
        success = run_integration_tests(verbosity)
    elif args.unit:
        success = run_unit_tests(verbosity)
    else:
        success = run_all_tests(verbosity)
    
    # Print final result
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests PASSED! System is healthy.")
        return 0
    else:
        print("❌ Some tests FAILED. Please review the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())