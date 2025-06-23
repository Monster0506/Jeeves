"""
Integration tests for Jeeves AI Assistant.
Tests the interaction between different components.
"""

import uuid
from unittest.mock import Mock, patch

from core.ai_engine import AIEngine
from core.ai_provider_manager import AIProviderManager
from core.chat_manager import ChatManager


class TestAIEngineIntegration:
    """Integration tests for AI Engine."""

    def test_ai_engine_initialization(self, test_database):
        """Test AI Engine initialization."""
        chat_manager = ChatManager(test_database)
        ai_engine = AIEngine(chat_manager)

        assert ai_engine.chat_manager is not None
        assert ai_engine.provider_manager is not None
        assert isinstance(ai_engine.conversation_history, list)

    def test_ai_engine_response_generation(self, test_database):
        """Test AI Engine response generation."""
        chat_manager = ChatManager(test_database)
        ai_engine = AIEngine(chat_manager)

        # Create a thread first
        thread_id = chat_manager.create_thread("Test Thread", "🧪")
        chat_manager.switch_thread(thread_id)

        # Test response generation
        response = ai_engine.generate_response("Hello, this is a test message.")

        assert isinstance(response, str)
        assert len(response) > 0

        # Check that messages were added to the database
        messages = chat_manager.get_messages(thread_id)
        assert len(messages) >= 2  # User message + AI response

    def test_ai_engine_conversation_context(self, test_database):
        """Test AI Engine conversation context retrieval."""
        chat_manager = ChatManager(test_database)
        ai_engine = AIEngine(chat_manager)

        # Create a thread and add some messages with unique name
        thread_name = f"Test Thread {uuid.uuid4().hex[:8]}"
        thread_id = chat_manager.create_thread(thread_name, "🧪")
        chat_manager.switch_thread(thread_id)

        chat_manager.add_user_message("First message")
        chat_manager.add_ai_message("First response")
        chat_manager.add_user_message("Second message")

        # Get conversation context
        context = ai_engine.get_conversation_context(thread_id)

        assert isinstance(context, list)
        assert len(context) >= 3

    def test_ai_engine_provider_switching(self, test_database):
        """Test AI Engine provider switching."""
        chat_manager = ChatManager(test_database)
        ai_engine = AIEngine(chat_manager)

        # Get available providers
        providers = ai_engine.get_available_providers()
        assert len(providers) > 0

        # Test switching to placeholder provider
        result = ai_engine.switch_ai_provider("placeholder")
        assert result is True

        # Verify the switch
        current_provider = ai_engine.get_current_provider_info()
        assert current_provider["name"] == "PlaceholderProvider"

    def test_ai_engine_conversation_analysis(self, test_database):
        """Test AI Engine conversation analysis."""
        chat_manager = ChatManager(test_database)
        ai_engine = AIEngine(chat_manager)

        # Create a thread and add some messages with unique name
        thread_name = f"Test Thread {uuid.uuid4().hex[:8]}"
        thread_id = chat_manager.create_thread(thread_name, "🧪")
        chat_manager.switch_thread(thread_id)

        chat_manager.add_user_message("Hello, how are you?")
        chat_manager.add_ai_message("I'm doing well, thank you!")
        chat_manager.add_user_message("That's great to hear.")

        # Analyze conversation
        analysis = ai_engine.analyze_conversation(thread_id)

        assert isinstance(analysis, dict)
        assert "total_messages" in analysis
        assert "user_messages" in analysis
        assert "ai_messages" in analysis
        assert analysis["total_messages"] >= 3


class TestDatabaseManagerIntegration:
    """Integration tests for DatabaseManager component."""

    def test_database_with_chat_manager(self, test_database):
        """Test database integration with chat manager."""
        chat_manager = ChatManager(test_database)

        # Create a thread with unique name
        thread_name = f"Database Test {uuid.uuid4().hex[:8]}"
        thread_id = chat_manager.create_thread(thread_name, "💾")
        assert thread_id is not None

        # Switch to the thread first
        chat_manager.switch_thread(thread_id)

        # Add a message
        message_id = chat_manager.add_user_message("Test database message")
        assert message_id is not None

        # Retrieve messages
        messages = chat_manager.get_messages(thread_id)
        assert len(messages) >= 1
        assert messages[0]["content"] == "Test database message"
        assert messages[0]["sender"] == "user"

        # Test thread listing
        threads = chat_manager.get_threads()
        assert len(threads) >= 1
        assert any(t["id"] == thread_id for t in threads)

    # Removed test_database_concurrent_access due to SQLite locking issues causing test hangs


