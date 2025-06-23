"""
Unit tests for tool calling functionality.
"""
import pytest
import inspect
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, List, Any

from core.ai_providers import GeminiProvider, PlaceholderProvider, BaseAIProvider
from core.ai_provider_manager import AIProviderManager
from core.tools import JeevesTools
from core.chat_manager import ChatManager
from core.database import DatabaseManager


# Test tool functions
def get_current_time() -> str:
    """Get the current time and date."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers."""
    return a + b


def get_weather(location: str) -> str:
    """Get weather information for a location."""
    weather_data = {
        "New York": "Sunny, 72°F",
        "London": "Rainy, 55°F",
        "Tokyo": "Cloudy, 68°F"
    }
    return weather_data.get(location, f"Weather data not available for {location}")


def log_thought(thought: str) -> str:
    """Log a thought for internal planning."""
    return f"Thought logged: {thought}"


def complex_tool(param1: str, param2: int, optional_param: bool = False) -> dict:
    """A complex tool with multiple parameters."""
    return {
        "param1": param1,
        "param2": param2,
        "optional_param": optional_param,
        "result": f"Processed {param1} with {param2}"
    }


def tool_with_error() -> str:
    """A tool that raises an exception."""
    raise ValueError("This is a test error")


class TestThreadIdentifierResolution:
    """Test thread identifier resolution functionality."""
    
    @pytest.fixture
    def setup_tools(self, tmp_path):
        """Set up tools with test database."""
        db_path = tmp_path / "test.db"
        db_manager = DatabaseManager(str(db_path))
        chat_manager = ChatManager(db_manager)
        tools = JeevesTools(chat_manager)
        
        yield tools, chat_manager, db_manager
        
        # Cleanup: close database connections
        try:
            db_manager.close_connections()
        except:
            pass
    
    def test_resolve_thread_identifier_with_id(self, setup_tools):
        """Test resolving thread identifier with direct ID."""
        tools, chat_manager, db_manager = setup_tools
        
        # Create a test thread
        thread_id = chat_manager.create_thread("Test Thread", "🧪")
        
        # Test ID resolution
        result = tools._resolve_thread_identifier(str(thread_id))
        assert result == thread_id
    
    def test_resolve_thread_identifier_with_name_unique(self, setup_tools):
        """Test resolving thread identifier with unique name."""
        tools, chat_manager, db_manager = setup_tools
        
        # Create a test thread
        thread_id = chat_manager.create_thread("Unique Thread Name", "🧪")
        
        # Test name resolution
        result = tools._resolve_thread_identifier("Unique Thread Name")
        assert result == thread_id
    
    def test_resolve_thread_identifier_with_name_partial_match(self, setup_tools):
        """Test resolving thread identifier with partial name match."""
        tools, chat_manager, db_manager = setup_tools
        
        # Create a test thread
        thread_id = chat_manager.create_thread("Project Planning Meeting", "📋")
        
        # Test partial name resolution
        result = tools._resolve_thread_identifier("Project Planning")
        assert result == thread_id
    
    def test_resolve_thread_identifier_with_name_case_insensitive(self, setup_tools):
        """Test resolving thread identifier with case-insensitive name."""
        tools, chat_manager, db_manager = setup_tools
        
        # Create a test thread
        thread_id = chat_manager.create_thread("Bug Fixes", "🐛")
        
        # Test case-insensitive name resolution
        result = tools._resolve_thread_identifier("bug fixes")
        assert result == thread_id
    
    def test_resolve_thread_identifier_with_ambiguous_name(self, setup_tools):
        """Test resolving thread identifier with ambiguous name raises error."""
        tools, chat_manager, db_manager = setup_tools
        
        # Create multiple threads with similar names
        thread1_id = chat_manager.create_thread("Project Planning", "📋")
        thread2_id = chat_manager.create_thread("Project Planning Backup", "📋")
        
        # Test ambiguous name resolution
        with pytest.raises(ValueError) as exc_info:
            tools._resolve_thread_identifier("Project Planning")
        
        error_msg = str(exc_info.value)
        assert "Multiple threads found matching" in error_msg
        assert str(thread1_id) in error_msg
        assert str(thread2_id) in error_msg
        assert "Please specify the exact thread ID" in error_msg
    
    def test_resolve_thread_identifier_with_none_current_thread(self, setup_tools):
        """Test resolving thread identifier with None (current thread)."""
        tools, chat_manager, db_manager = setup_tools
        
        # Create a test thread and switch to it
        thread_id = chat_manager.create_thread("Current Thread", "💬")
        chat_manager.switch_thread(thread_id)
        
        # Test None resolution (current thread)
        result = tools._resolve_thread_identifier(None)
        assert result == thread_id
    
    def test_resolve_thread_identifier_with_none_no_current_thread(self, setup_tools):
        """Test resolving thread identifier with None when no current thread."""
        tools, chat_manager, db_manager = setup_tools
        
        # Test None resolution when no current thread
        result = tools._resolve_thread_identifier(None)
        assert result is None
    
    def test_resolve_thread_identifier_with_nonexistent_id(self, setup_tools):
        """Test resolving thread identifier with non-existent ID."""
        tools, chat_manager, db_manager = setup_tools
        
        # Test non-existent ID resolution
        result = tools._resolve_thread_identifier("99999")
        assert result is None
    
    def test_resolve_thread_identifier_with_nonexistent_name(self, setup_tools):
        """Test resolving thread identifier with non-existent name."""
        tools, chat_manager, db_manager = setup_tools
        
        # Test non-existent name resolution
        result = tools._resolve_thread_identifier("Non-existent Thread")
        assert result is None
    
    def test_rename_chat_thread_with_id(self, setup_tools):
        """Test rename_chat_thread with thread ID."""
        tools, chat_manager, db_manager = setup_tools
        
        # Create a test thread
        thread_id = chat_manager.create_thread("Old Name", "🧪")
        
        # Test renaming with ID
        result = tools.rename_chat_thread(str(thread_id), "New Name")
        assert "Successfully renamed" in result
        
        # Verify the thread was renamed
        thread = chat_manager.get_thread(thread_id)
        assert thread["name"] == "New Name"
    
    def test_rename_chat_thread_with_name(self, setup_tools):
        """Test rename_chat_thread with thread name."""
        tools, chat_manager, db_manager = setup_tools
        
        # Create a test thread
        thread_id = chat_manager.create_thread("Old Name", "🧪")
        
        # Test renaming with name
        result = tools.rename_chat_thread("Old Name", "New Name")
        assert "Successfully renamed" in result
        
        # Verify the thread was renamed
        thread = chat_manager.get_thread(thread_id)
        assert thread["name"] == "New Name"
    
    def test_rename_chat_thread_with_ambiguous_name(self, setup_tools):
        """Test rename_chat_thread with ambiguous name returns error."""
        tools, chat_manager, db_manager = setup_tools
        
        # Create multiple threads with similar names
        chat_manager.create_thread("Project Planning", "📋")
        chat_manager.create_thread("Project Planning Backup", "📋")
        
        # Test renaming with ambiguous name
        result = tools.rename_chat_thread("Project Planning", "New Name")
        assert "Error:" in result
        assert "Multiple threads found matching" in result
    
    def test_rename_chat_thread_with_nonexistent_identifier(self, setup_tools):
        """Test rename_chat_thread with non-existent identifier."""
        tools, chat_manager, db_manager = setup_tools
        
        # Test renaming with non-existent ID
        result = tools.rename_chat_thread("99999", "New Name")
        assert "Thread '99999' not found" in result
        
        # Test renaming with non-existent name
        result = tools.rename_chat_thread("Non-existent Thread", "New Name")
        assert "Thread 'Non-existent Thread' not found" in result
    
    def test_rename_chat_thread_with_empty_name(self, setup_tools):
        """Test rename_chat_thread with empty name."""
        tools, chat_manager, db_manager = setup_tools
        
        # Create a test thread
        thread_id = chat_manager.create_thread("Test Thread", "🧪")
        
        # Test renaming with empty name
        result = tools.rename_chat_thread(str(thread_id), "")
        assert "Error:" in result
        assert "New name cannot be empty" in result
    
    def test_search_chat_history_with_thread_id(self, setup_tools):
        """Test search_chat_history with thread ID."""
        tools, chat_manager, db_manager = setup_tools
        
        # Create a test thread and add messages
        thread_id = chat_manager.create_thread("Test Thread", "🧪")
        chat_manager.switch_thread(thread_id)
        chat_manager.add_user_message("Hello world")
        chat_manager.add_ai_message("Hi there!")
        
        # Test searching with thread ID
        result = tools.search_chat_history("Hello", thread_identifier=str(thread_id))
        assert "Found" in result
        assert "Hello world" in result
    
    def test_search_chat_history_with_thread_name(self, setup_tools):
        """Test search_chat_history with thread name."""
        tools, chat_manager, db_manager = setup_tools
        
        # Create a test thread and add messages
        thread_id = chat_manager.create_thread("Test Thread", "🧪")
        chat_manager.switch_thread(thread_id)
        chat_manager.add_user_message("Hello world")
        chat_manager.add_ai_message("Hi there!")
        
        # Test searching with thread name
        result = tools.search_chat_history("Hello", thread_identifier="Test Thread")
        assert "Found" in result
        assert "Hello world" in result
    
    def test_search_chat_history_with_ambiguous_name(self, setup_tools):
        """Test search_chat_history with ambiguous name returns error."""
        tools, chat_manager, db_manager = setup_tools
        
        # Create multiple threads with similar names
        chat_manager.create_thread("Project Planning", "📋")
        chat_manager.create_thread("Project Planning Backup", "📋")
        
        # Test searching with ambiguous name
        result = tools.search_chat_history("test", thread_identifier="Project Planning")
        assert "Error:" in result
        assert "Multiple threads found matching" in result
    
    def test_search_chat_history_with_nonexistent_identifier(self, setup_tools):
        """Test search_chat_history with non-existent identifier."""
        tools, chat_manager, db_manager = setup_tools
        
        # Test searching with non-existent ID
        result = tools.search_chat_history("test", thread_identifier="99999")
        assert "Thread '99999' not found" in result
        
        # Test searching with non-existent name
        result = tools.search_chat_history("test", thread_identifier="Non-existent Thread")
        assert "Thread 'Non-existent Thread' not found" in result
    
    def test_export_current_conversation_with_thread_id(self, setup_tools):
        """Test export_current_conversation with thread ID."""
        tools, chat_manager, db_manager = setup_tools
        
        # Create a test thread and add messages
        thread_id = chat_manager.create_thread("Test Thread", "🧪")
        chat_manager.switch_thread(thread_id)
        chat_manager.add_user_message("Hello world")
        chat_manager.add_ai_message("Hi there!")
        
        # Test exporting with thread ID
        result = tools.export_current_conversation(thread_identifier=str(thread_id), format="json")
        assert "Successfully exported" in result
    
    def test_export_current_conversation_with_thread_name(self, setup_tools):
        """Test export_current_conversation with thread name."""
        tools, chat_manager, db_manager = setup_tools
        
        # Create a test thread and add messages
        thread_id = chat_manager.create_thread("Test Thread", "🧪")
        chat_manager.switch_thread(thread_id)
        chat_manager.add_user_message("Hello world")
        chat_manager.add_ai_message("Hi there!")
        
        # Test exporting with thread name
        result = tools.export_current_conversation(thread_identifier="Test Thread", format="json")
        assert "Successfully exported" in result
    
    def test_export_current_conversation_with_ambiguous_name(self, setup_tools):
        """Test export_current_conversation with ambiguous name returns error."""
        tools, chat_manager, db_manager = setup_tools
        
        # Create multiple threads with similar names
        chat_manager.create_thread("Project Planning", "📋")
        chat_manager.create_thread("Project Planning Backup", "📋")
        
        # Test exporting with ambiguous name
        result = tools.export_current_conversation(thread_identifier="Project Planning", format="json")
        assert "Error:" in result
        assert "Multiple threads found matching" in result
    
    def test_export_current_conversation_with_nonexistent_identifier(self, setup_tools):
        """Test export_current_conversation with non-existent identifier."""
        tools, chat_manager, db_manager = setup_tools
        
        # Test exporting with non-existent ID
        result = tools.export_current_conversation(thread_identifier="99999", format="json")
        assert "Thread '99999' not found" in result
        
        # Test exporting with non-existent name
        result = tools.export_current_conversation(thread_identifier="Non-existent Thread", format="json")
        assert "Thread 'Non-existent Thread' not found" in result
    
    def test_export_current_conversation_with_none_no_current_thread(self, setup_tools):
        """Test export_current_conversation with None when no current thread."""
        tools, chat_manager, db_manager = setup_tools
        
        # Test exporting with None when no current thread
        result = tools.export_current_conversation(thread_identifier=None, format="json")
        assert "No active thread to export" in result


