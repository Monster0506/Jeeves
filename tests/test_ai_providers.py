"""
Unit tests for AI providers.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from core.ai_providers import GeminiProvider, PlaceholderProvider, BaseAIProvider
from typing import List, Dict


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