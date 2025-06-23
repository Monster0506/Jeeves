"""
AI Provider Manager for Jeeves AI Assistant.
Manages multiple AI providers and handles switching between them.
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from .ai_providers import BaseAIProvider, GeminiProvider, PlaceholderProvider

logger = logging.getLogger(__name__)


class AIProviderManager:
    """Manages multiple AI providers and handles provider switching."""

    def __init__(self):
        """Initialize the AI provider manager."""
        self.providers: Dict[str, BaseAIProvider] = {}
        self.current_provider: Optional[BaseAIProvider] = None
        self.provider_order = ["gemini", "placeholder"]  # Priority order
        self.registered_tools: Dict[str, Callable] = {}

        # Register available providers
        self._register_providers()

    def _register_providers(self):
        """Register all available AI providers."""
        try:
            # Register Gemini provider
            gemini_config = self._get_gemini_config()
            self.providers["gemini"] = GeminiProvider(gemini_config)
            logger.info("Registered Gemini provider")
        except Exception as e:
            logger.warning(f"Failed to register Gemini provider: {e}")

        # Register placeholder provider (always available)
        self.providers["placeholder"] = PlaceholderProvider()
        logger.info("Registered Placeholder provider")

    def _get_gemini_config(self) -> Dict[str, Any]:
        """Get Gemini provider configuration."""
        return {
            "model": "gemini-2.0-flash",
            "max_output_tokens": 2048,
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "system_instruction": None,  # Use default
            "enable_tool_calling": True,
            "automatic_function_calling": True,
            "max_tool_calls": 5,
        }

    def initialize(self) -> bool:
        """
        Initialize the AI provider manager and select the best available provider.

        Returns:
            True if at least one provider was initialized successfully
        """
        logger.info("Initializing AI provider manager...")

        # Try to initialize providers in priority order
        for provider_name in self.provider_order:
            if provider_name in self.providers:
                provider = self.providers[provider_name]

                logger.info(f"Attempting to initialize {provider_name} provider...")
                if provider.initialize():
                    self.current_provider = provider
                    logger.info(f"Successfully initialized {provider_name} provider")

                    # Register tools with the current provider
                    self._register_tools_with_provider(provider)

                    return True
                else:
                    logger.warning(f"Failed to initialize {provider_name} provider")

        # If no provider was initialized, use placeholder as fallback
        if "placeholder" in self.providers:
            self.current_provider = self.providers["placeholder"]
            logger.info("Using placeholder provider as fallback")
            return True

        logger.error("No AI providers could be initialized")
        return False

    def _register_tools_with_provider(self, provider: BaseAIProvider):
        """Register all tools with the given provider."""
        for name, func in self.registered_tools.items():
            try:
                provider.register_tool(name, func)
                logger.info(f"Registered tool '{name}' with {provider.provider_name}")
            except Exception as e:
                logger.error(f"Failed to register tool '{name}' with {provider.provider_name}: {e}")

    def register_tool(self, name: str, function: Callable, description: Optional[str] = None) -> bool:
        """
        Register a tool/function that can be used by all providers.

        Args:
            name: Name of the tool
            function: The callable function
            description: Optional description of the tool

        Returns:
            True if registration was successful, False otherwise
        """
        try:
            self.registered_tools[name] = function

            # Register with current provider if available
            if self.current_provider:
                self.current_provider.register_tool(name, function, description)

            logger.info(f"Registered tool '{name}' with AI provider manager")
            return True
        except Exception as e:
            logger.error(f"Failed to register tool '{name}': {e}")
            return False

    def unregister_tool(self, name: str) -> bool:
        """
        Unregister a tool/function from all providers.

        Args:
            name: Name of the tool to unregister

        Returns:
            True if unregistration was successful, False otherwise
        """
        # Check if tool exists in manager
        if name not in self.registered_tools:
            logger.warning(f"Tool '{name}' not found in manager")
            return False

        try:
            # Remove from manager
            del self.registered_tools[name]

            # Remove from current provider
            if self.current_provider:
                self.current_provider.unregister_tool(name)

            logger.info(f"Unregistered tool '{name}' from AI provider manager")
            return True
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
            # Filter args to only include parameters that the function accepts
            import inspect

            func = self.registered_tools[name]
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())

            # Filter args to only include valid parameters
            filtered_args = {k: v for k, v in args.items() if k in param_names}

            result = func(**filtered_args)
            logger.info(f"Executed tool '{name}' with args: {filtered_args}")
            return result
        except Exception as e:
            logger.error(f"Failed to execute tool '{name}': {e}")
            raise

    def get_current_provider(self) -> Optional[BaseAIProvider]:
        """
        Get the currently active AI provider.

        Returns:
            Current AI provider or None if none is available
        """
        return self.current_provider

    def switch_provider(self, provider_name: str) -> bool:
        """
        Switch to a different AI provider.

        Args:
            provider_name: Name of the provider to switch to

        Returns:
            True if the switch was successful, False otherwise
        """
        if provider_name not in self.providers:
            logger.error(f"Provider '{provider_name}' not found")
            return False

        provider = self.providers[provider_name]

        if not provider.initialize():
            logger.error(f"Failed to initialize provider '{provider_name}'")
            return False

        # Clean up current provider
        if self.current_provider:
            self.current_provider.cleanup()

        self.current_provider = provider

        # Register tools with the new provider
        self._register_tools_with_provider(provider)

        logger.info(f"Switched to {provider_name} provider")
        return True

    def generate_response(
        self,
        user_message: str,
        context: Optional[List[Dict]] = None,
        attachments: Optional[List[Dict]] = None,
    ) -> str:
        """
        Generate a response using the current AI provider.

        Args:
            user_message: The user's input message
            context: Optional conversation context
            attachments: Optional list of attachment dictionaries

        Returns:
            Generated AI response
        """
        if not self.current_provider:
            return "Sorry, no AI provider is currently available."

        try:
            return self.current_provider.generate_response(user_message, context, attachments)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

    def refresh_memory(self) -> bool:
        """
        Refresh memory content for the current provider.

        Returns:
            True if memory was refreshed successfully, False otherwise
        """
        if not self.current_provider:
            logger.warning("No current provider to refresh memory for")
            return False

        try:
            if hasattr(self.current_provider, "refresh_memory"):
                success = self.current_provider.refresh_memory()
                if success:
                    logger.info("Memory refreshed successfully for current provider")
                else:
                    logger.warning("Failed to refresh memory for current provider")
                return success
            else:
                logger.debug("Current provider does not support memory refresh")
                return True
        except Exception as e:
            logger.error(f"Error refreshing memory: {e}")
            return False

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """
        Get information about all available providers.

        Returns:
            List of provider information dictionaries
        """
        providers_info = []

        for name, provider in self.providers.items():
            info = provider.get_provider_info()
            info["name"] = name
            info["is_current"] = provider == self.current_provider
            providers_info.append(info)

        return providers_info

    def get_provider_status(self) -> Dict[str, Any]:
        """
        Get the status of the current provider.

        Returns:
            Dictionary containing current provider status
        """
        if not self.current_provider:
            return {"provider": None, "status": "no_provider", "available": False}

        info = self.current_provider.get_provider_info()
        info["status"] = "active" if self.current_provider.is_available() else "unavailable"
        return info

    def add_provider(self, name: str, provider: BaseAIProvider) -> bool:
        """
        Add a custom AI provider.

        Args:
            name: Name for the provider
            provider: Provider instance

        Returns:
            True if provider was added successfully
        """
        if name in self.providers:
            logger.warning(f"Provider '{name}' already exists, overwriting")

        self.providers[name] = provider

        # Register tools with the new provider
        self._register_tools_with_provider(provider)

        logger.info(f"Added custom provider: {name}")
        return True

    def remove_provider(self, name: str) -> bool:
        """
        Remove an AI provider.

        Args:
            name: Name of the provider to remove

        Returns:
            True if provider was removed successfully
        """
        if name not in self.providers:
            logger.warning(f"Provider '{name}' not found")
            return False

        provider = self.providers[name]

        # Don't remove if it's the current provider
        if provider == self.current_provider:
            logger.error(f"Cannot remove current provider '{name}'")
            return False

        provider.cleanup()
        del self.providers[name]
        logger.info(f"Removed provider: {name}")
        return True

    def cleanup(self):
        """Clean up all providers."""
        for name, provider in self.providers.items():
            try:
                provider.cleanup()
                logger.info(f"Cleaned up {name} provider")
            except Exception as e:
                logger.error(f"Error cleaning up {name} provider: {e}")

        self.current_provider = None
        self.registered_tools.clear()
        logger.info("AI provider manager cleaned up")

    def __str__(self) -> str:
        current = self.current_provider.provider_name if self.current_provider else "None"
        tools_count = len(self.registered_tools)
        return f"AIProviderManager(current={current}, providers={list(self.providers.keys())}, tools={tools_count})"

    def __repr__(self) -> str:
        return self.__str__()