class TestBaseProviderToolCalling:
    """Test tool calling functionality in BaseAIProvider."""
    
    def test_base_provider_tool_registration(self):
        """Test tool registration in base provider."""
        # Create a concrete implementation for testing
        class TestProvider(BaseAIProvider):
            def initialize(self) -> bool:
                return True
            
            def generate_response(self, user_message: str, context: List[Dict] = None) -> str:
                return "Test response"
            
            def is_available(self) -> bool:
                return True
        
        provider = TestProvider()
        
        # Test tool registration
        result = provider.register_tool("test_tool", get_current_time)
        assert result is True
        assert "test_tool" in provider.registered_tools
        assert provider.registered_tools["test_tool"] == get_current_time
    
    def test_base_provider_tool_unregistration(self):
        """Test tool unregistration in base provider."""
        class TestProvider(BaseAIProvider):
            def initialize(self) -> bool:
                return True
            
            def generate_response(self, user_message: str, context: List[Dict] = None) -> str:
                return "Test response"
            
            def is_available(self) -> bool:
                return True
        
        provider = TestProvider()
        
        # Register a tool
        provider.register_tool("test_tool", get_current_time)
        assert "test_tool" in provider.registered_tools
        
        # Unregister the tool
        result = provider.unregister_tool("test_tool")
        assert result is True
        assert "test_tool" not in provider.registered_tools
    
    def test_base_provider_tool_unregistration_not_found(self):
        """Test unregistering a non-existent tool."""
        class TestProvider(BaseAIProvider):
            def initialize(self) -> bool:
                return True
            
            def generate_response(self, user_message: str, context: List[Dict] = None) -> str:
                return "Test response"
            
            def is_available(self) -> bool:
                return True
        
        provider = TestProvider()
        
        result = provider.unregister_tool("non_existent")
        assert result is False
    
    def test_base_provider_get_registered_tools(self):
        """Test getting registered tools."""
        class TestProvider(BaseAIProvider):
            def initialize(self) -> bool:
                return True
            
            def generate_response(self, user_message: str, context: List[Dict] = None) -> str:
                return "Test response"
            
            def is_available(self) -> bool:
                return True
        
        provider = TestProvider()
        
        # Register multiple tools
        provider.register_tool("tool1", get_current_time)
        provider.register_tool("tool2", calculate_sum)
        
        tools = provider.get_registered_tools()
        
        assert len(tools) == 2
        assert "tool1" in tools
        assert "tool2" in tools
        assert tools["tool1"] == get_current_time
        assert tools["tool2"] == calculate_sum
    
    def test_base_provider_execute_tool(self):
        """Test tool execution."""
        class TestProvider(BaseAIProvider):
            def initialize(self) -> bool:
                return True
            
            def generate_response(self, user_message: str, context: List[Dict] = None) -> str:
                return "Test response"
            
            def is_available(self) -> bool:
                return True
        
        provider = TestProvider()
        provider.register_tool("calculate_sum", calculate_sum)
        
        result = provider.execute_tool("calculate_sum", {"a": 5, "b": 3})
        assert result == 8
    
    def test_base_provider_execute_tool_not_registered(self):
        """Test executing a non-registered tool."""
        class TestProvider(BaseAIProvider):
            def initialize(self) -> bool:
                return True
            
            def generate_response(self, user_message: str, context: List[Dict] = None) -> str:
                return "Test response"
            
            def is_available(self) -> bool:
                return True
        
        provider = TestProvider()
        
        with pytest.raises(KeyError, match="Tool 'non_existent' is not registered"):
            provider.execute_tool("non_existent", {})
    
    def test_base_provider_execute_tool_with_error(self):
        """Test tool execution that raises an exception."""
        class TestProvider(BaseAIProvider):
            def initialize(self) -> bool:
                return True
            
            def generate_response(self, user_message: str, context: List[Dict] = None) -> str:
                return "Test response"
            
            def is_available(self) -> bool:
                return True
        
        provider = TestProvider()
        provider.register_tool("error_tool", tool_with_error)
        
        with pytest.raises(ValueError, match="This is a test error"):
            provider.execute_tool("error_tool", {})
    
    def test_base_provider_tool_config(self):
        """Test tool configuration management."""
        class TestProvider(BaseAIProvider):
            def initialize(self) -> bool:
                return True
            
            def generate_response(self, user_message: str, context: List[Dict] = None) -> str:
                return "Test response"
            
            def is_available(self) -> bool:
                return True
        
        provider = TestProvider()
        
        config = {"max_tools": 5, "timeout": 30}
        provider.set_tool_config(config)
        
        retrieved_config = provider.get_tool_config()
        assert retrieved_config == config
    
    def test_base_provider_get_provider_info_with_tools(self):
        """Test provider info includes tool information."""
        class TestProvider(BaseAIProvider):
            def initialize(self) -> bool:
                return True
            
            def generate_response(self, user_message: str, context: List[Dict] = None) -> str:
                return "Test response"
            
            def is_available(self) -> bool:
                return True
        
        provider = TestProvider()
        provider.register_tool("test_tool", get_current_time)
        provider.set_tool_config({"test": "config"})
        
        info = provider.get_provider_info()
        
        assert "registered_tools" in info
        assert "tool_config" in info
        assert "test_tool" in info["registered_tools"]
        assert info["tool_config"] == {"test": "config"}
    
    def test_base_provider_cleanup_with_tools(self):
        """Test cleanup clears tools."""
        class TestProvider(BaseAIProvider):
            def initialize(self) -> bool:
                return True
            
            def generate_response(self, user_message: str, context: List[Dict] = None) -> str:
                return "Test response"
            
            def is_available(self) -> bool:
                return True
        
        provider = TestProvider()
        provider.register_tool("test_tool", get_current_time)
        provider.set_tool_config({"test": "config"})
        
        provider.cleanup()
        
        assert len(provider.registered_tools) == 0
        assert len(provider.tool_config) == 0


