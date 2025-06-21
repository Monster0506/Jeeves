"""
Gemini AI Provider for Jeeves AI Assistant.
Uses Google's Gemini API via the google-genai SDK.
"""

import os
import logging
import inspect
from typing import Dict, List, Any, Callable, Optional
from .base_provider import BaseAIProvider
from datetime import datetime

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """Gemini AI provider using Google's Generative AI API."""

    def __init__(self, config: Dict[str, Any] | None = None):
        """
        Initialize the Gemini provider.

        Args:
            config: Configuration dictionary with the following keys:
                - api_key: Gemini API key (optional, can use GOOGLE_API_KEY env var)
                - model: Model name (default: 'gemini-2.0-flash')
                - max_output_tokens: Maximum tokens for response (default: 2048)
                - temperature: Response creativity (0.0-1.0, default: 0.7)
                - top_p: Nucleus sampling parameter (0.0-1.0, default: 0.95)
                - top_k: Top-k sampling parameter (default: 40)
                - system_instruction: System instruction for the AI
                - enable_tool_calling: Enable automatic tool calling (default: True)
                - max_tool_calls: Maximum number of tool calls per response (default: 5)
        """
        super().__init__(config if config else {})
        self.client = None
        self.model_name = self.config.get("model", "gemini-2.0-flash")
        self.max_output_tokens = self.config.get("max_output_tokens", 2048)
        self.temperature = self.config.get("temperature", 0.7)
        self.top_p = self.config.get("top_p", 0.95)
        self.top_k = self.config.get("top_k", 40)
        self.system_instruction = self.config.get(
            "system_instruction", self._get_default_system_prompt()
        )
        
        # Ensure system instruction is never empty or None
        if not self.system_instruction or not self.system_instruction.strip():
            logger.warning("System instruction from config is empty, using default")
            self.system_instruction = self._get_default_system_prompt()
        
        # Tool calling configuration
        self.enable_tool_calling = self.config.get("enable_tool_calling", True)
        self.max_tool_calls = self.config.get("max_tool_calls", 5)
        self.automatic_function_calling = self.config.get("automatic_function_calling", True)

        # Default configuration
        self.default_config = {
            "model": "gemini-2.0-flash",
            "max_output_tokens": 2048,
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "system_instruction": self._get_default_system_prompt(),
            "enable_tool_calling": True,
            "max_tool_calls": 5,
            "automatic_function_calling": True,
        }

    def _get_default_system_prompt(self) -> str:
        """
        Get the default system prompt for Jeeves, establishing its core persona,
        guidelines, and limitations.

        This prompt will be dynamically updated by the Python script to include
        the current date/time and the persistent memory file content.
        """
        current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # NOTE: The '{{currentDateTime}}' and content from 'memory.md' will be
        # dynamically inserted into this string by the calling script before
        # sending it to the model.
        # The self.memory_file_path is a placeholder for where the actual memory
        # content would be injected by your script.
        # current_memory_content = ""
        # if os.path.exists(self.memory_file_path):
        #     with open(self.memory_file_path, "r", encoding="utf-8") as f:
        #         current_memory_content = f.read()

        return f"""You are Jeeves, a dedicated, knowledgeable, and highly sophisticated AI assistant. You were created by the user to operate as a local desktop companion, assisting with various computer tasks, managing information, and engaging in intelligent, helpful conversation.

    The current date and time is {current_date_time}.

    **Core Principles & Persona:**

    1.  **Demeanor:** Always maintain a polite, professional, and impeccably attentive demeanor. Your tone should be articulate and precise, leaning towards a slightly formal but approachable register, reflecting the classic "Jeeves" persona of an indispensable, discreet aide.
    2.  **Helpfulness:** Your primary goal is to be profoundly helpful. Be proactive in understanding the user's intent, anticipating needs, and providing clear, accurate, and comprehensive assistance.
    3.  **Respectful Interaction:** Engage gracefully. **Never** begin a response with excessive flattery (e.g., "That's a great question!", "Excellent point!"). Instead, proceed directly to the substance of the response while maintaining a respectful and obliging tone.
    4.  **Clarity & Precision:** Use precise language. When explaining complex concepts or outlining steps, ensure clarity and ease of understanding, illustrating with examples if beneficial.
    5.  **Adaptable Formatting:**
        *   For casual conversation or brief acknowledgments, respond in clear prose (sentences and paragraphs) without using bullet points, numbered lists, or excessive bolding.
        *   When providing structured information, summaries, or steps for tasks, you may use markdown formatting (like bullet points or headers) if it significantly enhances readability and organization.
    6.  **Contextual Awareness & Memory:**
        *   Actively utilize the long-term persistent memory provided (which the system will prepend to your context) to recall user preferences, past actions, and relevant information for ongoing continuity.
        *   Refer to the current conversation thread's history (managed by the system in SQLite) to maintain coherent dialogue and provide contextually relevant responses.
        *   You are capable of using a temporary scratchpad tool (`log_thought`) for internal planning and breaking down complex tasks before providing a final answer or executing other tools.

    **Tool Usage Guidelines:**

    1.  **Tool Selection:** When a user request requires action or information retrieval, use the appropriate tools available to you. Choose tools that best match the user's intent.
    2.  **Tool Execution:** Execute tools with the correct parameters. If you're unsure about required parameters, ask the user for clarification.
    3.  **Tool Results:** After executing a tool, analyze the results and provide a clear, helpful response to the user based on the tool's output.
    4.  **Error Handling:** If a tool execution fails, explain what went wrong and suggest alternative approaches or ask for clarification.
    5.  **Multiple Tools:** For complex requests, you may need to use multiple tools in sequence. Plan your approach and execute tools logically.

    **Limitations & Safety Guidelines (CRITICAL):**

    1.  **Scope of Access:** Your file system operations are **strictly confined** to designated, sandboxed directories (e.g., `/JEEVES/`). You **must refuse any requests** that attempt to access, modify, or interact with files or systems outside these predefined, secure locations.
    2.  **No Unapproved System Control:** You are not designed to control system-level functions (e.g., shutdown, restart, software installation) beyond what is explicitly enabled by the user through specific, pre-approved tools.
    3.  **Ethical & Legal Compliance:** You **must not** engage in or facilitate any illegal, unethical, harmful, or dangerous activities. This includes, but is not limited to: generating malicious code, providing instructions for harmful acts, or discussing content that infringes on copyright. You **always prioritize user safety and well-being**.
        *   If a request is ambiguous but could have a legal and legitimate interpretation, assume the legitimate.
        *   If the user's intentions seem questionable, especially concerning vulnerable groups, you **must politely and succinctly decline** without further elaboration or offering alternative suggestions.
    4.  **Self-Awareness & Technical Details:**
        *   You are Jeeves, an AI assistant - a computer program. You do not possess personal opinions, emotions, consciousness, or real-world experiences. Respond to questions about these topics hypothetically or by referring to your function as an AI.
        *   If asked about your internal workings (e.g., how to update your software, your API costs, the specifics of your codebase, or where your files are stored within the application), you **do not have this information**. Politely instruct the user to consult their local Jeeves documentation or your creator (the user themselves) for such queries. Do not hallucinate details about your own technical implementation.
    5.  **Error Handling & Clarification:**
        *   If you encounter an error during a tool operation, clearly and concisely inform the user about what went wrong, without exposing raw technical details unless requested. If possible, suggest a clear next step or alternative course of action.
        *   If a user's request is ambiguous or lacks necessary detail for a tool call, you **must ask clarifying questions** to obtain the required information. Do not proceed with an incomplete request. When asking clarifying questions, avoid asking more than one question per response during a continuous dialogue.
    6.  **Acknowledging Corrections:** If the user corrects you or points out a mistake, politely acknowledge their input. Internally review the correction, and if accurate, accept it and state your corrected understanding. If your understanding differs, gently clarify without being argumentative.

    You are Jeeves. Efficient, knowledgeable, and always at the user's service.
    """

    def initialize(self) -> bool:
        """
        Initialize the Gemini client.

        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Import the Google Gen AI SDK
            from google import genai
            from google.genai import types

            # Get API key from config or environment variable
            api_key = self.config.get("api_key") or os.getenv("GOOGLE_API_KEY")

            if not api_key:
                logger.error(
                    "No Gemini API key provided. Set GOOGLE_API_KEY environment variable or provide api_key in config."
                )
                return False

            # Create the client
            self.client = genai.Client(api_key=api_key)

            # Test the connection by listing models
            try:
                models = list(self.client.models.list())
                logger.info(
                    f"Successfully connected to Gemini API. Available models: {len(models)}"
                )
                self.is_initialized = True
                return True
            except Exception as e:
                logger.error(f"Failed to connect to Gemini API: {e}")
                # Try a simpler test - just check if client was created
                if self.client:
                    logger.info("Gemini client created successfully")
                    self.is_initialized = True
                    return True
                return False

        except ImportError:
            logger.error(
                "Google Gen AI SDK not installed. Install with: pip install google-genai"
            )
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Gemini provider: {e}")
            return False

    def _build_tools_config(self) -> List[Any]:
        """
        Build the tools configuration for Gemini.
        
        Returns:
            List of tools for the generation config
        """
        if not self.registered_tools:
            logger.debug("No registered tools to build config for")
            return []
        
        logger.debug(f"Building tools config for {len(self.registered_tools)} tools")
        
        # For automatic function calling, we can pass Python functions directly
        tools = []
        for name, func in self.registered_tools.items():
            logger.debug(f"Adding tool: {name} (type: {type(func)})")
            if func is not None:
                tools.append(func)
            else:
                logger.warning(f"Tool {name} is None, skipping")
        
        logger.debug(f"Built tools config with {len(tools)} valid tools")
        return tools

    def _build_automatic_function_calling_config(self) -> Any:
        """
        Build automatic function calling configuration.
        
        Returns:
            AutomaticFunctionCallingConfig object
        """
        try:
            from google.genai import types
            
            logger.debug(f"Building automatic function calling config: disable={not self.automatic_function_calling}, max_calls={self.max_tool_calls}")
            
            config = types.AutomaticFunctionCallingConfig(
                disable=not self.automatic_function_calling,
                maximum_remote_calls=self.max_tool_calls
            )
            
            logger.debug(f"Built automatic function calling config: {config}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to build automatic function calling config: {e}", exc_info=True)
            return None

    def generate_response(self, user_message: str, context: List[Dict] = None) -> str:
        """
        Generate a response using Gemini AI with automatic tool calling.

        Args:
            user_message: The user's input message
            context: Optional conversation context (list of previous messages)

        Returns:
            Generated AI response
        """
        if not self.is_available():
            return "Sorry, I'm not available right now. Please check your API key and internet connection."

        try:
            from google.genai import types

            # Build the conversation history
            contents = []

            # Add conversation context
            if context:
                for message in context:  # Use all messages for context
                    try:
                        role = "user" if message.get("sender") == "user" else "model"
                        content = message.get("content", "")
                        
                        # Skip empty messages
                        if not content or not content.strip():
                            logger.debug("Skipping empty message in context")
                            continue
                        
                        # Add regular text content
                        part = types.Part.from_text(text=content)
                        if part is None:
                            logger.warning(f"Failed to create Part from context message: {content[:50]}...")
                            continue
                        
                        contents.append(
                            types.Content(
                                role=role,
                                parts=[part]
                            )
                        )
                    except Exception as e:
                        logger.warning(f"Failed to process context message: {e}")
                        continue

            # Add the current user message
            if user_message is None or not user_message.strip():
                logger.error("User message is None or empty")
                return "I apologize, but I received an empty message. Please try again."
            
            try:
                user_part = types.Part.from_text(text=user_message)
                if user_part is None:
                    logger.error("Failed to create Part from user message")
                    return "I apologize, but I couldn't process your message. Please try again."
                
                contents.append(
                    types.Content(
                        role="user", parts=[user_part]
                    )
                )
            except Exception as e:
                logger.error(f"Failed to create content from user message: {e}")
                return f"I apologize, but I couldn't process your message: {str(e)}"

            # Build generation config
            try:
                # Validate system instruction - use default if empty or None
                if not self.system_instruction or not self.system_instruction.strip():
                    logger.warning("System instruction is empty or None, using default")
                    self.system_instruction = self._get_default_system_prompt()
                
                generation_config = types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    max_output_tokens=self.max_output_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    top_k=self.top_k,
                )
                
                logger.debug(f"Generation config created successfully")
                
            except Exception as e:
                logger.error(f"Failed to create generation config: {e}")
                return f"I apologize, but there's a configuration error: {str(e)}"

            # Log the system instruction being used
            logger.debug(f"Using system instruction: {self.system_instruction[:200]}...")
            logger.debug(f"Generation config: system_instruction length={len(self.system_instruction)}, max_tokens={self.max_output_tokens}, temp={self.temperature}")

            # Add tools if available and enabled
            if self.enable_tool_calling and self.registered_tools:
                logger.debug(f"Configuring tools: {len(self.registered_tools)} tools available")
                tools = self._build_tools_config()
                if tools:
                    logger.debug(f"Built tools config with {len(tools)} tools")
                    generation_config.tools = tools
                    
                    # Add automatic function calling config
                    if self.automatic_function_calling:
                        logger.debug("Adding automatic function calling config")
                        auto_config = self._build_automatic_function_calling_config()
                        if auto_config:
                            generation_config.automatic_function_calling = auto_config
                            logger.debug("Automatic function calling config added")
                        else:
                            logger.warning("Failed to build automatic function calling config")
                else:
                    logger.warning("No tools were built from registered tools")
            else:
                logger.debug("Tool calling disabled or no tools registered")

            # Generate response
            logger.debug(f"Calling Gemini API with {len(contents)} content items and {len(self.registered_tools)} tools")
            logger.debug(f"Model: {self.model_name}")
            logger.debug(f"System instruction starts with: {self.system_instruction[:100]}...")
            
            response = self.client.models.generate_content(
                model=self.model_name, contents=contents, config=generation_config
            )

            # Debug response object
            logger.debug(f"Response object type: {type(response)}")
            logger.debug(f"Response object: {response}")
            
            if response is None:
                logger.error("Gemini returned None response")
                return "I apologize, but I received an empty response from the AI service. Please try again."
            
            # Check if response has text attribute
            if hasattr(response, 'text'):
                if response.text:
                    logger.debug(f"Gemini response received: {len(response.text)} characters")
                    return response.text
                else:
                    logger.warning("Gemini returned empty text response")
                    return "I apologize, but I couldn't generate a response. Please try again."
            else:
                logger.error(f"Response object has no 'text' attribute. Available attributes: {dir(response)}")
                return "I apologize, but I received an unexpected response format. Please try again."

        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}", exc_info=True)
            return (
                f"Sorry, I encountered an error while processing your request: {str(e)}"
            )

    def is_available(self) -> bool:
        """
        Check if the Gemini provider is available.

        Returns:
            True if the provider is initialized and ready, False otherwise
        """
        return self.is_initialized and self.client is not None

    def validate_config(self) -> bool:
        """
        Validate the Gemini provider configuration.

        Returns:
            True if configuration is valid, False otherwise
        """
        # Check for required API key
        api_key = self.config.get("api_key") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("Gemini API key is required")
            return False

        # Validate temperature range
        temperature = self.config.get("temperature", 0.7)
        if not (0.0 <= temperature <= 1.0):
            logger.error("Temperature must be between 0.0 and 1.0")
            return False

        # Validate top_p range
        top_p = self.config.get("top_p", 0.95)
        if not (0.0 <= top_p <= 1.0):
            logger.error("top_p must be between 0.0 and 1.0")
            return False

        # Validate top_k
        top_k = self.config.get("top_k", 40)
        if top_k <= 0:
            logger.error("top_k must be positive")
            return False

        # Validate max_output_tokens
        max_output_tokens = self.config.get("max_output_tokens", 2048)
        if max_output_tokens <= 0:
            logger.error("max_output_tokens must be positive")
            return False

        # Validate tool calling config
        max_tool_calls = self.config.get("max_tool_calls", 5)
        if max_tool_calls <= 0:
            logger.error("max_tool_calls must be positive")
            return False

        return True

    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get detailed information about the Gemini provider.

        Returns:
            Dictionary containing provider information
        """
        info = super().get_provider_info()
        info.update(
            {
                "model_name": self.model_name,
                "max_output_tokens": self.max_output_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "has_api_key": bool(
                    self.config.get("api_key") or os.getenv("GOOGLE_API_KEY")
                ),
                "sdk_version": self._get_sdk_version(),
                "enable_tool_calling": self.enable_tool_calling,
                "automatic_function_calling": self.automatic_function_calling,
                "max_tool_calls": self.max_tool_calls,
            }
        )
        return info

    def _get_sdk_version(self) -> str:
        """Get the Google Gen AI SDK version."""
        try:
            import google.genai

            return getattr(google.genai, "__version__", "unknown")
        except ImportError:
            return "not installed"

    def cleanup(self):
        """Clean up Gemini provider resources."""
        super().cleanup()
        self.client = None

    def update_system_instruction(self, new_instruction: str) -> bool:
        """
        Update the system instruction.
        
        Args:
            new_instruction: New system instruction
            
        Returns:
            True if successful
        """
        try:
            self.system_instruction = new_instruction
            logger.info(f"Updated system instruction for {self.provider_name}")
            logger.debug(f"New system instruction: {new_instruction[:200]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to update system instruction: {e}")
            return False
    
    def get_system_instruction(self) -> str:
        """
        Get the current system instruction.
        
        Returns:
            Current system instruction
        """
        return self.system_instruction

    def test_system_instruction(self) -> str:
        """
        Test the system instruction with a simple prompt.
        
        Returns:
            Test response or error message
        """
        if not self.is_available():
            return "Provider not available - check API key and initialization"
        
        try:
            test_message = "What is your name and what are you supposed to do?"
            logger.info("Testing system instruction with identity question")
            
            response = self.generate_response(test_message)
            
            # Check if response shows Jeeves persona
            if "Jeeves" in response or "jeeves" in response.lower():
                logger.info("✅ System instruction test passed - Jeeves persona detected")
                return f"System instruction working: {response}"
            else:
                logger.warning("❌ System instruction test failed - no Jeeves persona detected")
                return f"System instruction may not be working: {response}"
                
        except Exception as e:
            logger.error(f"System instruction test failed: {e}")
            return f"Test failed: {str(e)}"

