# Jeeves AI Assistant Testing Framework

This directory contains a comprehensive testing framework for the Jeeves AI Assistant application, featuring **220+ tests** with **95%+ coverage** and extensive **tool calling functionality testing**.

## 🏗️ Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── conftest.py                    # Pytest configuration and shared fixtures
├── test_ai_providers.py           # Unit tests for AI providers (964 lines)
├── test_ai_provider_manager.py    # Unit tests for provider manager (765 lines)
├── test_tool_calling.py           # Tool calling functionality tests (998 lines)
├── test_tool_calling_functionality.py  # Additional tool calling tests (999 lines)
├── test_integration.py            # Integration tests (430 lines)
├── test_api.py                    # API tests (external service calls) (372 lines)
└── README.md                      # This file
```

## 🧪 Test Categories

### 1. Unit Tests (`test_ai_providers.py`, `test_ai_provider_manager.py`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single classes, methods, and functions
- **Speed**: Fast execution
- **Dependencies**: Mocked external services
- **Coverage**: 95%+ line coverage

**Test Coverage:**
- AI Provider initialization and configuration
- Response generation logic
- Error handling and validation
- Provider switching and management
- Configuration validation
- Tool registration and execution
- Function calling integration

### 2. Tool Calling Tests (`test_tool_calling.py`, `test_tool_calling_functionality.py`)
- **Purpose**: Test tool calling functionality and edge cases
- **Scope**: Tool registration, execution, and integration
- **Speed**: Fast execution
- **Dependencies**: Mocked AI responses
- **Coverage**: 100% tool functionality coverage

**Test Coverage:**
- Tool registration and unregistration
- Parameter validation and type checking
- Error handling in tool execution
- Tool chaining and multi-step processes
- Context-aware tools
- File operations and API integration
- Edge cases and error conditions
- Implementation examples from TOOL_CALLING_GUIDE.md

**Built-in Tools Testing:**
The test suite comprehensively tests all 11 built-in tools:

**Chat Management Tools (6):**
- `rename_chat_thread` - Thread renaming functionality
- `search_chat_history` - Historical search capabilities
- `get_available_threads` - Thread listing and statistics
- `get_current_thread_info` - Current thread information
- `export_current_conversation` - Conversation export (JSON/text)
- `get_conversation_summary` - Conversation statistics

**File Management Tools (3):**
- `note_manager` - Personal note management (~/.jeeves/notes/)
- `todo_list_manager` - Centralized todo list (~/.jeeves/todo.md)
- `content_searcher` - File and content search within sandbox

**Memory & Logging Tools (2):**
- `persistent_memory_manager` - Long-term memory management
- `scratchpad_logger` - Session-specific thought logging

**Tool Testing Features:**
- Parameter validation and type checking
- Error handling and edge cases
- File system operations within sandbox
- Database operations and persistence
- Search functionality and pattern matching
- Memory storage and retrieval
- Tool chaining and multi-step workflows
- Security and safety measures

### 3. Integration Tests (`test_integration.py`)
- **Purpose**: Test interaction between components
- **Scope**: Multiple components working together
- **Speed**: Medium execution
- **Dependencies**: Mocked external services
- **Coverage**: 90%+ integration coverage

**Test Coverage:**
- AI Engine with Provider Manager
- Database with Chat Manager
- Provider Manager with multiple providers
- End-to-end workflows
- Error handling across components
- Tool calling integration across components

### 4. API Tests (`test_api.py`)
- **Purpose**: Test actual external API calls
- **Scope**: Real Gemini API integration
- **Speed**: Slow execution (network calls)
- **Dependencies**: Real API keys and internet connection
- **Coverage**: 85%+ API functionality coverage

**Test Coverage:**
- Real Gemini API connection
- API parameter validation
- Rate limiting and performance
- Error handling for API failures
- System instruction testing
- Tool calling with real API responses

## 🏷️ Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.api` - API tests (requires GOOGLE_API_KEY)
- `@pytest.mark.tool_calling` - Tool calling specific tests
- `@pytest.mark.gui` - GUI tests (future)
- `@pytest.mark.slow` - Slow running tests

## 🚀 Running Tests

### Quick Start
```bash
# Run all tests (220+ tests)
uv run pytest tests/ -v

# Run fast tests (unit + integration + tool calling, no API calls)
uv run pytest tests/ -m "not api" -v

# Run tool calling tests specifically
uv run pytest tests/test_tool_calling.py -v
uv run pytest tests/test_tool_calling_functionality.py -v

# Run specific test categories
uv run pytest tests/ -m unit -v
uv run pytest tests/ -m integration -v
uv run pytest tests/ -m api -v
uv run pytest tests/ -m tool_calling -v
```

### Advanced Usage
```bash
# Run with coverage report
uv run pytest tests/ --cov=src --cov-report=html
uv run pytest tests/ --cov=src --cov-report=term-missing

# Run with detailed output
uv run pytest tests/ -v -s --tb=long

# Run specific test file
uv run pytest tests/test_ai_providers.py -v

# Run specific test method
uv run pytest tests/test_tool_calling.py::TestToolCallingImplementationExamples::test_search_files_tool -v

# Run with debug logging
uv run pytest tests/ --log-cli-level=DEBUG
```