class TestGeminiProviderToolCalling:
    """Test tool calling functionality in GeminiProvider."""
    
    @patch('google.genai.Client')
    def test_gemini_provider_tool_registration(self, mock_client_class):
        """Test tool registration in Gemini provider."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_models = [Mock(), Mock()]
        mock_client.models.list.return_value = mock_models
        
        provider = GeminiProvider({'api_key': 'test_key'})
        provider.initialize()
        
        # Test tool registration
        result = provider.register_tool("test_tool", get_current_time)
        assert result is True
        assert "test_tool" in provider.registered_tools
    
    @patch('google.genai.Client')
    def test_gemini_provider_build_tools_config(self, mock_client_class):
        """Test tools configuration building."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_models = [Mock(), Mock()]
        mock_client.models.list.return_value = mock_models
        
        provider = GeminiProvider({'api_key': 'test_key'})
        provider.initialize()
        
        # Register tools
        provider.register_tool("calculate_sum", calculate_sum)
        provider.register_tool("get_weather", get_weather)
        
        tools_config = provider._build_tools_config()
        
        assert len(tools_config) == 2
        # Current implementation returns Python functions directly
        assert calculate_sum in tools_config
        assert get_weather in tools_config
    
    @patch('google.genai.Client')
    def test_gemini_provider_build_automatic_function_calling_config(self, mock_client_class):
        """Test automatic function calling configuration building."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_models = [Mock(), Mock()]
        mock_client.models.list.return_value = mock_models
        
        provider = GeminiProvider({
            'api_key': 'test_key',
            'automatic_function_calling': True,
            'max_tool_calls': 3
        })
        provider.initialize()
        
        config = provider._build_automatic_function_calling_config()
        
        assert config is not None
        assert config.disable is False
        assert config.maximum_remote_calls == 3
    
    @patch('google.genai.Client')
    def test_gemini_provider_build_automatic_function_calling_config_disabled(self, mock_client_class):
        """Test automatic function calling configuration when disabled."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_models = [Mock(), Mock()]
        mock_client.models.list.return_value = mock_models
        
        provider = GeminiProvider({
            'api_key': 'test_key',
            'automatic_function_calling': False,
            'max_tool_calls': 3
        })
        provider.initialize()
        
        config = provider._build_automatic_function_calling_config()
        
        assert config is not None
        assert config.disable is True
    
    @patch('google.genai.Client')
    def test_gemini_provider_generate_response_with_tools(self, mock_client_class):
        """Test response generation with tools enabled."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_models = [Mock(), Mock()]
        mock_client.models.list.return_value = mock_models
        
        # Mock response without function calls
        mock_response = Mock()
        mock_response.text = "This is a test response"
        mock_response.function_calls = []
        mock_client.models.generate_content.return_value = mock_response
        
        provider = GeminiProvider({
            'api_key': 'test_key',
            'enable_tool_calling': True
        })
        provider.initialize()
        
        # Register a tool
        provider.register_tool("calculate_sum", calculate_sum)
        
        response = provider.generate_response("What is 5 + 3?")
        
        assert response == "This is a test response"
        # Verify that tools were included in the generation config
        mock_client.models.generate_content.assert_called_once()
        call_args = mock_client.models.generate_content.call_args
        config = call_args[1]['config']
        assert hasattr(config, 'tools')
        assert len(config.tools) > 0
    
    @patch('google.genai.Client')
    def test_gemini_provider_generate_response_with_function_calls(self, mock_client_class):
        """Test response generation with actual function calls."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_models = [Mock(), Mock()]
        mock_client.models.list.return_value = mock_models
        
        # With automatic function calling, Gemini handles tool execution internally
        # and returns the final response directly
        mock_response = Mock()
        mock_response.text = "The sum of 5 and 3 is 8"
        
        mock_client.models.generate_content.return_value = mock_response
        
        provider = GeminiProvider({
            'api_key': 'test_key',
            'enable_tool_calling': True
        })
        provider.initialize()
        
        # Register the tool
        provider.register_tool("calculate_sum", calculate_sum)
        
        response = provider.generate_response("What is 5 + 3?")
        
        assert "The sum of 5 and 3 is 8" in response
        # Verify that generate_content was called once (automatic function calling)
        assert mock_client.models.generate_content.call_count == 1
    
    @patch('google.genai.Client')
    def test_gemini_provider_generate_response_tool_calling_disabled(self, mock_client_class):
        """Test response generation with tool calling disabled."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_models = [Mock(), Mock()]
        mock_client.models.list.return_value = mock_models
        
        mock_response = Mock()
        mock_response.text = "This is a test response"
        mock_response.function_calls = []  # Empty function calls list
        mock_client.models.generate_content.return_value = mock_response
        
        provider = GeminiProvider({
            'api_key': 'test_key',
            'enable_tool_calling': False
        })
        provider.initialize()
        
        # Register a tool (should be ignored)
        provider.register_tool("calculate_sum", calculate_sum)
        
        response = provider.generate_response("What is 5 + 3?")
        
        assert response == "This is a test response"
        # Verify that tools were NOT included in the generation config
        mock_client.models.generate_content.assert_called_once()
        call_args = mock_client.models.generate_content.call_args
        config = call_args[1]['config']
        assert not hasattr(config, 'tools') or config.tools is None
    
    @patch('google.genai.Client')
    def test_gemini_provider_handle_function_calls_with_error(self, mock_client_class):
        """Test function call handling when tool execution fails."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_models = [Mock(), Mock()]
        mock_client.models.list.return_value = mock_models
        
        # With automatic function calling, Gemini handles tool execution internally
        # and returns the final response directly, even when tools fail
        mock_response = Mock()
        mock_response.text = "There was an error executing the tool"
        
        mock_client.models.generate_content.return_value = mock_response
        
        provider = GeminiProvider({
            'api_key': 'test_key',
            'enable_tool_calling': True
        })
        provider.initialize()
        
        # Register a tool that raises an error
        provider.register_tool("error_tool", tool_with_error)
        
        response = provider.generate_response("Test error handling")
        
        assert "There was an error executing the tool" in response
    
    def test_gemini_provider_validate_config_with_tool_calling(self):
        """Test configuration validation with tool calling settings."""
        provider = GeminiProvider({
            'api_key': 'test_key',
            'max_tool_calls': 5
        })
        
        assert provider.validate_config() is True
    
    def test_gemini_provider_validate_config_invalid_max_tool_calls(self):
        """Test configuration validation with invalid max_tool_calls."""
        provider = GeminiProvider({
            'api_key': 'test_key',
            'max_tool_calls': 0  # Invalid
        })
        
        assert provider.validate_config() is False
    
    def test_gemini_provider_validate_config_negative_max_tool_calls(self):
        """Test configuration validation with negative max_tool_calls."""
        provider = GeminiProvider({
            'api_key': 'test_key',
            'max_tool_calls': -1  # Invalid
        })
        
        assert provider.validate_config() is False
    
    @patch('google.genai.Client')
    def test_gemini_provider_get_provider_info_with_tool_calling(self, mock_client_class):
        """Test provider info includes tool calling information."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_models = [Mock(), Mock()]
        mock_client.models.list.return_value = mock_models
        
        provider = GeminiProvider({
            'api_key': 'test_key',
            'enable_tool_calling': True,
            'automatic_function_calling': True,
            'max_tool_calls': 5
        })
        provider.initialize()
        
        info = provider.get_provider_info()
        
        assert info['enable_tool_calling'] is True
        assert info['automatic_function_calling'] is True
        assert info['max_tool_calls'] == 5


class TestAIProviderManagerToolCalling:
    """Test tool calling functionality in AIProviderManager."""
    
    def test_provider_manager_tool_registration(self):
        """Test tool registration in provider manager."""
        manager = AIProviderManager()
        
        # Test tool registration
        result = manager.register_tool("test_tool", get_current_time)
        assert result is True
        assert "test_tool" in manager.registered_tools
    
    def test_provider_manager_tool_unregistration(self):
        """Test tool unregistration in provider manager."""
        manager = AIProviderManager()
        
        # Register a tool
        manager.register_tool("test_tool", get_current_time)
        assert "test_tool" in manager.registered_tools
        
        # Unregister the tool
        result = manager.unregister_tool("test_tool")
        assert result is True
        assert "test_tool" not in manager.registered_tools
    
    def test_provider_manager_tool_unregistration_not_found(self):
        """Test unregistering a non-existent tool."""
        manager = AIProviderManager()
        
        result = manager.unregister_tool("non_existent")
        assert result is False
    
    def test_provider_manager_get_registered_tools(self):
        """Test getting registered tools."""
        manager = AIProviderManager()
        
        # Register multiple tools
        manager.register_tool("tool1", get_current_time)
        manager.register_tool("tool2", calculate_sum)
        
        tools = manager.get_registered_tools()
        
        assert len(tools) == 2
        assert "tool1" in tools
        assert "tool2" in tools
        assert tools["tool1"] == get_current_time
        assert tools["tool2"] == calculate_sum
    
    def test_provider_manager_execute_tool(self):
        """Test tool execution through manager."""
        manager = AIProviderManager()
        manager.register_tool("calculate_sum", calculate_sum)
        
        result = manager.execute_tool("calculate_sum", {"a": 5, "b": 3})
        assert result == 8
    
    def test_provider_manager_execute_tool_not_registered(self):
        """Test executing a non-registered tool through manager."""
        manager = AIProviderManager()
        
        with pytest.raises(KeyError, match="Tool 'non_existent' is not registered"):
            manager.execute_tool("non_existent", {})
    
    @patch('google.genai.Client')
    def test_provider_manager_initialize_with_tools(self, mock_client_class):
        """Test provider manager initialization with tools."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_models = [Mock(), Mock()]
        mock_client.models.list.return_value = mock_models
        
        manager = AIProviderManager()
        
        # Register tools before initialization
        manager.register_tool("calculate_sum", calculate_sum)
        manager.register_tool("get_weather", get_weather)
        
        result = manager.initialize()
        
        assert result is True
        assert manager.current_provider is not None
        
        # Check that tools were registered with the current provider
        current_provider_tools = manager.current_provider.get_registered_tools()
        assert "calculate_sum" in current_provider_tools
        assert "get_weather" in current_provider_tools
    
    @patch('google.genai.Client')
    def test_provider_manager_switch_provider_with_tools(self, mock_client_class):
        """Test provider switching with tools."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_models = [Mock(), Mock()]
        mock_client.models.list.return_value = mock_models
        
        manager = AIProviderManager()
        manager.initialize()
        
        # Register tools
        manager.register_tool("calculate_sum", calculate_sum)
        manager.register_tool("get_weather", get_weather)
        
        # Switch to placeholder provider
        result = manager.switch_provider("placeholder")
        
        assert result is True
        assert manager.current_provider.provider_name == "PlaceholderProvider"
        
        # Check that tools were registered with the new provider
        current_provider_tools = manager.current_provider.get_registered_tools()
        assert "calculate_sum" in current_provider_tools
        assert "get_weather" in current_provider_tools
    
    def test_provider_manager_add_provider_with_tools(self):
        """Test adding a provider with existing tools."""
        manager = AIProviderManager()
        
        # Register tools first
        manager.register_tool("calculate_sum", calculate_sum)
        manager.register_tool("get_weather", get_weather)
        
        # Add a new provider
        new_provider = PlaceholderProvider()
        new_provider.initialize = Mock(return_value=True)
        
        result = manager.add_provider("test_provider", new_provider)
        
        assert result is True
        assert "test_provider" in manager.providers
        
        # Check that tools were registered with the new provider
        new_provider_tools = new_provider.get_registered_tools()
        assert "calculate_sum" in new_provider_tools
        assert "get_weather" in new_provider_tools
    
    def test_provider_manager_cleanup_with_tools(self):
        """Test cleanup clears tools."""
        manager = AIProviderManager()
        
        # Register tools
        manager.register_tool("calculate_sum", calculate_sum)
        manager.register_tool("get_weather", get_weather)
        
        manager.cleanup()
        
        assert len(manager.registered_tools) == 0
    
    def test_provider_manager_str_representation_with_tools(self):
        """Test string representation includes tool count."""
        manager = AIProviderManager()
        
        # Register tools
        manager.register_tool("calculate_sum", calculate_sum)
        manager.register_tool("get_weather", get_weather)
        
        str_repr = str(manager)
        
        assert "tools=2" in str_repr


class TestToolCallingIntegration:
    """Integration tests for tool calling functionality."""
    
    @patch('google.genai.Client')
    def test_full_tool_calling_workflow(self, mock_client_class):
        """Test complete tool calling workflow."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_models = [Mock(), Mock()]
        mock_client.models.list.return_value = mock_models
        
        # With automatic function calling, Gemini handles tool execution internally
        # and returns the final response directly
        mock_response = Mock()
        mock_response.text = "The sum of 10 and 20 is 30"
        
        mock_client.models.generate_content.return_value = mock_response
        
        # Create manager and register tools
        manager = AIProviderManager()
        manager.register_tool("calculate_sum", calculate_sum)
        manager.register_tool("get_weather", get_weather)
        manager.register_tool("get_current_time", get_current_time)
        
        # Initialize
        result = manager.initialize()
        assert result is True
        
        # Test response generation
        response = manager.generate_response("What is 10 + 20?")
        
        assert "The sum of 10 and 20 is 30" in response
        assert mock_client.models.generate_content.call_count == 1
    
    @patch('google.genai.Client')
    def test_multiple_tool_calls_in_single_request(self, mock_client_class):
        """Test multiple tool calls in a single request."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_models = [Mock(), Mock()]
        mock_client.models.list.return_value = mock_models
        
        # With automatic function calling, Gemini handles multiple tool calls internally
        # and returns the final response directly
        mock_response = Mock()
        mock_response.text = "The sum is 8 and the current time is 2024-01-01 12:00:00"
        
        mock_client.models.generate_content.return_value = mock_response
        
        # Create manager and register tools
        manager = AIProviderManager()
        manager.register_tool("calculate_sum", calculate_sum)
        manager.register_tool("get_current_time", get_current_time)
        
        # Initialize
        manager.initialize()
        
        # Test response generation
        response = manager.generate_response("What is 5 + 3 and what time is it?")
        
        assert "The sum is 8" in response
        assert "current time" in response
        assert mock_client.models.generate_content.call_count == 1
    
    @patch('google.genai.Client')
    def test_tool_calling_with_context(self, mock_client_class):
        """Test tool calling with conversation context."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_models = [Mock(), Mock()]
        mock_client.models.list.return_value = mock_models
        
        # With automatic function calling, Gemini handles tool execution internally
        # and returns the final response directly
        mock_response = Mock()
        mock_response.text = "The weather in New York is Sunny, 72°F"
        
        mock_client.models.generate_content.return_value = mock_response
        
        # Create manager and register tools
        manager = AIProviderManager()
        manager.register_tool("get_weather", get_weather)
        
        # Initialize
        manager.initialize()
        
        # Test with context
        context = [
            {'sender': 'user', 'content': 'I need weather information'},
            {'sender': 'assistant', 'content': 'I can help you with that. What city?'}
        ]
        
        response = manager.generate_response("New York", context)
        
        assert "The weather in New York is Sunny, 72°F" in response
        assert mock_client.models.generate_content.call_count == 1
    
    def test_tool_calling_error_handling(self):
        """Test error handling in tool calling."""
        manager = AIProviderManager()
        
        # Register a tool that raises an error
        manager.register_tool("error_tool", tool_with_error)
        
        # Test direct execution
        with pytest.raises(ValueError, match="This is a test error"):
            manager.execute_tool("error_tool", {})
        
        # Test through provider (should handle gracefully)
        manager.initialize()
        
        # The placeholder provider should handle this gracefully
        response = manager.generate_response("Test error handling")
        assert isinstance(response, str)
        assert len(response) > 0


