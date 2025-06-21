"""
Base AI Provider interface for Jeeves AI Assistant.
Defines the contract that all AI providers must implement.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable, Union
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
        self.registered_tools: Dict[str, Callable] = {}
        self.tool_config: Dict[str, Any] = {}
    
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
    
    def register_tool(self, name: str, function: Callable, description: str = None) -> bool:
        """
        Register a tool/function that can be called by the AI.
        
        Args:
            name: Name of the tool
            function: The callable function
            description: Optional description of the tool
            
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            self.registered_tools[name] = function
            logger.info(f"Registered tool '{name}' with {self.provider_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register tool '{name}': {e}")
            return False
    
    def unregister_tool(self, name: str) -> bool:
        """
        Unregister a tool/function.
        
        Args:
            name: Name of the tool to unregister
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        try:
            if name in self.registered_tools:
                del self.registered_tools[name]
                logger.info(f"Unregistered tool '{name}' from {self.provider_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to unregister tool '{name}': {e}")
            return False
    
    def get_registered_tools(self) -> Dict[str, Callable]:
        """
        Get all registered tools.
        
        Returns:
            Dictionary of registered tool names and their functions
        """
        return self.registered_tools.copy()
    
    def execute_tool(self, name: str, args: Dict[str, Any]) -> Any:
        """
        Execute a registered tool with the given arguments.
        
        Args:
            name: Name of the tool to execute
            args: Arguments to pass to the tool
            
        Returns:
            Result of the tool execution
            
        Raises:
            KeyError: If tool is not registered
            Exception: If tool execution fails
        """
        if name not in self.registered_tools:
            raise KeyError(f"Tool '{name}' is not registered")
        
        try:
            result = self.registered_tools[name](**args)
            logger.info(f"Executed tool '{name}' with args: {args}")
            return result
        except Exception as e:
            logger.error(f"Failed to execute tool '{name}': {e}")
            raise
    
    def set_tool_config(self, config: Dict[str, Any]) -> None:
        """
        Set tool configuration for the provider.
        
        Args:
            config: Tool configuration dictionary
        """
        self.tool_config = config.copy()
        logger.info(f"Updated tool config for {self.provider_name}")
    
    def get_tool_config(self) -> Dict[str, Any]:
        """
        Get current tool configuration.
        
        Returns:
            Current tool configuration dictionary
        """
        return self.tool_config.copy()
    
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
            'config': self.config,
            'registered_tools': list(self.registered_tools.keys()),
            'tool_config': self.tool_config
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
        self.registered_tools.clear()
        self.tool_config.clear()
        logger.info(f"Cleaned up {self.provider_name}")
    
    def __str__(self) -> str:
        return f"{self.provider_name}(initialized={self.is_initialized}, available={self.is_available()}, tools={len(self.registered_tools)})"
    
    def __repr__(self) -> str:
        return self.__str__() 