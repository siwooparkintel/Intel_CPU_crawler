# Testing Guide

This document describes the comprehensive testing framework for the Intel CPU Crawler project.

## Overview

The project includes two types of tests:
- **Integration Tests**: Comprehensive tests that verify the entire system works correctly
- **Unit Tests**: Individual component tests (legacy, but maintained for compatibility)

## Running Tests

### Quick Test (Recommended)
```bash
# Run all integration tests (recommended after any changes)
python run_tests.py --integration

# Run with verbose output
python run_tests.py --integration --verbose
```

### Complete Test Suite
```bash
# Run all tests (integration + unit)
python run_tests.py

# Run only unit tests
python run_tests.py --unit
```

### Manual Test Execution
```bash
# Run integration tests directly
python -m unittest tests.test_integration -v

# Run unit tests directly  
python -m unittest tests.test_crawler -v
```

## Integration Tests

The integration tests (`tests/test_integration.py`) provide comprehensive coverage:

### TestCrawlerIntegration
- **Module Imports**: Verifies all core modules can be imported
- **Configuration Loading**: Tests YAML config loading and defaults
- **Database Operations**: Complete database CRUD operations with SQLite
- **Data Manager**: JSON/CSV export functionality
- **Utility Functions**: Logging, headers, URL validation, text cleaning
- **Parser Functionality**: URL filtering and processing logic
- **Crawler Initialization**: Component initialization and configuration
- **End-to-End Workflow**: Complete workflow with mocked HTTP requests
- **CLI Integration**: Command-line interface structure verification

### TestSystemHealth
- **Requirements Compatibility**: All required packages are importable
- **File Structure**: Required files and directories exist
- **Configuration Validity**: YAML configuration is valid and complete

## Test Coverage

The integration tests cover:

| Component | Coverage | Details |
|-----------|----------|---------|
| **Crawler** | ✅ Full | Initialization, configuration, workflow |
| **Parser** | ✅ Core | URL filtering, basic functionality |
| **Database** | ✅ Full | CRUD operations, statistics, search |
| **Data Manager** | ✅ Full | JSON/CSV export, file operations |
| **Utils** | ✅ Full | All utility functions |
| **Configuration** | ✅ Full | YAML loading, validation |
| **CLI** | ✅ Structure | Command availability and imports |

## Health Check Features

The test runner includes automatic system health checks:

1. **Python Version**: Ensures Python 3.8+ (3.11+ recommended)
2. **Directory Structure**: Verifies all required directories exist
3. **Module Imports**: Tests that all core modules can be imported
4. **Configuration**: Validates YAML configuration files

## Test Results Interpretation

### Success (Exit Code 0)
```
🎉 All tests PASSED! System is healthy.
```
- All functionality is working correctly
- Safe to deploy or continue development
- System is ready for production use

### Failure (Exit Code 1)
```
❌ Some tests FAILED. Please review the output above.
```
- Review the detailed test output for specific failures
- Fix any issues before deploying
- Re-run tests after fixes

## Best Practices

### When to Run Tests
- **Always** before committing code changes
- After installing new dependencies
- After modifying configuration files
- Before deploying to production
- After cleaning up code (like we just did!)

### Development Workflow
1. Make changes to the code
2. Run integration tests: `python run_tests.py --integration`
3. Fix any failures
4. Commit changes
5. Periodically run full test suite

### Adding New Tests
When adding new functionality:
1. Add tests to `tests/test_integration.py` for new features
2. Update existing tests if interfaces change
3. Ensure new tests follow the existing patterns
4. Document any new test requirements

## Troubleshooting

### Common Issues

**Import Errors**
```
ModuleNotFoundError: No module named 'click'
```
- Solution: Ensure virtual environment is activated and dependencies are installed
- Run: `pip install -r requirements.txt`

**Database Lock Errors**
```
[WinError 32] The process cannot access the file because it is being used by another process
```
- Solution: Close any applications that might be using the database
- Wait a few seconds and retry

**Configuration Errors**
```
Config file not found, using defaults
```
- This is usually expected behavior and not an error
- Tests should still pass with default configuration

### Test Environment Setup
```bash
# Ensure you're in the project directory
cd /path/to/Intel_cpu_crawler

# Activate virtual environment (if using one)
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
python run_tests.py --integration
```

## Continuous Integration

The tests are designed to be run in CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run Integration Tests
  run: |
    python run_tests.py --integration --no-health
```

Use `--no-health` flag in CI environments where the health check might not be needed.