class TestToolCallingEdgeCases:
    """Test edge cases and error conditions in tool calling."""
    
    def test_tool_with_complex_parameters(self):
        """Test tool with complex parameter types."""
        manager = AIProviderManager()
        
        def complex_tool_with_lists(items: list, count: int = 5) -> str:
            """A tool with list parameters."""
            return f"Processed {len(items)} items, showing {count}"
        
        manager.register_tool("complex_tool", complex_tool_with_lists)
        
        result = manager.execute_tool("complex_tool", {
            "items": ["a", "b", "c"],
            "count": 2
        })
        
        assert result == "Processed 3 items, showing 2"
    
    def test_tool_with_dict_parameters(self):
        """Test tool with dictionary parameters."""
        manager = AIProviderManager()
        
        def dict_tool(data: dict, key: str) -> str:
            """A tool with dictionary parameters."""
            return data.get(key, "Not found")
        
        manager.register_tool("dict_tool", dict_tool)
        
        result = manager.execute_tool("dict_tool", {
            "data": {"name": "John", "age": 30},
            "key": "name"
        })
        
        assert result == "John"
    
    def test_tool_with_no_parameters(self):
        """Test tool with no parameters."""
        manager = AIProviderManager()
        
        def no_param_tool() -> str:
            """A tool with no parameters."""
            return "No parameters needed"
        
        manager.register_tool("no_param_tool", no_param_tool)
        
        result = manager.execute_tool("no_param_tool", {})
        assert result == "No parameters needed"
    
    def test_tool_registration_with_description(self):
        """Test tool registration with custom description."""
        manager = AIProviderManager()
        
        result = manager.register_tool(
            "custom_tool", 
            get_current_time, 
            "Custom description for the tool"
        )
        
        assert result is True
        assert "custom_tool" in manager.registered_tools
    
    def test_tool_registration_duplicate(self):
        """Test registering the same tool twice."""
        manager = AIProviderManager()
        
        # Register tool first time
        result1 = manager.register_tool("test_tool", get_current_time)
        assert result1 is True
        
        # Register same tool again (should overwrite)
        result2 = manager.register_tool("test_tool", calculate_sum)
        assert result2 is True
        
        # Should now be the second function
        tools = manager.get_registered_tools()
        assert tools["test_tool"] == calculate_sum
    
    def test_tool_execution_with_wrong_parameters(self):
        """Test tool execution with incorrect parameters."""
        manager = AIProviderManager()
        manager.register_tool("calculate_sum", calculate_sum)
        
        # Test with missing parameters
        with pytest.raises(TypeError):
            manager.execute_tool("calculate_sum", {"a": 5})  # Missing 'b'
        
        # Test with wrong parameter types
        with pytest.raises(TypeError):
            manager.execute_tool("calculate_sum", {"a": "invalid", "b": 3})
    
    def test_tool_execution_with_extra_parameters(self):
        """Test tool execution with extra parameters."""
        manager = AIProviderManager()
        manager.register_tool("calculate_sum", calculate_sum)
        
        # Should work fine - extra parameters are ignored
        result = manager.execute_tool("calculate_sum", {
            "a": 5, 
            "b": 3, 
            "extra_param": "ignored"
        })
        
        assert result == 8

    def test_read_file_returns_attachment_format_for_attachments(self):
        """Test that read_file returns appropriate message for attachment files."""
        # Create a test database manager
        from src.core.database import DatabaseManager
        db_manager = DatabaseManager(":memory:")
        
        # Create a test chat manager
        chat_manager = ChatManager(db_manager)
        
        # Create tools instance
        tools = JeevesTools(chat_manager)
        
        # Test with an attachment file path
        result = tools.read_file("attachments/test_image.png")
        
        # Should return a message instructing to use attach button
        assert "attachments directory" in result
        assert "Attach File" in result
        assert "button" in result 