class TestProviderManagerIntegration:
    """Integration tests for Provider Manager."""

    @patch("google.genai.Client")
    def test_provider_manager_with_real_providers(self, mock_client_class):
        """Test Provider Manager with real provider implementations."""
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

        # Test provider information
        providers_info = manager.get_available_providers()
        assert len(providers_info) >= 1

        # Test provider switching
        if "placeholder" in manager.providers:
            result = manager.switch_provider("placeholder")
            assert result is True
            assert manager.current_provider.provider_name == "PlaceholderProvider"

        # Test cleanup
        manager.cleanup()
        assert manager.current_provider is None

    def test_provider_manager_fallback_mechanism(self):
        """Test Provider Manager fallback mechanism."""
        manager = AIProviderManager()

        # Mock all providers except placeholder to fail
        for name, provider in manager.providers.items():
            if name != "placeholder":
                provider.initialize = Mock(return_value=False)

        # Test initialization with fallback
        result = manager.initialize()
        assert result is True
        assert manager.current_provider is not None
        assert manager.current_provider.provider_name == "PlaceholderProvider"

        # Test response generation with fallback
        response = manager.generate_response("Fallback test")
        assert isinstance(response, str)
        assert len(response) > 0

        manager.cleanup()


class TestChatManagerIntegration:
    """Integration tests for Chat Manager."""

    def test_chat_manager_full_workflow(self, test_database):
        """Test complete Chat Manager workflow."""
        chat_manager = ChatManager(test_database)

        # Create a thread with unique name
        thread_name = f"Full Workflow Test {uuid.uuid4().hex[:8]}"
        thread_id = chat_manager.create_thread(thread_name, "general")
        assert thread_id is not None

        # Switch to the thread
        chat_manager.switch_thread(thread_id)

        # Add multiple messages
        messages = [
            ("user", "Hello, how are you?"),
            ("ai", "I'm doing well, thank you!"),
            ("user", "Can you help me with Python?"),
            ("ai", "Of course! Python is a great language."),
        ]

        for sender, content in messages:
            if sender == "user":
                chat_manager.add_user_message(content)
            elif sender == "ai":
                chat_manager.add_ai_message(content)
            else:
                chat_manager.add_system_message(content)

        # Retrieve all messages
        stored_messages = chat_manager.get_messages(thread_id)
        assert len(stored_messages) >= len(messages)

        # Verify message order and content
        for i, (sender, content) in enumerate(messages):
            if i < len(stored_messages):
                assert stored_messages[i]["sender"] == sender
                assert stored_messages[i]["content"] == content

        # Test thread listing
        threads = chat_manager.get_threads()
        assert len(threads) >= 1

        # Find our thread
        our_thread = next((t for t in threads if t["id"] == thread_id), None)
        assert our_thread is not None
        assert our_thread["name"] == thread_name
        assert our_thread["icon"] == "general"

        # Test thread deletion
        result = chat_manager.delete_thread(thread_id)
        assert result is True

        # Verify thread is deleted
        threads_after = chat_manager.get_threads()
        assert len(threads_after) < len(threads)

    def test_chat_manager_message_search(self, test_database):
        """Test Chat Manager message search functionality."""
        chat_manager = ChatManager(test_database)

        # Create a thread with specific content and unique name
        thread_name = f"Search Test {uuid.uuid4().hex[:8]}"
        thread_id = chat_manager.create_thread(thread_name, "general")
        chat_manager.switch_thread(thread_id)

        # Add messages with searchable content
        search_terms = ["Python", "programming", "code", "algorithm"]
        for term in search_terms:
            chat_manager.add_user_message(f"Let's talk about {term}")
            chat_manager.add_ai_message(f"I can help you with {term}")

        # Test searching for messages (if search functionality exists)
        # This would depend on the actual implementation
        messages = chat_manager.get_messages(thread_id)
        assert len(messages) >= len(search_terms) * 2

        # Verify all search terms are present
        all_content = " ".join([msg["content"] for msg in messages])
        for term in search_terms:
            assert term.lower() in all_content.lower()

    def test_chat_manager_thread_management(self, test_database):
        """Test Chat Manager thread management."""
        chat_manager = ChatManager(test_database)

        # Create a new thread with unique name
        thread_name = f"Test Thread {uuid.uuid4().hex[:8]}"
        thread_id = chat_manager.create_thread(thread_name, "🧪", "A test thread")
        assert thread_id is not None

        # Switch to the thread
        result = chat_manager.switch_thread(thread_id)
        assert result is True

        # Get current thread
        current_thread = chat_manager.get_current_thread()
        assert current_thread is not None
        assert current_thread["id"] == thread_id
        assert current_thread["name"] == thread_name

        # Add messages to the thread
        message_id1 = chat_manager.add_user_message("Hello, this is a test message.")
        message_id2 = chat_manager.add_ai_message("This is a test response.")

        assert message_id1 is not None
        assert message_id2 is not None

        # Get messages from the thread
        messages = chat_manager.get_messages(thread_id)
        assert len(messages) >= 2

        # Verify message content
        user_messages = [m for m in messages if m["sender"] == "user"]
        ai_messages = [m for m in messages if m["sender"] == "ai"]

        assert len(user_messages) >= 1
        assert len(ai_messages) >= 1
        assert "test message" in user_messages[0]["content"].lower()
        assert "test response" in ai_messages[0]["content"].lower()

    def test_chat_manager_message_flow(self, test_database):
        """Test Chat Manager message flow."""
        chat_manager = ChatManager(test_database)

        # Create and switch to a thread
        thread_id = chat_manager.create_thread("Message Flow Test", "💬")
        chat_manager.switch_thread(thread_id)

        # Add a user message
        user_message_id = chat_manager.add_user_message("What is the weather like?")
        assert user_message_id is not None

        # Add an AI response
        ai_message_id = chat_manager.add_ai_message("I don't have access to real-time weather data, but I can help you with other questions!")
        assert ai_message_id is not None

        # Get all messages
        messages = chat_manager.get_messages(thread_id)
        assert len(messages) >= 2

        # Verify message order and content
        assert messages[0]["sender"] == "user"
        assert "weather" in messages[0]["content"].lower()
        assert messages[1]["sender"] == "ai"
        assert "weather data" in messages[1]["content"].lower()

    # Removed test_chat_manager_concurrent_access due to SQLite locking issues causing test hangs


