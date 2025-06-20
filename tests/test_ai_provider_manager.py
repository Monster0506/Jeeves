"""
Unit tests for AI Provider Manager.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from core.ai_provider_manager import AIProviderManager
from core.ai_providers import GeminiProvider, PlaceholderProvider


class TestAIProviderManager:
    """Test the AI Provider Manager."""
    
    def test_provider_manager_initialization(self):
        """Test provider manager initialization."""
        manager = AIProviderManager()
        
        assert manager.providers is not None
        assert isinstance(manager.providers, dict)
        assert manager.current_provider is None
        assert manager.provider_order == ['gemini', 'placeholder']
    
    def test_provider_manager_register_providers(self):
        """Test provider registration."""
        manager = AIProviderManager()
        
        # Should have registered providers
        assert 'placeholder' in manager.providers
        assert isinstance(manager.providers['placeholder'], PlaceholderProvider)
        
        # Gemini provider might not be registered if there's an error
        # but placeholder should always be available
        assert len(manager.providers) >= 1
    
    @patch('google.genai.Client')
    def test_provider_manager_initialize_success(self, mock_client_class):
        """Test provider manager initialization with successful provider."""
        # Mock Gemini client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_models = [Mock(), Mock()]
        mock_client.models.list.return_value = mock_models
        
        manager = AIProviderManager()
        
        result = manager.initialize()
        
        assert result is True
        assert manager.current_provider is not None
        assert manager.current_provider.provider_name == 'GeminiProvider'
    
    def test_provider_manager_initialize_fallback(self):
        """Test provider manager initialization with fallback to placeholder."""
        manager = AIProviderManager()
        
        # Mock all providers to fail except placeholder
        for name, provider in manager.providers.items():
            if name != 'placeholder':
                provider.initialize = Mock(return_value=False)
        
        result = manager.initialize()
        
        assert result is True
        assert manager.current_provider is not None
        assert manager.current_provider.provider_name == 'PlaceholderProvider'
    
    def test_provider_manager_initialize_all_fail(self):
        """Test provider manager initialization when all providers fail."""
        manager = AIProviderManager()
        
        # Mock all providers to fail
        for provider in manager.providers.values():
            provider.initialize = Mock(return_value=False)
        
        result = manager.initialize()
        
        # Should still succeed because placeholder is always available
        assert result is True
    
    def test_provider_manager_get_current_provider(self):
        """Test getting current provider."""
        manager = AIProviderManager()
        
        # Initially no current provider
        assert manager.get_current_provider() is None
        
        # Set a current provider
        test_provider = PlaceholderProvider()
        manager.current_provider = test_provider
        
        assert manager.get_current_provider() == test_provider
    
    def test_provider_manager_switch_provider_success(self):
        """Test successful provider switching."""
        manager = AIProviderManager()
        
        # Setup providers
        provider1 = PlaceholderProvider()
        provider2 = PlaceholderProvider()
        provider1.initialize = Mock(return_value=True)
        provider2.initialize = Mock(return_value=True)
        
        manager.providers['test1'] = provider1
        manager.providers['test2'] = provider2
        manager.current_provider = provider1
        
        result = manager.switch_provider('test2')
        
        assert result is True
        assert manager.current_provider == provider2
    
    def test_provider_manager_switch_provider_not_found(self):
        """Test provider switching with non-existent provider."""
        manager = AIProviderManager()
        
        result = manager.switch_provider('non_existent')
        
        assert result is False
        assert manager.current_provider is None
    
    def test_provider_manager_switch_provider_initialization_fails(self):
        """Test provider switching when initialization fails."""
        manager = AIProviderManager()
        
        # Create a provider that fails to initialize
        failing_provider = PlaceholderProvider()
        failing_provider.initialize = Mock(return_value=False)
        
        manager.providers['failing'] = failing_provider
        
        result = manager.switch_provider('failing')
        
        assert result is False
    
    def test_provider_manager_generate_response_success(self):
        """Test successful response generation."""
        manager = AIProviderManager()
        
        # Setup a mock provider
        mock_provider = Mock()
        mock_provider.generate_response.return_value = "Test response"
        manager.current_provider = mock_provider
        
        response = manager.generate_response("Hello")
        
        assert response == "Test response"
        mock_provider.generate_response.assert_called_once_with("Hello", None)
    
    def test_provider_manager_generate_response_with_context(self):
        """Test response generation with context."""
        manager = AIProviderManager()
        
        # Setup a mock provider
        mock_provider = Mock()
        mock_provider.generate_response.return_value = "Context response"
        manager.current_provider = mock_provider
        
        context = [{'sender': 'user', 'content': 'Previous message'}]
        response = manager.generate_response("Hello", context)
        
        assert response == "Context response"
        mock_provider.generate_response.assert_called_once_with("Hello", context)
    
    def test_provider_manager_generate_response_no_provider(self):
        """Test response generation when no provider is available."""
        manager = AIProviderManager()
        
        response = manager.generate_response("Hello")
        
        assert "sorry, no ai provider" in response.lower()
    
    def test_provider_manager_generate_response_exception(self):
        """Test response generation when provider raises an exception."""
        manager = AIProviderManager()
        
        # Setup a mock provider that raises an exception
        mock_provider = Mock()
        mock_provider.generate_response.side_effect = Exception("Test error")
        manager.current_provider = mock_provider
        
        response = manager.generate_response("Hello")
        
        assert "encountered an error" in response.lower()
        assert "Test error" in response
    
    def test_provider_manager_get_available_providers(self):
        """Test getting available providers information."""
        manager = AIProviderManager()
        
        # Setup some providers
        provider1 = PlaceholderProvider()
        provider2 = PlaceholderProvider()
        manager.providers['test1'] = provider1
        manager.providers['test2'] = provider2
        manager.current_provider = provider1
        
        providers_info = manager.get_available_providers()
        
        assert len(providers_info) >= 2
        
        # Check that each provider info has required fields
        for info in providers_info:
            assert 'name' in info
            assert 'is_current' in info
            assert isinstance(info['name'], str)
            assert isinstance(info['is_current'], bool)
    
    def test_provider_manager_get_provider_status_no_provider(self):
        """Test getting provider status when no provider is available."""
        manager = AIProviderManager()
        
        status = manager.get_provider_status()
        
        assert status['provider'] is None
        assert status['status'] == 'no_provider'
        assert status['available'] is False
    
    def test_provider_manager_get_provider_status_with_provider(self):
        """Test getting provider status when a provider is available."""
        manager = AIProviderManager()
        
        # Setup a provider
        provider = PlaceholderProvider()
        provider.initialize()
        manager.current_provider = provider
        
        status = manager.get_provider_status()
        
        assert status['name'] == 'PlaceholderProvider'
        assert status['is_initialized'] is True
        assert status['is_available'] is True
    
    def test_provider_manager_add_provider(self):
        """Test adding a custom provider."""
        manager = AIProviderManager()
        
        # Create a custom provider
        custom_provider = PlaceholderProvider()
        
        result = manager.add_provider('custom', custom_provider)
        
        assert result is True
        assert 'custom' in manager.providers
        assert manager.providers['custom'] == custom_provider
    
    def test_provider_manager_add_provider_overwrite(self):
        """Test adding a provider that already exists."""
        manager = AIProviderManager()
        
        # Add a provider
        provider1 = PlaceholderProvider()
        manager.add_provider('test', provider1)
        
        # Add another provider with the same name
        provider2 = PlaceholderProvider()
        result = manager.add_provider('test', provider2)
        
        assert result is True
        assert manager.providers['test'] == provider2
    
    def test_provider_manager_remove_provider_success(self):
        """Test successful provider removal."""
        manager = AIProviderManager()
        
        # Add a provider
        provider = PlaceholderProvider()
        manager.add_provider('test', provider)
        
        result = manager.remove_provider('test')
        
        assert result is True
        assert 'test' not in manager.providers
    
    def test_provider_manager_remove_provider_not_found(self):
        """Test removing a non-existent provider."""
        manager = AIProviderManager()
        
        result = manager.remove_provider('non_existent')
        
        assert result is False
    
    def test_provider_manager_remove_current_provider(self):
        """Test removing the current provider."""
        manager = AIProviderManager()
        
        # Add and set as current provider
        provider = PlaceholderProvider()
        manager.add_provider('test', provider)
        manager.current_provider = provider
        
        result = manager.remove_provider('test')
        
        # Should not allow removing current provider
        assert result is False
    
    def test_provider_manager_cleanup(self):
        """Test provider manager cleanup."""
        manager = AIProviderManager()
        
        # Setup some providers
        provider1 = Mock()
        provider2 = Mock()
        manager.providers['test1'] = provider1
        manager.providers['test2'] = provider2
        manager.current_provider = provider1
        
        manager.cleanup()
        
        # Verify cleanup was called on all providers
        provider1.cleanup.assert_called_once()
        provider2.cleanup.assert_called_once()
    
    def test_provider_manager_str_representation(self):
        """Test string representation of provider manager."""
        manager = AIProviderManager()
        
        str_repr = str(manager)
        
        assert isinstance(str_repr, str)
        assert "AIProviderManager" in str_repr
    
    def test_provider_manager_repr_representation(self):
        """Test repr representation of provider manager."""
        manager = AIProviderManager()
        
        repr_str = repr(manager)
        
        assert isinstance(repr_str, str)
        assert "AIProviderManager" in repr_str
    
    @patch('google.genai.Client')
    def test_provider_manager_integration_test(self, mock_client_class):
        """Test provider manager integration with real providers."""
        # Mock Gemini client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_models = [Mock(), Mock()]
        mock_client.models.list.return_value = mock_models
        
        # Mock the response generation
        mock_response = Mock()
        mock_response.text = "This is a test response from Gemini."
        mock_client.models.generate_content.return_value = mock_response
        
        manager = AIProviderManager()
        
        # Test initialization
        result = manager.initialize()
        assert result is True
        assert manager.current_provider is not None
        
        # Test response generation
        response = manager.generate_response("Hello, this is a test.")
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Test provider switching
        if 'placeholder' in manager.providers:
            result = manager.switch_provider('placeholder')
            assert result is True
            assert manager.current_provider.provider_name == 'PlaceholderProvider'
        
        # Test cleanup
        manager.cleanup()
        assert manager.current_provider is None 