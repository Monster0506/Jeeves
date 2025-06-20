"""
Base AI Provider interface for Jeeves AI Assistant.
Defines the contract that all AI providers must implement.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the AI provider.
        
        Args:
            config: Configuration dictionary for the provider
        """
        self.config = config or {}
        self.is_initialized = False
        self.provider_name = self.__class__.__name__
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the AI provider.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def generate_response(self, user_message: str, context: List[Dict] = None) -> str:
        """
        Generate an AI response to the user's message.
        
        Args:
            user_message: The user's input message
            context: Optional conversation context (list of previous messages)
            
        Returns:
            Generated AI response
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the AI provider is available and ready to use.
        
        Returns:
            True if the provider is available, False otherwise
        """
        pass
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the AI provider.
        
        Returns:
            Dictionary containing provider information
        """
        return {
            'name': self.provider_name,
            'is_initialized': self.is_initialized,
            'is_available': self.is_available(),
            'config': self.config
        }
    
    def validate_config(self) -> bool:
        """
        Validate the provider configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        return True
    
    def cleanup(self):
        """Clean up resources used by the provider."""
        self.is_initialized = False
        logger.info(f"Cleaned up {self.provider_name}")
    
    def __str__(self) -> str:
        return f"{self.provider_name}(initialized={self.is_initialized}, available={self.is_available()})"
    
    def __repr__(self) -> str:
        return self.__str__() 