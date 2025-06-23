"""
AI Engine for Jeeves AI Assistant.
Handles AI responses and integrates with the chat manager.
Now uses a modular provider system for different AI backends.
"""

import logging
from typing import Dict, List, Optional

from .ai_provider_manager import AIProviderManager
from .chat_manager import ChatManager
from .tools import JeevesTools

logger = logging.getLogger(__name__)


class AIEngine:
    """AI Engine that generates responses and manages conversation flow."""

    def __init__(self, chat_manager: ChatManager):
        self.chat_manager = chat_manager

        self.provider_manager = AIProviderManager()
        self.tools = JeevesTools(chat_manager)

        self.chat_manager.register_message_callback(self._on_message_added)
        self.chat_manager.register_thread_callback(self._on_thread_changed)

        self._initialize_providers()

    @property
    def conversation_history(self) -> List[Dict]:
        """
        Get the current conversation history for backward compatibility.

        Returns:
            List of recent messages in the current thread
        """
        return self.get_conversation_context()

    def _initialize_providers(self):
        """Initialize AI providers."""
        try:
            if self.provider_manager.initialize():
                current_provider = self.provider_manager.get_current_provider()
                logger.info(f"AI Engine initialized with provider: {current_provider.provider_name}")

                # Register tools
                self._register_tools()
            else:
                logger.warning("Failed to initialize any AI providers, using fallback")
        except Exception as e:
            logger.error(f"Error initializing AI providers: {e}")

    def _register_tools(self):
        """Register all available tools with the provider manager."""
        try:
            # Get all tools and their descriptions
            tools = self.tools.get_registered_tools()
            descriptions = self.tools.get_tool_descriptions()

            # Register each tool
            for tool_name, tool_func in tools.items():
                description = descriptions.get(tool_name, f"Tool: {tool_name}")
                self.provider_manager.register_tool(tool_name, tool_func, description)
                logger.info(f"Registered tool: {tool_name}")

            logger.info(f"Registered {len(tools)} tools with provider manager")
        except Exception as e:
            logger.error(f"Error registering tools: {e}")

    def _on_message_added(self, message: Dict):
        """Callback when a new message is added to the conversation."""
        # No longer needed: self.conversation_history.append(message)
        pass

    def _on_thread_changed(self, thread: Dict):
        """Callback when thread changes."""
        # No longer needed: self.conversation_history = []
        pass

    def generate_response(self, user_message: str, attachments: Optional[List[Dict]] = None) -> str:
        """
        Generate an AI response to the user's message.

        Args:
            user_message: The user's input message
            attachments: Optional list of attachment dictionaries

        Returns:
            Generated AI response
        """
        logger.info(f"Generating response for message with " f"{len(attachments) if attachments else 0} attachments")

        # Format new attachments for database storage
        db_attachments = None
        if attachments:
            db_attachments = [
                {
                    "file_name": att.get("file_name"),
                    "file_path": att.get("sandbox_path"),  # Relative path for DB
                    "file_size": att.get("file_size"),
                    "mime_type": att.get("mime_type"),
                    "hash": att.get("hash"),
                }
                for att in attachments
            ]

        # Add user message to database
        message_id = self.chat_manager.add_user_message(user_message, content_type="text", attachments=db_attachments)

        # Refresh memory at the beginning of each chat session
        self._refresh_memory_if_needed()

        # Get conversation context
        context = self.get_conversation_context()

        # Prepare all attachments for the AI provider (historical + new)
        ai_attachments = []

        # 1. Process historical attachments from context
        from src.core.file_handler import JeevesFileHandler

        file_handler = JeevesFileHandler()

        for message in context:
            if message.get("attachments"):
                for att in message["attachments"]:
                    # Convert stored relative path to absolute sandbox path
                    sandbox_path = att.get("file_path")
                    if sandbox_path:
                        ai_attachments.append(
                            {
                                "file_name": att.get("file_name"),
                                "file_path": file_handler.get_absolute_path(sandbox_path),
                                "mime_type": att.get("mime_type"),
                                "file_size": att.get("file_size"),
                            }
                        )

        # 2. Process new attachments for this message
        if attachments:
            for att in attachments:
                # Use the absolute path already prepared
                ai_attachments.append(
                    {
                        "file_name": att.get("file_name"),
                        "file_path": att.get("sandbox_absolute_path"),
                        "mime_type": att.get("mime_type"),
                        "file_size": att.get("file_size"),
                    }
                )

        # Pass full context and all attachments to the provider
        response = self.provider_manager.generate_response(user_message, context, ai_attachments)

        # log context
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("-- SENDING CONTEXT TO AI --")
            for msg in context:
                logger.debug(f"[{msg.get('sender', 'unknown')}]: {msg.get('content', 'NONE')}")
            if ai_attachments:
                logger.debug(f"-- With {len(ai_attachments)} attachments --")
                for att in ai_attachments:
                    logger.debug(f"  - {att.get('file_name')}")
            logger.debug("-" * 35)

        # Add AI message
        self.chat_manager.add_ai_message(response)

        logger.info(f"Generated response for message {message_id} using " f"{self.provider_manager.get_current_provider().provider_name}")
        return response

    def _refresh_memory_if_needed(self):
        """
        Refresh memory content if the current provider supports it.
        This ensures the AI has the latest memory content for each conversation.
        """
        try:
            success = self.provider_manager.refresh_memory()
            if success:
                logger.debug("Memory refreshed successfully")
            else:
                logger.warning("Failed to refresh memory")
        except Exception as e:
            logger.error(f"Error refreshing memory: {e}")

    def refresh_memory(self) -> bool:
        """
        Manually refresh memory content.
        This can be called when memory is updated externally.

        Returns:
            True if memory was refreshed successfully, False otherwise
        """
        try:
            success = self.provider_manager.refresh_memory()
            if success:
                logger.info("Memory refreshed successfully")
            else:
                logger.warning("Failed to refresh memory")
            return success
        except Exception as e:
            logger.error(f"Error refreshing memory: {e}")
            return False

    def get_conversation_context(self, thread_id: Optional[int] = None) -> List[Dict]:
        """
        Get conversation context for AI processing.

        Args:
            thread_id: Thread ID (uses current thread if None)

        Returns:
            List of all messages for context
        """
        if thread_id is None:
            thread_id = self.chat_manager.get_current_thread_id()

        if thread_id is None:
            return []

        # Get all messages for context
        messages = self.chat_manager.get_messages(thread_id)
        return messages

    def switch_ai_provider(self, provider_name: str) -> bool:
        """
        Switch to a different AI provider.

        Args:
            provider_name: Name of the provider to switch to

        Returns:
            True if the switch was successful
        """
        return self.provider_manager.switch_provider(provider_name)

    def get_current_provider_info(self) -> Dict:
        """
        Get information about the current AI provider.

        Returns:
            Dictionary containing provider information
        """
        return self.provider_manager.get_provider_status()

    def get_available_providers(self) -> List[Dict]:
        """
        Get information about all available AI providers.

        Returns:
            List of provider information dictionaries
        """
        return self.provider_manager.get_available_providers()

    def analyze_conversation(self, thread_id: Optional[int] = None) -> Dict:
        """
        Analyze the current conversation for insights.

        Args:
            thread_id: Thread ID (uses current thread if None)

        Returns:
            Analysis results
        """
        if thread_id is None:
            thread_id = self.chat_manager.get_current_thread_id()

        if thread_id is None:
            return {}

        messages = self.chat_manager.get_messages(thread_id)

        if not messages:
            return {"status": "empty_conversation"}

        # Basic analysis
        user_messages = [m for m in messages if m["sender"] == "user"]
        ai_messages = [m for m in messages if m["sender"] == "ai"]

        total_length = sum(len(m["content"]) for m in messages)
        avg_length = total_length / len(messages) if messages else 0

        # Simple topic detection (placeholder)
        common_words = [
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        ]
        all_text = " ".join(m["content"].lower() for m in messages)
        words = [w for w in all_text.split() if w not in common_words and len(w) > 3]

        # Get most common words (simple approach)
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1

        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "ai_messages": len(ai_messages),
            "conversation_length": total_length,
            "average_message_length": round(avg_length, 2),
            "topics": [word for word, count in top_words],
            "conversation_duration": self._calculate_duration(messages),
            "interaction_pattern": self._analyze_interaction_pattern(messages),
            "ai_provider": self.get_current_provider_info(),
        }

    def _calculate_duration(self, messages: List[Dict]) -> str:
        """Calculate the duration of a conversation."""
        if len(messages) < 2:
            return "0 minutes"

        try:
            from datetime import datetime

            first_time = datetime.fromisoformat(messages[0]["timestamp"].replace("Z", "+00:00"))
            last_time = datetime.fromisoformat(messages[-1]["timestamp"].replace("Z", "+00:00"))
            duration = last_time - first_time

            minutes = duration.total_seconds() / 60
            if minutes < 1:
                return "Less than 1 minute"
            elif minutes < 60:
                return f"{int(minutes)} minutes"
            else:
                hours = minutes / 60
                return f"{hours:.1f} hours"
        except (ValueError, KeyError) as e:
            logger.warning(f"Could not calculate conversation duration: {e}")
            return "Unknown"

    def _analyze_interaction_pattern(self, messages: List[Dict]) -> str:
        """Analyze the interaction pattern between user and AI."""
        if not messages:
            return "No interaction"

        # Simple analysis of interaction pattern
        senders = [m["sender"] for m in messages]

        if len(senders) < 2:
            return "Single message"

        # Check for rapid back-and-forth
        rapid_exchanges = 0
        try:
            from datetime import datetime

            for i in range(1, len(messages)):
                try:
                    time1 = datetime.fromisoformat(messages[i - 1]["timestamp"].replace("Z", "+00:00"))
                    time2 = datetime.fromisoformat(messages[i]["timestamp"].replace("Z", "+00:00"))
                    if (time2 - time1).total_seconds() < 60:
                        rapid_exchanges += 1
                except (ValueError, KeyError) as e:
                    logger.warning(f"Could not analyze interaction pattern: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error analyzing interaction pattern: {e}")

        if rapid_exchanges > len(messages) / 2:
            return "Rapid back-and-forth"

        return "Normal interaction"

    def suggest_responses(self, user_message: str, count: int = 3) -> List[str]:
        """
        Suggest a few short, relevant responses.

        Args:
            user_message: The user's message
            count: Number of suggestions

        Returns:
            List of suggested responses
        """
        # Placeholder for a more advanced implementation
        # This could be powered by a smaller, faster model or keyword analysis

        suggestions = [
            "Tell me more about that.",
            "Can you elaborate on your last point?",
            "What are your thoughts on this?",
        ]

        # Simple keyword-based suggestions
        if "help" in user_message.lower():
            suggestions.append("What do you need help with?")
        if "question" in user_message.lower():
            suggestions.append("I'll do my best to answer.")

        return suggestions[:count]

    def get_ai_stats(self) -> Dict:
        """
        Get statistics about AI usage and performance.

        Returns:
            Dictionary with AI stats
        """
        provider_info = self.get_current_provider_info()

        return {
            "provider": provider_info.get("name", "Unknown"),
            "model": provider_info.get("model", "Unknown"),
            "total_responses": self.chat_manager.get_stats().get("total_ai_messages", 0),
            "average_response_time": 0,  # Placeholder
        }

    def cleanup(self):
        """Cleanup AI Engine resources."""
        if self.provider_manager:
            self.provider_manager.cleanup()
        logger.info("AI Engine cleaned up")
