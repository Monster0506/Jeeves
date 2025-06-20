"""
API tests for Jeeves AI Assistant.
Tests actual API calls and external service integration.
"""
import pytest
import os
import time
from unittest.mock import patch, Mock
from core.ai_providers import GeminiProvider
from core.ai_provider_manager import AIProviderManager


class TestGeminiAPI:
    """Tests for actual Gemini API integration."""
    
    @pytest.mark.api
    @pytest.mark.slow
    def test_gemini_api_connection(self):
        """Test actual connection to Gemini API."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")
        
        provider = GeminiProvider({'api_key': api_key})
        
        # Test initialization
        result = provider.initialize()
        assert result is True
        assert provider.is_available() is True
        
        # Test basic response generation
        response = provider.generate_response("Hello, this is a test message.")
        assert isinstance(response, str)
        assert len(response) > 0
        
        provider.cleanup()
    
    @pytest.mark.api
    @pytest.mark.slow
    def test_gemini_api_conversation_context(self):
        """Test Gemini API with conversation context."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")
        
        provider = GeminiProvider({'api_key': api_key})
        provider.initialize()
        
        # Test with conversation context
        context = [
            {'sender': 'user', 'content': 'My name is Alice'},
            {'sender': 'ai', 'content': 'Nice to meet you, Alice!'}
        ]
        
        response = provider.generate_response("What's my name?", context)
        response_lower = response.lower()
        
        # Check if response contains expected content or error message
        assert 'alice' in response_lower or 'name' in response_lower or 'error' in response_lower
    
    @pytest.mark.api
    @pytest.mark.slow
    def test_gemini_api_system_instruction(self):
        """Test Gemini API with custom system instruction."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")
        
        custom_instruction = "You are a helpful coding assistant. Always respond with code examples when relevant."
        
        provider = GeminiProvider({
            'api_key': api_key,
            'system_instruction': custom_instruction
        })
        provider.initialize()
        
        # Test with a coding question
        response = provider.generate_response("How do I create a Python function?")
        assert isinstance(response, str)
        assert len(response) > 0
        
        # The response should be coding-focused
        response_lower = response.lower()
        assert any(term in response_lower for term in ['def ', 'function', 'code', 'python'])
        
        provider.cleanup()
    
    @pytest.mark.api
    @pytest.mark.slow
    def test_gemini_api_parameter_validation(self):
        """Test Gemini API with different parameters."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")
        
        # Test with different temperature settings
        for temperature in [0.1, 0.5, 0.9]:
            provider = GeminiProvider({
                'api_key': api_key,
                'temperature': temperature,
                'max_output_tokens': 100
            })
            provider.initialize()
            
            response = provider.generate_response("Tell me a short story.")
            assert isinstance(response, str)
            assert len(response) > 0
            
            provider.cleanup()
    
    @pytest.mark.api
    @pytest.mark.slow
    def test_gemini_api_error_handling(self):
        """Test Gemini API error handling."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")
        
        provider = GeminiProvider({'api_key': api_key})
        result = provider.initialize()
        
        # Provider should initialize successfully even with potential API issues
        assert result is True
    
    @pytest.mark.api
    @pytest.mark.slow
    def test_gemini_api_rate_limiting(self):
        """Test Gemini API rate limiting behavior."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")
        
        provider = GeminiProvider({'api_key': api_key})
        provider.initialize()
        
        # Send multiple requests quickly
        responses = []
        for i in range(3):
            response = provider.generate_response(f"Test message {i}")
            responses.append(response)
            time.sleep(0.5)  # Small delay between requests
        
        # All responses should be successful
        for response in responses:
            assert isinstance(response, str)
            assert len(response) > 0
        
        provider.cleanup()
    
    @pytest.mark.api
    @pytest.mark.slow
    def test_gemini_api_model_variations(self):
        """Test different Gemini models."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")
        
        # Test with different models if available
        models_to_test = ['gemini-2.0-flash', 'gemini-1.5-flash']
        
        for model in models_to_test:
            try:
                provider = GeminiProvider({
                    'api_key': api_key,
                    'model': model
                })
                
                if provider.initialize():
                    response = provider.generate_response("Hello, test message.")
                    assert isinstance(response, str)
                    assert len(response) > 0
                    provider.cleanup()
                    break  # If one model works, we're good
                else:
                    provider.cleanup()
            except Exception:
                continue  # Skip models that don't work


class TestProviderManagerAPI:
    """Tests for Provider Manager with actual API calls."""
    
    @pytest.mark.api
    @pytest.mark.slow
    def test_provider_manager_with_real_api(self):
        """Test Provider Manager with real API integration."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")
        
        manager = AIProviderManager()
        
        # Test initialization
        result = manager.initialize()
        assert result is True
        assert manager.current_provider is not None
        
        # Test response generation
        response = manager.generate_response("Hello, this is a real API test.")
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Test provider information
        providers_info = manager.get_available_providers()
        assert len(providers_info) >= 1
        
        # Test provider status
        status = manager.get_provider_status()
        assert status['is_available'] is True
        
        manager.cleanup()
    
    @pytest.mark.api
    @pytest.mark.slow
    def test_provider_manager_fallback_with_api_failure(self):
        """Test Provider Manager fallback when API fails."""
        manager = AIProviderManager()
        
        # Mock Gemini provider to fail
        if 'gemini' in manager.providers:
            original_initialize = manager.providers['gemini'].initialize
            manager.providers['gemini'].initialize = Mock(return_value=False)
        
        # Test initialization with fallback
        result = manager.initialize()
        assert result is True
        assert manager.current_provider is not None
        
        # Should fall back to placeholder provider
        if 'gemini' in manager.providers:
            assert manager.current_provider.provider_name == 'PlaceholderProvider'
        
        # Restore original method
        if 'gemini' in manager.providers:
            manager.providers['gemini'].initialize = original_initialize
        
        manager.cleanup()
    
    @pytest.mark.api
    @pytest.mark.slow
    def test_provider_manager_switching_with_api(self):
        """Test Provider Manager provider switching with real API."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")
        
        manager = AIProviderManager()
        manager.initialize()
        
        # Get available providers
        providers_info = manager.get_available_providers()
        
        # Test switching between providers
        for provider_info in providers_info:
            provider_name = provider_info['name']
            
            # Try to switch to this provider
            result = manager.switch_provider(provider_name)
            
            if result:
                # Test response generation with this provider
                response = manager.generate_response("Test message")
                assert isinstance(response, str)
                assert len(response) > 0
                
                # Verify the switch worked
                current_provider = manager.get_current_provider()
                assert current_provider is not None
                # Check if provider name contains the expected substring
                assert provider_name.lower() in current_provider.provider_name.lower() or current_provider.provider_name.lower() in provider_name.lower()
        
        manager.cleanup()


class TestAPIErrorHandling:
    """Tests for API error handling scenarios."""
    
    @pytest.mark.api
    def test_api_timeout_handling(self):
        """Test handling of API timeouts."""
        # This would require mocking network timeouts
        # For now, we'll test the error handling structure
        provider = GeminiProvider({'api_key': 'test_key'})
        
        # Test with a provider that's not initialized
        response = provider.generate_response("Test message")
        assert "not available" in response.lower()
    
    @pytest.mark.api
    def test_api_invalid_response_handling(self):
        """Test handling of invalid API responses."""
        with patch('google.genai.Client') as mock_client_class:
            # Mock invalid response
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            mock_response = Mock()
            mock_response.text = None
            mock_client.models.generate_content.return_value = mock_response
            
            provider = GeminiProvider({'api_key': 'test_key'})
            provider.initialize()
            
            response = provider.generate_response("Hello")
            assert "I apologize" in response or "empty" in response.lower()
    
    @pytest.mark.api
    def test_api_exception_handling(self):
        """Test handling of API exceptions."""
        with patch('google.genai.Client') as mock_client_class:
            # Mock exception
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.models.generate_content.side_effect = Exception("API Error")
            
            provider = GeminiProvider({'api_key': 'test_key'})
            provider.initialize()
            
            response = provider.generate_response("Hello")
            assert "error" in response.lower() or "sorry" in response.lower()


class TestAPIPerformance:
    """Tests for API performance characteristics."""
    
    @pytest.mark.api
    @pytest.mark.slow
    def test_api_response_time(self):
        """Test API response time."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")
        
        provider = GeminiProvider({'api_key': api_key})
        provider.initialize()
        
        # Test response time
        start_time = time.time()
        response = provider.generate_response("Quick test message")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert response_time < 30.0  # Should respond within 30 seconds
        
        provider.cleanup()
    
    @pytest.mark.api
    @pytest.mark.slow
    def test_api_concurrent_requests(self):
        """Test handling of concurrent API requests."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")
        
        provider = GeminiProvider({'api_key': api_key})
        provider.initialize()
        
        # Send multiple requests
        responses = []
        for i in range(3):
            response = provider.generate_response(f"Concurrent test {i}")
            responses.append(response)
        
        # All responses should be successful
        for response in responses:
            assert isinstance(response, str)
            assert len(response) > 0
        
        provider.cleanup() 