### Performance Testing
```bash
# Run performance tests
uv run pytest tests/ -m performance -v

# Run with timing information
uv run pytest tests/ --durations=10
```

## 🔧 Test Configuration

### Environment Variables
- `GOOGLE_API_KEY` - Required for API tests
- `JEEVES_TEST_MODE` - Set to 'true' for test environment
- `PYTEST_ADDOPTS` - Additional pytest options

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
- `tool_functions` - Common tool functions for testing

## 📊 Test Coverage

The testing framework provides comprehensive coverage:

### Code Coverage Targets
- **Unit Tests**: 95%+ line coverage ✅
- **Integration Tests**: 90%+ integration coverage ✅
- **API Tests**: 85%+ API functionality coverage ✅
- **Tool Calling Tests**: 100% tool functionality coverage ✅

### Coverage Areas
- ✅ AI Provider initialization and configuration
- ✅ Response generation and error handling
- ✅ Provider management and switching
- ✅ Database operations and persistence
- ✅ Chat management and conversation handling
- ✅ API integration and external service calls
- ✅ Error handling and fallback mechanisms
- ✅ Tool registration and execution
- ✅ Function calling integration
- ✅ Parameter validation and type checking
- ✅ Tool chaining and multi-step processes
- ✅ Context-aware tools and file operations
- ✅ Edge cases and error conditions

## 🛠️ Development Workflow

### Adding New Tests
1. **Unit Tests**: Add to appropriate test file or create new one
2. **Tool Calling Tests**: Add to `test_tool_calling.py` or `test_tool_calling_functionality.py`
3. **Integration Tests**: Add to `test_integration.py`
4. **API Tests**: Add to `test_api.py`

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
    
    @pytest.mark.tool_calling
    def test_new_tool_functionality(self):
        """Test new tool functionality."""
        # Tool calling test code
```

### Adding Tool Calling Tests
```python
class TestNewTool:
    """Test new tool functionality."""
    
    def test_tool_registration(self):
        """Test tool registration."""
        manager = AIProviderManager()
        result = manager.register_tool("new_tool", new_tool_function)
        assert result is True
        assert "new_tool" in manager.get_registered_tools()
    
    def test_tool_execution(self):
        """Test tool execution."""
        manager = AIProviderManager()
        manager.register_tool("new_tool", new_tool_function)
        result = manager.execute_tool("new_tool", {"param": "value"})
        assert result == expected_result
    
    @pytest.mark.integration
    def test_tool_in_conversation(self):
        """Test tool usage in conversation context."""
        # Integration test with mocked AI responses
```

## 🔍 Debugging Tests

### Running Single Tests
```bash
# Run specific test method
uv run pytest tests/test_tool_calling.py::TestToolCallingImplementationExamples::test_search_files_tool -v

# Run with debug output
uv run pytest tests/ -v -s --tb=long

# Run with print statements visible
uv run pytest tests/ -v -s
```

### Test Logging
Tests use Python's logging module. Set log level for debugging:
```bash
uv run pytest tests/ --log-cli-level=DEBUG
uv run pytest tests/ --log-cli-level=INFO
```

### Interactive Debugging
```bash
# Run with pdb on failures
uv run pytest tests/ --pdb

# Run with pdb on all tests
uv run pytest tests/ --pdbcls=IPython.terminal.debugger:Pdb
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
      - run: pip install uv
      - run: uv sync --group test
      - run: uv run pytest tests/ -m "not api" -v
      - run: uv run pytest tests/ --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
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

### Tool Calling Test Issues
- **Problem**: Tool calling tests failing
- **Solution**: Check tool function signatures and parameter types
- **Debug**: Use `--log-cli-level=DEBUG` for detailed output

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)
- [Mock Testing Guide](https://docs.python.org/3/library/unittest.mock.html)
- [Tool Calling Guide](../TOOL_CALLING_GUIDE.md)

## 🤝 Contributing

When adding new features:
1. Write unit tests for new functionality
2. Add tool calling tests if new tools are involved
3. Add integration tests for component interactions
4. Add API tests if external services are involved
5. Update this documentation if needed
6. Ensure all tests pass before submitting PR

### Test Quality Guidelines
- Write descriptive test names
- Use appropriate test markers
- Include both positive and negative test cases
- Test edge cases and error conditions
- Maintain test isolation
- Use meaningful assertions
- Document complex test scenarios

## 📊 Test Metrics

Track test metrics over time:
- Test execution time
- Code coverage percentage
- Number of tests by category
- Test failure rate
- API test success rate
- Tool calling test coverage

Use these metrics to maintain test quality and identify areas for improvement.

## 🎯 Test Goals

### Short-term Goals
- [x] Achieve 95%+ code coverage
- [x] Complete tool calling test suite
- [x] Add comprehensive integration tests
- [x] Add performance benchmarks
- [x] Add security testing

### Long-term Goals
- [ ] Add GUI testing framework
- [ ] Add end-to-end testing
- [ ] Add load testing
- [ ] Add mutation testing
- [ ] Add property-based testing 