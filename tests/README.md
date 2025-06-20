# Jeeves AI Assistant Testing Framework

This directory contains a comprehensive testing framework for the Jeeves AI Assistant application.

## 🏗️ Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and shared fixtures
├── test_ai_providers.py     # Unit tests for AI providers
├── test_ai_provider_manager.py  # Unit tests for provider manager
├── test_integration.py      # Integration tests
├── test_api.py              # API tests (external service calls)
└── README.md                # This file
```

## 🧪 Test Categories

### 1. Unit Tests (`test_ai_providers.py`, `test_ai_provider_manager.py`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single classes, methods, and functions
- **Speed**: Fast execution
- **Dependencies**: Mocked external services

**Test Coverage:**
- AI Provider initialization and configuration
- Response generation logic
- Error handling and validation
- Provider switching and management
- Configuration validation

### 2. Integration Tests (`test_integration.py`)
- **Purpose**: Test interaction between components
- **Scope**: Multiple components working together
- **Speed**: Medium execution
- **Dependencies**: Mocked external services

**Test Coverage:**
- AI Engine with Provider Manager
- Database with Chat Manager
- Provider Manager with multiple providers
- End-to-end workflows
- Error handling across components

### 3. API Tests (`test_api.py`)
- **Purpose**: Test actual external API calls
- **Scope**: Real Gemini API integration
- **Speed**: Slow execution (network calls)
- **Dependencies**: Real API keys and internet connection

**Test Coverage:**
- Real Gemini API connection
- API parameter validation
- Rate limiting and performance
- Error handling for API failures
- System instruction testing

## 🏷️ Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.api` - API tests
- `@pytest.mark.gui` - GUI tests (future)
- `@pytest.mark.slow` - Slow running tests

## 🚀 Running Tests

### Quick Start
```bash
# Run fast tests (unit + integration, no API calls)
python run_tests.py --type fast

# Run all tests
python run_tests.py --type all

# Run specific test categories
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type api
```

### Advanced Usage
```bash
# Run with coverage report
python run_tests.py --type coverage

# Run code linting
python run_tests.py --type lint

# Run type checking
python run_tests.py --type types

# Run security checks
python run_tests.py --type security

# Run performance tests
python run_tests.py --type performance

# Check dependencies
python run_tests.py --check-deps
```

### Direct Pytest Commands
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ai_providers.py -v

# Run tests with specific marker
pytest tests/ -m unit -v
pytest tests/ -m "not slow" -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 🔧 Test Configuration

### Environment Variables
- `GOOGLE_API_KEY` - Required for API tests
- `JEEVES_TEST_MODE` - Set to 'true' for test environment

### Test Fixtures
Common test fixtures are defined in `conftest.py`:

- `test_data_dir` - Temporary directory for test data
- `test_database` - Test database instance
- `gemini_provider` - Configured Gemini provider
- `placeholder_provider` - Placeholder provider
- `ai_provider_manager` - Provider manager instance
- `chat_manager` - Chat manager instance
- `sample_conversation` - Sample conversation data
- `sample_threads` - Sample thread data

## 📊 Test Coverage

The testing framework aims for comprehensive coverage:

### Code Coverage Targets
- **Unit Tests**: 90%+ line coverage
- **Integration Tests**: 80%+ integration coverage
- **API Tests**: 70%+ API functionality coverage

### Coverage Areas
- ✅ AI Provider initialization and configuration
- ✅ Response generation and error handling
- ✅ Provider management and switching
- ✅ Database operations and persistence
- ✅ Chat management and conversation handling
- ✅ API integration and external service calls
- ✅ Error handling and fallback mechanisms

## 🛠️ Development Workflow

### Adding New Tests
1. **Unit Tests**: Add to appropriate test file or create new one
2. **Integration Tests**: Add to `test_integration.py`
3. **API Tests**: Add to `test_api.py`

### Test Naming Convention
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<functionality>`

### Example Test Structure
```python
class TestNewFeature:
    """Test the new feature functionality."""
    
    def test_new_feature_initialization(self):
        """Test new feature initialization."""
        # Arrange
        # Act
        # Assert
    
    @pytest.mark.integration
    def test_new_feature_integration(self):
        """Test new feature integration."""
        # Integration test code
```

## 🔍 Debugging Tests

### Running Single Tests
```bash
# Run specific test method
pytest tests/test_ai_providers.py::TestGeminiProvider::test_gemini_provider_initialization -v

# Run with debug output
pytest tests/ -v -s --tb=long
```

### Test Logging
Tests use Python's logging module. Set log level for debugging:
```bash
pytest tests/ --log-cli-level=DEBUG
```

## 📈 Continuous Integration

### GitHub Actions (Recommended)
Create `.github/workflows/test.yml`:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - run: pip install -e ".[test]"
      - run: python run_tests.py --type fast
      - run: python run_tests.py --type coverage
```

### Pre-commit Hooks
Install pre-commit hooks for automatic testing:
```bash
pip install pre-commit
pre-commit install
```

## 🐛 Common Issues

### API Key Issues
- **Problem**: API tests failing
- **Solution**: Set `GOOGLE_API_KEY` environment variable
- **Alternative**: Skip API tests with `-m "not api"`

### Import Errors
- **Problem**: Module import errors
- **Solution**: Ensure `src/` is in Python path
- **Check**: Run `python -c "import sys; print(sys.path)"`

### Database Issues
- **Problem**: Database test failures
- **Solution**: Tests use temporary databases, no setup required
- **Check**: Ensure SQLite is available

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)
- [Mock Testing Guide](https://docs.python.org/3/library/unittest.mock.html)

## 🤝 Contributing

When adding new features:
1. Write unit tests for new functionality
2. Add integration tests for component interactions
3. Add API tests if external services are involved
4. Update this documentation if needed
5. Ensure all tests pass before submitting PR

## 📊 Test Metrics

Track test metrics over time:
- Test execution time
- Code coverage percentage
- Number of tests by category
- Test failure rate
- API test success rate

Use these metrics to maintain test quality and identify areas for improvement. 