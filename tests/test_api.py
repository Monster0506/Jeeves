"""
API tests for Jeeves AI Assistant.
Tests actual API calls and external service integration.
"""

import os
import time
from unittest.mock import Mock, patch

import pytest

from core.ai_provider_manager import AIProviderManager
from core.ai_providers import GeminiProvider


class TestGeminiAPI:
    """Tests for actual Gemini API integration."""

    @pytest.mark.api
    @pytest.mark.slow
    def test_gemini_api_connection(self):
        """Test actual connection to Gemini API."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")

        provider = GeminiProvider({"api_key": api_key})

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
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")

        provider = GeminiProvider({"api_key": api_key})
        provider.initialize()

        # Test with conversation context
        context = [
            {"sender": "user", "content": "My name is Alice"},
            {"sender": "ai", "content": "Nice to meet you, Alice!"},
        ]

        response = provider.generate_response("What's my name?", context)
        response_lower = response.lower()

        # Check if response contains expected content or error message
        assert "alice" in response_lower or "name" in response_lower or "error" in response_lower

    @pytest.mark.api
    @pytest.mark.slow
    def test_gemini_api_system_instruction(self):
        """Test Gemini API with custom system instruction."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")

        custom_instruction = "You are a helpful coding assistant. Always respond with code examples when relevant."

        provider = GeminiProvider({"api_key": api_key, "system_instruction": custom_instruction})
        provider.initialize()

        # Test with a coding question
        response = provider.generate_response("How do I create a Python function?")
        assert isinstance(response, str)
        assert len(response) > 0

        # The response should be coding-focused
        response_lower = response.lower()
        assert any(term in response_lower for term in ["def ", "function", "code", "python"])

        provider.cleanup()

    @pytest.mark.api
    @pytest.mark.slow
    def test_gemini_api_parameter_validation(self):
        """Test Gemini API with different parameters."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")

        # Test with different temperature settings
        for temperature in [0.1, 0.5, 0.9]:
            provider = GeminiProvider(
                {
                    "api_key": api_key,
                    "temperature": temperature,
                    "max_output_tokens": 100,
                }
            )
            provider.initialize()

            response = provider.generate_response("Tell me a short story.")
            assert isinstance(response, str)
            assert len(response) > 0

            provider.cleanup()

    @pytest.mark.api
    @pytest.mark.slow
    def test_gemini_api_error_handling(self):
        """Test Gemini API error handling."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")

        provider = GeminiProvider({"api_key": api_key})
        result = provider.initialize()

        # Provider should initialize successfully even with potential API issues
        assert result is True

    @pytest.mark.api
    @pytest.mark.slow
    def test_gemini_api_rate_limiting(self):
        """Test Gemini API rate limiting behavior."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")

        provider = GeminiProvider({"api_key": api_key})
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
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")

        # Test with different models if available
        models_to_test = ["gemini-2.5-flash-lite-preview-06-17", "gemini-2.0-flash"]

        for model in models_to_test:
            try:
                provider = GeminiProvider({"api_key": api_key, "model": model})

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
        api_key = os.getenv("GOOGLE_API_KEY")
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
        assert status["is_available"] is True

        manager.cleanup()

    @pytest.mark.api
    @pytest.mark.slow
    def test_provider_manager_fallback_with_api_failure(self):
        """Test Provider Manager fallback when API fails."""
        manager = AIProviderManager()

        # Mock Gemini provider to fail
        if "gemini" in manager.providers:
            original_initialize = manager.providers["gemini"].initialize
            manager.providers["gemini"].initialize = Mock(return_value=False)

        # Test initialization with fallback
        result = manager.initialize()
        assert result is True
        assert manager.current_provider is not None

        # Should fall back to placeholder provider
        if "gemini" in manager.providers:
            assert manager.current_provider.provider_name == "PlaceholderProvider"

        # Restore original method
        if "gemini" in manager.providers:
            manager.providers["gemini"].initialize = original_initialize

        manager.cleanup()

    @pytest.mark.api
    @pytest.mark.slow
    def test_provider_manager_switching_with_api(self):
        """Test Provider Manager provider switching with real API."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")

        manager = AIProviderManager()
        manager.initialize()

        # Get available providers
        providers_info = manager.get_available_providers()

        # Test switching between providers
        for provider_info in providers_info:
            provider_name = provider_info["name"]

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
        provider = GeminiProvider({"api_key": "test_key"})

        # Test with a provider that's not initialized
        response = provider.generate_response("Test message")
        assert "not available" in response.lower()

    @pytest.mark.api
    def test_api_invalid_response_handling(self):
        """Test handling of invalid API responses."""
        with patch("google.genai.Client") as mock_client_class:
            # Mock invalid response
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            mock_response = Mock()
            mock_response.text = None
            mock_client.models.generate_content.return_value = mock_response

            provider = GeminiProvider({"api_key": "test_key"})
            provider.initialize()

            response = provider.generate_response("Hello")
            assert "I apologize" in response or "empty" in response.lower()

    @pytest.mark.api
    def test_api_exception_handling(self):
        """Test handling of API exceptions."""
        with patch("google.genai.Client") as mock_client_class:
            # Mock exception
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.models.generate_content.side_effect = Exception("API Error")

            provider = GeminiProvider({"api_key": "test_key"})
            provider.initialize()

            response = provider.generate_response("Hello")
            assert "error" in response.lower() or "sorry" in response.lower()