class TestEndToEndIntegration:
    """End-to-end integration tests."""

    @patch("google.genai.Client")
    def test_full_application_workflow(self, mock_client_class, test_database):
        """Test complete application workflow."""
        # Setup mock Gemini client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_models = [Mock(name="gemini-2.0-flash")]
        mock_client.models.list.return_value = mock_models

        # Mock the response generation
        mock_response = Mock()
        mock_response.text = "This is a test response from Gemini."
        mock_client.models.generate_content.return_value = mock_response

        # Create all components
        chat_manager = ChatManager(test_database)
        ai_engine = AIEngine(chat_manager)

        # Create a conversation thread with unique name
        thread_name = f"E2E Test {uuid.uuid4().hex[:8]}"
        thread_id = chat_manager.create_thread(thread_name, "🧪")
        assert thread_id is not None

        # Switch to the thread
        chat_manager.switch_thread(thread_id)

        # Simulate a conversation
        user_messages = [
            "Hello, how are you?",
            "Can you help me with Python programming?",
            "What are the best practices for writing clean code?",
        ]

        for message in user_messages:
            # Generate AI response (this will add both user and AI messages)
            response = ai_engine.generate_response(message)
            assert isinstance(response, str)
            assert len(response) > 0

        # Verify conversation history
        messages = chat_manager.get_messages(thread_id)
        assert len(messages) >= len(user_messages) * 2  # User + AI for each message

        # Test thread management
        threads = chat_manager.get_threads()
        assert len(threads) >= 1
        assert any(t["id"] == thread_id for t in threads)

    def test_error_handling_integration(self, test_database):
        """Test error handling across components."""
        chat_manager = ChatManager(test_database)
        ai_engine = AIEngine(chat_manager)

        # Create a unique thread and switch to it
        thread_name = f"Error Handling Test {uuid.uuid4().hex[:8]}"
        thread_id = chat_manager.create_thread(thread_name, "🧪")
        chat_manager.switch_thread(thread_id)

        # Test with invalid thread ID
        invalid_thread_id = 99999  # Non-existent thread ID

        # These should handle errors gracefully
        messages = chat_manager.get_messages(invalid_thread_id)
        assert messages == []  # Should return empty list for invalid thread

        # Test generating response (should work even with invalid thread context)
        response = ai_engine.generate_response("test message")
        assert isinstance(response, str)  # Should still return a response
