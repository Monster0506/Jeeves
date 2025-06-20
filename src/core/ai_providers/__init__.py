"""
AI Providers module for Jeeves AI Assistant.
Contains different AI backend implementations.
"""

from .base_provider import BaseAIProvider
from .gemini_provider import GeminiProvider
from .placeholder_provider import PlaceholderProvider

__all__ = ['BaseAIProvider', 'GeminiProvider', 'PlaceholderProvider'] 