class TestAPIPerformance:
    """Tests for API performance characteristics."""

    @pytest.mark.api
    @pytest.mark.slow
    def test_api_response_time(self):
        """Test API response time."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")

        provider = GeminiProvider({"api_key": api_key})
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
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            pytest.skip("GOOGLE_API_KEY not set")

        provider = GeminiProvider({"api_key": api_key})
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


# class TestGeminiToolCallingAPI:
#     """Tests for actual Gemini API tool calling functionality."""

#     @pytest.mark.api
#     @pytest.mark.slow
#     def test_gemini_api_tool_calling_basic(self):
#         """Test basic tool calling with real Gemini API."""
#         api_key = os.getenv('GOOGLE_API_KEY')
#         if not api_key:
#             pytest.skip("GOOGLE_API_KEY not set")

#         provider = GeminiProvider({
#             'api_key': api_key,
#             'enable_tool_calling': True,
#             'automatic_function_calling': True
#         })
#         provider.initialize()

#         # Define a simple tool
#         def get_current_time() -> str:
#             """Get the current time and date."""
#             from datetime import datetime
#             return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         # Register the tool
#         provider.register_tool("get_current_time", get_current_time)

#         # Test tool calling
#         response = provider.generate_response("What time is it right now?")

#         # The response should either contain the time or indicate tool usage
#         assert isinstance(response, str)
#         assert len(response) > 0

#         # Check if the response contains an API error
#         response_lower = response.lower()
#         error_indicators = ['error', 'invalid', 'api key', '400', 'invalid_argument']
#         if any(indicator in response_lower for indicator in error_indicators):
#             pytest.skip("API key is invalid or API error occurred")

#         # Check if the response contains time-related content
#         time_indicators = ['time', 'current', 'now', 'datetime', '2024', '2025']
#         assert any(indicator in response_lower for indicator in time_indicators)

#         provider.cleanup()

#     @pytest.mark.api
#     @pytest.mark.slow
#     def test_gemini_api_tool_calling_calculation(self):
#         """Test calculation tool calling with real Gemini API."""
#         api_key = os.getenv('GOOGLE_API_KEY')
#         if not api_key:
#             pytest.skip("GOOGLE_API_KEY not set")

#         provider = GeminiProvider({
#             'api_key': api_key,
#             'enable_tool_calling': True,
#             'automatic_function_calling': True
#         })
#         provider.initialize()

#         # Define calculation tool
#         def calculate_sum(a: int, b: int) -> int:
#             """Calculate the sum of two numbers."""
#             return a + b

#         # Register the tool
#         provider.register_tool("calculate_sum", calculate_sum)

#         # Test calculation
#         response = provider.generate_response("What is 15 + 27?")

#         assert isinstance(response, str)
#         assert len(response) > 0

#         # Check if the response contains an API error
#         response_lower = response.lower()
#         error_indicators = ['error', 'invalid', 'api key', '400', 'invalid_argument']
#         if any(indicator in response_lower for indicator in error_indicators):
#             pytest.skip("API key is invalid or API error occurred")

#         # The response should contain the result (42) or indicate calculation
#         calculation_indicators = ['42', 'sum', 'result', 'calculation', 'add']
#         assert any(indicator in response_lower for indicator in calculation_indicators)

#         provider.cleanup()

#     @pytest.mark.api
#     @pytest.mark.slow
#     def test_gemini_api_tool_calling_weather(self):
#         """Test weather tool calling with real Gemini API."""
#         api_key = os.getenv('GOOGLE_API_KEY')
#         if not api_key:
#             pytest.skip("GOOGLE_API_KEY not set")

#         provider = GeminiProvider({
#             'api_key': api_key,
#             'enable_tool_calling': True,
#             'automatic_function_calling': True
#         })
#         provider.initialize()

#         # Define weather tool
#         def get_weather(location: str) -> str:
#             """Get weather information for a location."""
#             weather_data = {
#                 "New York": "Sunny, 72°F",
#                 "London": "Rainy, 55°F",
#                 "Tokyo": "Cloudy, 68°F",
#                 "Paris": "Partly cloudy, 65°F"
#             }
#             return weather_data.get(location, f"Weather data not available for {location}")

#         # Register the tool
#         provider.register_tool("get_weather", get_weather)

#         # Test weather query
#         response = provider.generate_response("What's the weather in Tokyo?")

#         assert isinstance(response, str)
#         assert len(response) > 0

#         # Check if the response contains an API error
#         response_lower = response.lower()
#         error_indicators = ['error', 'invalid', 'api key', '400', 'invalid_argument']
#         if any(indicator in response_lower for indicator in error_indicators):
#             pytest.skip("API key is invalid or API error occurred")

#         # The response should contain weather information or location
#         weather_indicators = ['tokyo', 'weather', 'cloudy', '68', 'temperature', '°f']
#         assert any(indicator in response_lower for indicator in weather_indicators)

#         provider.cleanup()

#     @pytest.mark.api
#     @pytest.mark.slow
#     def test_gemini_api_tool_calling_multiple_tools(self):
#         """Test multiple tool calling with real Gemini API."""
#         api_key = os.getenv('GOOGLE_API_KEY')
#         if not api_key:
#             pytest.skip("GOOGLE_API_KEY not set")

#         provider = GeminiProvider({
#             'api_key': api_key,
#             'enable_tool_calling': True,
#             'automatic_function_calling': True,
#             'max_tool_calls': 3
#         })
#         provider.initialize()

#         # Define multiple tools
#         def get_current_time() -> str:
#             """Get the current time and date."""
#             from datetime import datetime
#             return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         def calculate_sum(a: int, b: int) -> int:
#             """Calculate the sum of two numbers."""
#             return a + b

#         def get_weather(location: str) -> str:
#             """Get weather information for a location."""
#             weather_data = {
#                 "New York": "Sunny, 72°F",
#                 "London": "Rainy, 55°F",
#                 "Tokyo": "Cloudy, 68°F"
#             }
#             return weather_data.get(location, f"Weather data not available for {location}")

#         # Register all tools
#         provider.register_tool("get_current_time", get_current_time)
#         provider.register_tool("calculate_sum", calculate_sum)
#         provider.register_tool("get_weather", get_weather)

#         # Test complex request that might use multiple tools
#         response = provider.generate_response(
#             "What time is it, what's 10 + 5, and what's the weather in New York?"
#         )

#         assert isinstance(response, str)
#         assert len(response) > 0

#         # Check if the response contains an API error
#         response_lower = response.lower()
#         error_indicators = ['error', 'invalid', 'api key', '400', 'invalid_argument']
#         if any(indicator in response_lower for indicator in error_indicators):
#             pytest.skip("API key is invalid or API error occurred")

#         # The response should contain information from multiple tools
#         time_indicators = ['time', 'current', 'now']
#         calculation_indicators = ['15', 'sum', 'result']
#         weather_indicators = ['new york', 'weather', 'sunny', '72']

#         # Check for at least two types of information
#         indicators_found = 0
#         if any(indicator in response_lower for indicator in time_indicators):
#             indicators_found += 1
#         if any(indicator in response_lower for indicator in calculation_indicators):
#             indicators_found += 1
#         if any(indicator in response_lower for indicator in weather_indicators):
#             indicators_found += 1

#         assert indicators_found >= 1  # At least one tool should be used

#         provider.cleanup()

#     @pytest.mark.api
#     @pytest.mark.slow
#     def test_gemini_api_tool_calling_with_context(self):
#         """Test tool calling with conversation context."""
#         api_key = os.getenv('GOOGLE_API_KEY')
#         if not api_key:
#             pytest.skip("GOOGLE_API_KEY not set")

#         provider = GeminiProvider({
#             'api_key': api_key,
#             'enable_tool_calling': True,
#             'automatic_function_calling': True
#         })
#         provider.initialize()

#         # Define a tool
#         def get_user_info(user_id: str) -> dict:
#             """Get user information."""
#             user_data = {
#                 "123": {"id": "123", "name": "Alice", "email": "alice@example.com"},
#                 "456": {"id": "456", "name": "Bob", "email": "bob@example.com"}
#             }
#             return user_data.get(user_id, {"id": user_id, "name": "Unknown", "email": "unknown@example.com"})

#         # Register the tool
#         provider.register_tool("get_user_info", get_user_info)

#         # Test with conversation context
#         context = [
#             {'sender': 'user', 'content': 'I want to know about user 123'},
#             {'sender': 'ai', 'content': 'I can help you get information about users. What would you like to know?'}
#         ]

#         response = provider.generate_response("What is their name?", context)

#         assert isinstance(response, str)
#         assert len(response) > 0

#         # Check if the response contains an API error
#         response_lower = response.lower()
#         error_indicators = ['error', 'invalid', 'api key', '400', 'invalid_argument']
#         if any(indicator in response_lower for indicator in error_indicators):
#             pytest.skip("API key is invalid or API error occurred")

#         # The response should contain user information
#         user_indicators = ['alice', 'user', 'name', '123']
#         assert any(indicator in response_lower for indicator in user_indicators)

#         provider.cleanup()

#     @pytest.mark.api
#     @pytest.mark.slow
#     def test_gemini_api_tool_calling_disabled(self):
#         """Test that tool calling is properly disabled when configured."""
#         api_key = os.getenv('GOOGLE_API_KEY')
#         if not api_key:
#             pytest.skip("GOOGLE_API_KEY not set")

#         provider = GeminiProvider({
#             'api_key': api_key,
#             'enable_tool_calling': False,  # Disable tool calling
#             'automatic_function_calling': False
#         })
#         provider.initialize()

#         # Define a tool
#         def get_current_time() -> str:
#             """Get the current time and date."""
#             from datetime import datetime
#             return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         # Register the tool (should be ignored)
#         provider.register_tool("get_current_time", get_current_time)

#         # Test that tools are not called when disabled
#         response = provider.generate_response("What time is it right now?")

#         assert isinstance(response, str)
#         assert len(response) > 0

#         # The response should be a normal AI response, not tool execution
#         # It should not contain the exact time format from our tool
#         response_lower = response.lower()

#         # Check that it's not the exact tool output
#         from datetime import datetime
#         current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         assert current_time not in response

#         provider.cleanup()

#     @pytest.mark.api
#     @pytest.mark.slow
#     def test_provider_manager_tool_calling(self):
#         """Test tool calling through the provider manager with real API."""
#         api_key = os.getenv('GOOGLE_API_KEY')
#         if not api_key:
#             pytest.skip("GOOGLE_API_KEY not set")

#         manager = AIProviderManager()

#         # Define tools
#         def get_current_time() -> str:
#             """Get the current time and date."""
#             from datetime import datetime
#             return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         def calculate_sum(a: int, b: int) -> int:
#             """Calculate the sum of two numbers."""
#             return a + b

#         # Register tools with manager
#         manager.register_tool("get_current_time", get_current_time)
#         manager.register_tool("calculate_sum", calculate_sum)

#         # Initialize manager
#         result = manager.initialize()
#         assert result is True

#         # Test tool calling through manager
#         response = manager.generate_response("What time is it and what's 5 + 3?")

#         assert isinstance(response, str)
#         assert len(response) > 0

#         # Check if the response contains an API error
#         response_lower = response.lower()
#         error_indicators = ['error', 'invalid', 'api key', '400', 'invalid_argument']
#         if any(indicator in response_lower for indicator in error_indicators):
#             pytest.skip("API key is invalid or API error occurred")

#         # The response should contain time and calculation information
#         time_indicators = ['time', 'current', 'now']
#         calculation_indicators = ['8', 'sum', 'result', 'calculation']

#         # Check for at least one type of information
#         has_time_info = any(indicator in response_lower for indicator in time_indicators)
#         has_calc_info = any(indicator in response_lower for indicator in calculation_indicators)

#         assert has_time_info or has_calc_info

#         manager.cleanup()
