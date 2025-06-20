"""
Pytest configuration and shared fixtures for Jeeves test suite.
"""
import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import uuid

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.ai_providers import GeminiProvider, PlaceholderProvider
from core.ai_provider_manager import AIProviderManager
from core.database import DatabaseManager
from core.chat_manager import ChatManager


@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp(prefix="jeeves_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_db_path(tmp_path):
    """Create a unique test database path."""
    db_name = f"test_jeeves_{uuid.uuid4().hex[:8]}.db"
    return str(tmp_path / db_name)


@pytest.fixture
def mock_gemini_api_key():
    """Mock Gemini API key for testing."""
    return "test_api_key_12345"


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client for testing."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.text = "This is a test response from Gemini"
    mock_client.models.generate_content.return_value = mock_response
    return mock_client


@pytest.fixture
def gemini_provider(mock_gemini_api_key):
    """Create a Gemini provider instance for testing."""
    config = {
        'api_key': mock_gemini_api_key,
        'model': 'gemini-2.0-flash',
        'max_output_tokens': 1024,
        'temperature': 0.7,
        'top_p': 0.95,
        'top_k': 40
    }
    return GeminiProvider(config)


@pytest.fixture
def placeholder_provider():
    """Create a placeholder provider instance for testing."""
    return PlaceholderProvider()


@pytest.fixture
def ai_provider_manager():
    """Create an AI provider manager instance for testing."""
    return AIProviderManager()


@pytest.fixture
def test_database(test_db_path):
    """Create a test database instance."""
    db = DatabaseManager(test_db_path)
    # DatabaseManager initializes automatically in __init__, no need to call initialize()
    yield db
    # Cleanup - ensure connections are properly closed
    try:
        db.close_connections()
    except Exception as e:
        # Log but don't fail the test if cleanup fails
        print(f"Warning: Database cleanup failed: {e}")


@pytest.fixture
def chat_manager(test_database):
    """Create a chat manager instance for testing."""
    return ChatManager(test_database)


@pytest.fixture
def sample_conversation():
    """Sample conversation data for testing."""
    return [
        {'sender': 'user', 'content': 'Hello, how are you?', 'timestamp': '2024-01-01T10:00:00'},
        {'sender': 'assistant', 'content': 'I\'m doing well, thank you! How can I help you?', 'timestamp': '2024-01-01T10:00:01'},
        {'sender': 'user', 'content': 'Can you help me with Python?', 'timestamp': '2024-01-01T10:00:02'},
        {'sender': 'assistant', 'content': 'Of course! Python is a great programming language. What specific help do you need?', 'timestamp': '2024-01-01T10:00:03'}
    ]


@pytest.fixture
def sample_threads():
    """Sample thread data for testing."""
    return [
        {'id': 'test1', 'title': 'Test Thread 1', 'type': 'general', 'created_at': '2024-01-01T10:00:00'},
        {'id': 'test2', 'title': 'Test Thread 2', 'type': 'code', 'created_at': '2024-01-01T11:00:00'},
        {'id': 'test3', 'title': 'Test Thread 3', 'type': 'planning', 'created_at': '2024-01-01T12:00:00'}
    ]


# Environment setup
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    # Store original environment
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ['GOOGLE_API_KEY'] = 'test_api_key_12345'
    os.environ['JEEVES_TEST_MODE'] = 'true'
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# Test markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "gui: mark test as a GUI test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    ) 