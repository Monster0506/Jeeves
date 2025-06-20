"""
AI Engine for Jeeves AI Assistant.
Handles AI responses and integrates with the chat manager.
Now uses a modular provider system for different AI backends.
"""
import logging
import time
from typing import Dict, List, Optional
from .chat_manager import ChatManager
from .ai_provider_manager import AIProviderManager

logger = logging.getLogger(__name__)


class AIEngine:
    """AI Engine that generates responses and manages conversation flow."""
    
    def __init__(self, chat_manager: ChatManager):
        self.chat_manager = chat_manager
        self.conversation_history: List[Dict] = []
        
        # Initialize AI provider manager
        self.provider_manager = AIProviderManager()
        
        # Register callbacks
        self.chat_manager.register_message_callback(self._on_message_added)
        self.chat_manager.register_thread_callback(self._on_thread_changed)
        
        # Initialize providers
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize AI providers."""
        try:
            if self.provider_manager.initialize():
                current_provider = self.provider_manager.get_current_provider()
                logger.info(f"AI Engine initialized with provider: {current_provider.provider_name}")
            else:
                logger.warning("Failed to initialize any AI providers, using fallback")
        except Exception as e:
            logger.error(f"Error initializing AI providers: {e}")
    
    def _on_message_added(self, message: Dict):
        """Callback when a new message is added to the conversation."""
        self.conversation_history.append(message)
        logger.debug(f"Message added to history: {message['sender']}")
    
    def _on_thread_changed(self, thread: Dict):
        """Callback when thread changes."""
        # Clear conversation history when switching threads
        self.conversation_history = []
        logger.debug(f"Switched to thread: {thread['name']}")
    
    def generate_response(self, user_message: str) -> str:
        """
        Generate an AI response to the user's message.
        
        Args:
            user_message: The user's input message
            
        Returns:
            Generated AI response
        """
        # Add user message to database
        message_id = self.chat_manager.add_user_message(user_message)
        
        # Get conversation context
        context = self.get_conversation_context()
        
        # Generate response using the current AI provider
        response = self.provider_manager.generate_response(user_message, context)
        
        # Add AI response to database
        ai_message_id = self.chat_manager.add_ai_message(response)
        
        logger.info(f"Generated response for message {message_id} using {self.provider_manager.get_current_provider().provider_name}")
        return response
    
    def get_conversation_context(self, thread_id: int = None) -> List[Dict]:
        """
        Get conversation context for AI processing.
        
        Args:
            thread_id: Thread ID (uses current thread if None)
            
        Returns:
            List of recent messages for context
        """
        if thread_id is None:
            thread_id = self.chat_manager.get_current_thread_id()
        
        if thread_id is None:
            return []
        
        # Get last 10 messages for context
        messages = self.chat_manager.get_messages(thread_id, limit=10)
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
    
    def analyze_conversation(self, thread_id: int = None) -> Dict:
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
            return {'status': 'empty_conversation'}
        
        # Basic analysis
        user_messages = [m for m in messages if m['sender'] == 'user']
        ai_messages = [m for m in messages if m['sender'] == 'ai']
        
        total_length = sum(len(m['content']) for m in messages)
        avg_length = total_length / len(messages) if messages else 0
        
        # Simple topic detection (placeholder)
        common_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        all_text = ' '.join(m['content'].lower() for m in messages)
        words = [w for w in all_text.split() if w not in common_words and len(w) > 3]
        
        # Get most common words (simple approach)
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_messages': len(messages),
            'user_messages': len(user_messages),
            'ai_messages': len(ai_messages),
            'conversation_length': total_length,
            'average_message_length': round(avg_length, 2),
            'topics': [word for word, count in top_words],
            'conversation_duration': self._calculate_duration(messages),
            'interaction_pattern': self._analyze_interaction_pattern(messages),
            'ai_provider': self.get_current_provider_info()
        }
    
    def _calculate_duration(self, messages: List[Dict]) -> str:
        """Calculate the duration of a conversation."""
        if len(messages) < 2:
            return "0 minutes"
        
        try:
            from datetime import datetime
            first_time = datetime.fromisoformat(messages[0]['timestamp'].replace('Z', '+00:00'))
            last_time = datetime.fromisoformat(messages[-1]['timestamp'].replace('Z', '+00:00'))
            duration = last_time - first_time
            
            minutes = duration.total_seconds() / 60
            if minutes < 1:
                return "Less than 1 minute"
            elif minutes < 60:
                return f"{int(minutes)} minutes"
            else:
                hours = minutes / 60
                return f"{hours:.1f} hours"
        except:
            return "Unknown duration"
    
    def _analyze_interaction_pattern(self, messages: List[Dict]) -> str:
        """Analyze the interaction pattern between user and AI."""
        if len(messages) < 4:
            return "Short conversation"
        
        # Check for rapid exchanges
        rapid_exchanges = 0
        for i in range(len(messages) - 1):
            try:
                from datetime import datetime
                current_time = datetime.fromisoformat(messages[i]['timestamp'].replace('Z', '+00:00'))
                next_time = datetime.fromisoformat(messages[i + 1]['timestamp'].replace('Z', '+00:00'))
                
                if (next_time - current_time).total_seconds() < 30:  # Less than 30 seconds
                    rapid_exchanges += 1
            except:
                continue
        
        if rapid_exchanges > len(messages) * 0.5:
            return "Rapid exchange"
        elif rapid_exchanges > len(messages) * 0.2:
            return "Moderate pace"
        else:
            return "Leisurely conversation"
    
    def suggest_responses(self, user_message: str, count: int = 3) -> List[str]:
        """
        Suggest possible responses to a user message.
        
        Args:
            user_message: User's message
            count: Number of suggestions to generate
            
        Returns:
            List of suggested responses
        """
        # Try to get suggestions from current provider if available
        current_provider = self.provider_manager.get_current_provider()
        if hasattr(current_provider, 'suggest_responses'):
            try:
                return current_provider.suggest_responses(user_message, count)
            except Exception as e:
                logger.warning(f"Failed to get suggestions from provider: {e}")
        
        # Fallback to basic suggestions
        suggestions = []
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi']):
            suggestions = [
                "Hello! How can I assist you today?",
                "Hi there! What would you like to know?",
                "Greetings! I'm here to help."
            ]
        elif any(word in message_lower for word in ['weather']):
            suggestions = [
                "I can help you find weather information for your location.",
                "Would you like me to check the weather forecast?",
                "I can provide weather updates, but I need your location first."
            ]
        elif any(word in message_lower for word in ['help']):
            suggestions = [
                "I can help with various tasks. What do you need?",
                "I'm here to assist! What would you like to know?",
                "I can answer questions, provide information, or just chat. What interests you?"
            ]
        else:
            suggestions = [
                "That's interesting! Tell me more about that.",
                "I'd be happy to help with that. What specific information do you need?",
                "I can assist you with that. Let me know what you'd like to know."
            ]
        
        return suggestions[:count]
    
    def get_ai_stats(self) -> Dict:
        """Get AI engine statistics."""
        provider_info = self.get_current_provider_info()
        
        return {
            'total_conversations': len(self.chat_manager.get_threads()),
            'total_messages_processed': len(self.conversation_history),
            'current_thread': self.chat_manager.get_current_thread_id(),
            'engine_status': 'active',
            'current_provider': provider_info.get('name', 'unknown'),
            'provider_status': provider_info.get('status', 'unknown'),
            'available_providers': len(self.provider_manager.providers)
        }
    
    def cleanup(self):
        """Clean up AI engine resources."""
        self.provider_manager.cleanup()
        logger.info("AI Engine cleaned up") 