"""
Base AI Provider interface for Jeeves AI Assistant.
Defines the contract that all AI providers must implement.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize the AI provider.

        Args:
            config: Configuration dictionary for the provider
        """
        self.config = config or {}
        self.is_initialized = False
        self.provider_name = self.__class__.__name__
        self.registered_tools: dict[str, Callable] = {}
        self.tool_config: dict[str, Any] = {}

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the AI provider.

        Returns:
            True if initialization was successful, False otherwise
        """
        pass

    @abstractmethod
    def generate_response(
        self,
        user_message: str,
        context: Optional[list[dict]] = None,
        attachments: Optional[list[dict]] = None,
    ) -> str:
        """
        Generate an AI response to the user's message.

        Args:
            user_message: The user's input message
            context: Optional conversation context (list of previous messages)
            attachments: Optional list of attachment dictionaries with file information

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

    def register_tool(self, name: str, function: Callable, description: Optional[str] = None) -> bool:
        """
        Register a tool/function that can be used by the provider.

        Args:
            name: Name of the tool
            function: The callable function
            description: Optional description of the tool

        Returns:
            True if registration was successful, False otherwise
        """
        try:
            self.registered_tools[name] = function
            if description:
                self.tool_config[name] = {"description": description}
            logger.info(f"Registered tool '{name}' with {self.provider_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register tool '{name}' with {self.provider_name}: {e}")
            return False

    def unregister_tool(self, name: str) -> bool:
        """
        Unregister a tool/function from the provider.

        Args:
            name: Name of the tool to unregister

        Returns:
            True if unregistration was successful, False otherwise
        """
        try:
            found = False
            if name in self.registered_tools:
                del self.registered_tools[name]
                found = True
            if name in self.tool_config:
                del self.tool_config[name]
            logger.info(f"Unregistered tool '{name}' from {self.provider_name}")
            return found
        except Exception as e:
            logger.error(f"Failed to unregister tool '{name}' from {self.provider_name}: {e}")
            return False

    def get_registered_tools(self) -> dict[str, Callable]:
        """
        Get all registered tools.

        Returns:
            Dictionary of registered tools
        """
        return self.registered_tools.copy()

    def execute_tool(self, name: str, args: dict[str, Any]) -> Any:
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

    def set_tool_config(self, config: dict[str, Any]) -> None:
        """
        Set tool configuration for the provider.

        Args:
            config: Tool configuration dictionary
        """
        self.tool_config = config.copy()
        logger.info(f"Updated tool config for {self.provider_name}")

    def get_tool_config(self) -> dict[str, Any]:
        """
        Get current tool configuration.

        Returns:
            Current tool configuration dictionary
        """
        return self.tool_config.copy()

    def get_provider_info(self) -> dict[str, Any]:
        """
        Get detailed information about the provider.

        Returns:
            Dictionary containing provider information
        """
        info = {
            "provider_name": self.provider_name,
            "name": self.provider_name,  # for backward compatibility
            "is_initialized": self.is_initialized,
            "is_available": self.is_available(),
            "registered_tools_count": len(self.registered_tools),
            "registered_tools": list(self.registered_tools.keys()),  # for backward compatibility
            "tool_config": self.tool_config.copy(),  # for backward compatibility
            "config": self.config.copy() if self.config else {},
        }
        return info

    def validate_config(self) -> bool:
        """
        Validate the provider configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        # Base implementation - can be overridden by subclasses
        return True

    def cleanup(self) -> None:
        """Clean up provider resources."""
        self.registered_tools.clear()
        self.tool_config.clear()
        self.is_initialized = False
        logger.info(f"{self.provider_name} cleaned up")

    def refresh_memory(self) -> bool:
        """
        Refresh memory content and update system instruction if needed.
        Base implementation - can be overridden by subclasses that support memory.

        Returns:
            True if memory was refreshed successfully, False otherwise
        """
        # Base implementation does nothing - subclasses can override
        logger.debug(f"{self.provider_name} does not support memory refresh")
        return True

    def update_system_instruction(self, new_instruction: str) -> bool:
        """
        Update the system instruction.
        Base implementation - can be overridden by subclasses.

        Args:
            new_instruction: New system instruction

        Returns:
            True if successful
        """
        # Base implementation does nothing - subclasses can override
        logger.debug(f"{self.provider_name} does not support system instruction updates")
        return True

    def get_system_instruction(self) -> Optional[str]:
        """
        Get the current system instruction.
        Base implementation - can be overridden by subclasses.

        Returns:
            Current system instruction or empty string
        """
        # Base implementation returns empty string - subclasses can override
        return ""

    def __str__(self) -> str:
        return f"{self.provider_name}(initialized={self.is_initialized}, available={self.is_available()}, tools={len(self.registered_tools)})"

    def __repr__(self) -> str:
        return self.__str__()
