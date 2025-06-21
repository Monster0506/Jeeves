"""
Unit tests for AI providers.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from core.ai_providers import GeminiProvider, PlaceholderProvider, BaseAIProvider
from typing import List, Dict
from datetime import datetime


# Test tool functions for tool calling tests
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


def tool_with_error() -> str:
    """A tool that raises an exception."""
    raise ValueError("This is a test error")


class TestBaseAIProvider:
    """Test base AI provider functionality."""
    
    def test_base_provider_initialization(self):
        """Test base provider initialization."""
        # Create a concrete implementation for testing
        class TestProvider(BaseAIProvider):
            def initialize(self) -> bool:
                return True
            
            def generate_response(self, user_message: str, context: List[Dict] = None) -> str:
                return "Test response"
            
            def is_available(self) -> bool:
                return True
        
        config = {'test_param': 'test_value'}
        provider = TestProvider(config)
        
        assert provider.config == config
        assert provider.is_initialized is False
        assert provider.provider_name == 'TestProvider'
    
    def test_base_provider_cleanup(self):
        """Test base provider cleanup."""
        # Create a concrete implementation for testing
        class TestProvider(BaseAIProvider):
            def initialize(self) -> bool:
                return True
            
            def generate_response(self, user_message: str, context: List[Dict] = None) -> str:
                return "Test response"
            
            def is_available(self) -> bool:
                return True
        
        provider = TestProvider()
        provider.is_initialized = True
        
        provider.cleanup()
        
        assert provider.is_initialized is False
    
    def test_base_provider_get_provider_info(self):
        """Test getting provider information."""
        # Create a concrete implementation for testing
        class TestProvider(BaseAIProvider):
            def initialize(self) -> bool:
                return True
            
            def generate_response(self, user_message: str, context: List[Dict] = None) -> str:
                return "Test response"
            
            def is_available(self) -> bool:
                return True
        
        provider = TestProvider({'test': 'config'})
        info = provider.get_provider_info()
        
        assert info['name'] == 'TestProvider'
        assert info['is_initialized'] is False
        assert info['config'] == {'test': 'config'}


class TestBaseAIProviderToolCalling:
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


class TestPlaceholderProvider:
    """Test the placeholder AI provider."""
    
    def test_placeholder_provider_initialization(self):
        """Test placeholder provider initialization."""
        provider = PlaceholderProvider()
        
        assert provider.provider_name == 'PlaceholderProvider'
        assert provider.is_initialized is False
        assert provider.is_available() is True
    
    def test_placeholder_provider_initialize(self):
        """Test placeholder provider initialization."""
        provider = PlaceholderProvider()
        
        result = provider.initialize()
        
        assert result is True
        assert provider.is_initialized is True
    
    def test_placeholder_provider_generate_response(self):
        """Test placeholder provider response generation."""
        provider = PlaceholderProvider()
        provider.initialize()
        
        response = provider.generate_response("Hello")
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "Jeeves" in response or "assistant" in response.lower()
    
    def test_placeholder_provider_keyword_responses(self):
        """Test placeholder provider keyword-based responses."""
        provider = PlaceholderProvider()
        provider.initialize()
        
        # Test Python keyword
        response = provider.generate_response("Python programming")
        assert "PLACEHOLDER:" in response
        assert len(response) > 0
    
    def test_placeholder_provider_context_handling(self):
        """Test placeholder provider context handling."""
        provider = PlaceholderProvider()
        provider.initialize()
        
        context = [
            {'sender': 'user', 'content': 'Hello'},
            {'sender': 'assistant', 'content': 'Hi there!'}
        ]
        
        response = provider.generate_response("How are you?", context)
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_placeholder_provider_validation(self):
        """Test placeholder provider configuration validation."""
        provider = PlaceholderProvider()
        
        # Placeholder provider should always validate successfully
        assert provider.validate_config() is True
    
    def test_placeholder_provider_availability(self):
        """Test placeholder provider availability."""
        provider = PlaceholderProvider()
        
        # Should be available even before initialization
        assert provider.is_available() is True
        
        # Should still be available after initialization
        provider.initialize()
        assert provider.is_available() is True


class TestPlaceholderProviderToolCalling:
    """Test tool calling functionality in PlaceholderProvider."""
    
    def test_placeholder_provider_tool_registration(self):
        """Test tool registration in placeholder provider."""
        provider = PlaceholderProvider()
        
        # Test tool registration
        result = provider.register_tool("test_tool", get_current_time)
        assert result is True
        assert "test_tool" in provider.registered_tools
        assert provider.registered_tools["test_tool"] == get_current_time
    
    def test_placeholder_provider_tool_execution(self):
        """Test tool execution in placeholder provider."""
        provider = PlaceholderProvider()
        provider.register_tool("calculate_sum", calculate_sum)
        
        result = provider.execute_tool("calculate_sum", {"a": 5, "b": 3})
        assert result == 8
    
    def test_placeholder_provider_generate_response_with_tools(self):
        """Test response generation with tools in placeholder provider."""
        provider = PlaceholderProvider()
        provider.initialize()
        provider.register_tool("calculate_sum", calculate_sum)
        provider.register_tool("get_weather", get_weather)
        
        # The placeholder provider should mention available tools
        response = provider.generate_response("What tools do you have?")
        
        assert isinstance(response, str)
        assert len(response) > 0
        # Should mention that tools are available
        assert "tools" in response.lower() or "functions" in response.lower()


class TestGeminiProvider:
    """Test the Gemini AI provider."""
    
    def test_gemini_provider_initialization(self):
        """Test Gemini provider initialization."""
        config = {
            'api_key': 'test_key',
            'model': 'gemini-2.0-flash',
            'max_output_tokens': 1024,
            'temperature': 0.7
        }
        provider = GeminiProvider(config)
        
        assert provider.provider_name == 'GeminiProvider'
        assert provider.model_name == 'gemini-2.0-flash'
        assert provider.max_output_tokens == 1024
        assert provider.temperature == 0.7
        assert provider.is_initialized is False
    
    def test_gemini_provider_default_config(self):
        """Test Gemini provider with default configuration."""
        provider = GeminiProvider()
        
        assert provider.model_name == 'gemini-2.0-flash'
        assert provider.max_output_tokens == 2048
        assert provider.temperature == 0.7
        assert provider.top_p == 0.95
        assert provider.top_k == 40
        assert provider.system_instruction is not None
    
    def test_gemini_provider_system_prompt(self):
        """Test Gemini provider system prompt."""
        provider = GeminiProvider()
        
        system_prompt = provider._get_default_system_prompt()
        
        assert isinstance(system_prompt, str)
        assert "Jeeves" in system_prompt
        assert "helpful" in system_prompt.lower()
        assert "assistant" in system_prompt.lower()
    
    @patch('google.genai.Client')
    def test_gemini_provider_initialize_success(self, mock_client_class):
        """Test successful Gemini provider initialization."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock models.list() to return a list
        mock_models = [Mock(), Mock()]
        mock_client.models.list.return_value = mock_models
        
        provider = GeminiProvider({'api_key': 'test_key'})
        result = provider.initialize()
        
        assert result is True
        assert provider.is_initialized is True
        mock_client_class.assert_called_once_with(api_key='test_key')
    
    def test_gemini_provider_initialize_no_api_key(self):
        """Test Gemini provider initialization without API key."""
        provider = GeminiProvider()
        
        # Should return True even without API key (validation happens during actual API calls)
        result = provider.initialize()
        assert result is True
    
    def test_gemini_provider_initialize_import_error(self):
        """Test Gemini provider initialization with import error."""
        with patch('google.genai.Client', side_effect=ImportError("No module named 'google'")):
            provider = GeminiProvider()
            result = provider.initialize()
            assert result is False
    
    @patch('google.genai.Client')
    def test_gemini_provider_generate_response(self, mock_client_class):
        """Test Gemini provider response generation."""
        # Mock the client and response
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.text = "This is a test response from Gemini."
        mock_client.models.generate_content.return_value = mock_response
        
        provider = GeminiProvider({'api_key': 'test_key'})
        provider.initialize()
        
        response = provider.generate_response("Hello, how are you?")
        
        assert "This is a test response from Gemini." in response
        mock_client.models.generate_content.assert_called_once()
    
    def test_gemini_provider_generate_response_not_available(self):
        """Test response generation when provider is not available."""
        provider = GeminiProvider()
        
        response = provider.generate_response("Hello")
        
        assert "not available" in response.lower()
    
    @patch('google.genai.Client')
    def test_gemini_provider_generate_response_with_context(self, mock_client_class):
        """Test Gemini provider response generation with context."""
        # Mock the client and response
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.text = "Response with context."
        mock_client.models.generate_content.return_value = mock_response
        
        provider = GeminiProvider({'api_key': 'test_key'})
        provider.initialize()
        
        context = [
            {'sender': 'user', 'content': 'My name is Alice'},
            {'sender': 'assistant', 'content': 'Nice to meet you, Alice!'}
        ]
        
        response = provider.generate_response("What is my name?", context)
        
        assert "Response with context." in response
        # Verify context was passed to generate_content
        call_args = mock_client.models.generate_content.call_args
        assert call_args is not None
    
    @patch('google.genai.Client')
    def test_gemini_provider_generate_response_empty_response(self, mock_client_class):
        """Test handling of empty response from Gemini."""
        # Mock the client and empty response
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.text = ""
        mock_client.models.generate_content.return_value = mock_response
        
        provider = GeminiProvider({'api_key': 'test_key'})
        provider.initialize()
        
        response = provider.generate_response("Hello")
        
        assert "I apologize" in response or "empty" in response.lower()
    
    def test_gemini_provider_validate_config_valid(self):
        """Test Gemini provider configuration validation with valid config."""
        config = {
            'api_key': 'test_key',
            'temperature': 0.5,
            'top_p': 0.9,
            'top_k': 20,
            'max_output_tokens': 1024
        }
        provider = GeminiProvider(config)
        
        assert provider.validate_config() is True
    
    def test_gemini_provider_validate_config_no_api_key(self):
        """Test Gemini provider configuration validation without API key."""
        provider = GeminiProvider()
        
        # Should return True even without API key (validation happens during initialization)
        assert provider.validate_config() is True
    
    def test_gemini_provider_validate_config_invalid_temperature(self):
        """Test Gemini provider configuration validation with invalid temperature."""
        config = {'api_key': 'test_key', 'temperature': 1.5}
        provider = GeminiProvider(config)
        
        assert provider.validate_config() is False
    
    def test_gemini_provider_validate_config_invalid_top_p(self):
        """Test Gemini provider configuration validation with invalid top_p."""
        config = {'api_key': 'test_key', 'top_p': 1.5}
        provider = GeminiProvider(config)
        
        assert provider.validate_config() is False
    
    def test_gemini_provider_validate_config_invalid_top_k(self):
        """Test Gemini provider configuration validation with invalid top_k."""
        config = {'api_key': 'test_key', 'top_k': -1}
        provider = GeminiProvider(config)
        
        assert provider.validate_config() is False
    
    def test_gemini_provider_validate_config_invalid_max_tokens(self):
        """Test Gemini provider configuration validation with invalid max_output_tokens."""
        config = {'api_key': 'test_key', 'max_output_tokens': 0}
        provider = GeminiProvider(config)
        
        assert provider.validate_config() is False
    
    def test_gemini_provider_is_available(self):
        """Test Gemini provider availability check."""
        provider = GeminiProvider({'api_key': 'test_key'})
        
        # Should not be available without initialization
        assert provider.is_available() is False
        
        # Mock initialization
        provider.is_initialized = True
        provider.client = Mock()
        
        assert provider.is_available() is True
    
    def test_gemini_provider_get_provider_info(self):
        """Test getting Gemini provider information."""
        config = {
            'api_key': 'test_key',
            'model': 'gemini-2.0-flash',
            'max_output_tokens': 1024,
            'temperature': 0.7
        }
        provider = GeminiProvider(config)
        
        info = provider.get_provider_info()
        
        assert info['name'] == 'GeminiProvider'
        assert info['model_name'] == 'gemini-2.0-flash'
        assert info['max_output_tokens'] == 1024
        assert info['temperature'] == 0.7
        assert info['top_p'] == 0.95
        assert info['top_k'] == 40
        assert info['has_api_key'] is True
    
    def test_gemini_provider_cleanup(self):
        """Test Gemini provider cleanup."""
        provider = GeminiProvider({'api_key': 'test_key'})
        provider.client = Mock()
        provider.is_initialized = True
        
        provider.cleanup()
        
        assert provider.client is None
        assert provider.is_initialized is False
    
    def test_gemini_provider_sdk_version(self):
        """Test getting SDK version."""
        provider = GeminiProvider()
        
        version = provider._get_sdk_version()
        
        # Should return either a version string or 'not installed'
        assert isinstance(version, str)


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