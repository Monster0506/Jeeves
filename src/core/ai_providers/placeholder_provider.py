"""
Placeholder AI Provider for Jeeves AI Assistant.
Provides simple keyword-based responses as a fallback when no AI service is available.
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_provider import BaseAIProvider

logger = logging.getLogger(__name__)


class PlaceholderProvider(BaseAIProvider):
    """Placeholder AI provider with simple keyword-based responses."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the placeholder provider.

        Args:
            config: Configuration dictionary (not used in placeholder)
        """
        super().__init__(config)
        self.response_templates = [
            "I understand you're asking about {topic}. Let me help you with that.",
            "That's an interesting question about {topic}. Here's what I can tell you.",
            "Regarding {topic}, I can provide some insights.",
            "I see you're interested in {topic}. Let me share some information about that.",
            "Great question about {topic}! Here's what I know.",
        ]

    def initialize(self) -> bool:
        """
        Initialize the placeholder provider.

        Returns:
            Always returns True (placeholder is always available)
        """
        self.is_initialized = True
        logger.info("Placeholder AI provider initialized")
        return True

    def generate_response(
        self,
        user_message: str,
        context: Optional[List[Dict]] = None,
        attachments: Optional[List[Dict]] = None,
    ) -> str:
        """
        Generate a placeholder response based on keywords.

        Args:
            user_message: The user's input message
            context: Optional conversation context (not used in placeholder)
            attachments: Optional list of attachment dictionaries (not used in placeholder)

        Returns:
            Generated placeholder response
        """
        # Simulate processing time
        time.sleep(0.5)

        # Check if user is asking about tools and we have tools registered
        message_lower = user_message.lower()
        if any(word in message_lower for word in ["tools", "functions", "what can you do"]) and self.registered_tools:
            return "PLACEHOLDER: I have several tools available! I can help you with calculations, weather information, and more. Just ask me to use them!"

        # Handle attachments if present
        if attachments:
            attachment_info = f" (with {len(attachments)} attachment(s) from sandbox)"
            return f"PLACEHOLDER: I see you've attached {len(attachments)} file(s) that have been securely copied to the sandbox. In a real AI system, I would analyze these files from the sandbox location and provide insights based on their content. For now, this is a placeholder response.{attachment_info}"

        return "PLACEHOLDER: " + self._generate_placeholder_response(user_message)

    def _generate_placeholder_response(self, user_message: str) -> str:
        """
        Generate a placeholder response based on keywords.

        Args:
            user_message: User's message

        Returns:
            Generated response
        """
        message_lower = user_message.lower()

        # Greeting responses
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm Jeeves, your AI assistant. How can I help you today?"

        # Help responses
        elif any(word in message_lower for word in ["help", "assist"]):
            return "I'm here to help! You can ask me questions, have conversations, or just chat. What would you like to know?"

        # Weather responses
        elif any(word in message_lower for word in ["weather", "temperature"]):
            return "I'd be happy to help with weather information, but I don't have access to real-time weather data yet. This is a placeholder response!"

        # Time/date responses
        elif any(word in message_lower for word in ["time", "date"]):
            now = datetime.now()
            return f"The current time is {now.strftime('%I:%M %p')} on {now.strftime('%B %d, %Y')}."

        # Identity responses
        elif any(word in message_lower for word in ["name", "who are you"]):
            return "I'm Jeeves, your AI assistant! I'm designed to help you with various tasks and conversations."

        # Thank you responses
        elif any(word in message_lower for word in ["thank", "thanks"]):
            return "You're welcome! I'm glad I could help. Is there anything else you'd like to know?"

        # Goodbye responses
        elif any(word in message_lower for word in ["bye", "goodbye", "see you"]):
            return "Goodbye! Feel free to come back anytime if you need assistance."

        # AI/model responses
        elif any(word in message_lower for word in ["ai", "model", "gemini", "openai"]):
            return "I'm currently running with placeholder responses. In the future, I'll be connected to real AI services like Gemini or OpenAI for more sophisticated responses!"

        # Default responses based on message length
        else:
            if len(user_message) < 10:
                return "That's interesting! Could you tell me more about that?"
            elif len(user_message) < 50:
                return "I see what you're saying. Let me think about that for a moment... This is a placeholder response while I work on real AI integration!"
            else:
                return "That's a detailed question! I'm currently running with placeholder responses, but I'm designed to handle complex queries like yours. In the future, I'll be able to provide more sophisticated answers."

    def is_available(self) -> bool:
        """
        Check if the placeholder provider is available.

        Returns:
            Always returns True (placeholder is always available)
        """
        return True

    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the placeholder provider.

        Returns:
            Dictionary containing provider information
        """
        info = super().get_provider_info()
        info.update(
            {
                "type": "placeholder",
                "description": "Simple keyword-based responses for testing and fallback",
                "capabilities": [
                    "basic keyword matching",
                    "time/date responses",
                    "greetings",
                ],
            }
        )
        return info

    def suggest_responses(self, user_message: str, count: int = 3) -> List[str]:
        """
        Suggest possible responses to a user message.

        Args:
            user_message: User's message
            count: Number of suggestions to generate

        Returns:
            List of suggested responses
        """
        suggestions = []
        message_lower = user_message.lower()

        # Generate contextual suggestions
        if any(word in message_lower for word in ["hello", "hi"]):
            suggestions = [
                "Hello! How can I assist you today?",
                "Hi there! What would you like to know?",
                "Greetings! I'm here to help.",
            ]
        elif any(word in message_lower for word in ["weather"]):
            suggestions = [
                "I can help you find weather information for your location.",
                "Would you like me to check the weather forecast?",
                "I can provide weather updates, but I need your location first.",
            ]
        elif any(word in message_lower for word in ["help"]):
            suggestions = [
                "I can help with various tasks. What do you need?",
                "I'm here to assist! What would you like to know?",
                "I can answer questions, provide information, or just chat. What interests you?",
            ]
        else:
            suggestions = [
                "That's interesting! Tell me more about that.",
                "I'd be happy to help with that. What specific information do you need?",
                "I can assist you with that. Let me know what you'd like to know.",
            ]

        return suggestions[:count]
