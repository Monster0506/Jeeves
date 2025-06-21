# Tool Calling Guide for Jeeves AI Assistant

This guide explains how to use the advanced tool calling functionality in Jeeves, which allows the AI to execute custom functions and tools during conversations.

## Overview

Tool calling enables Jeeves to:
- Execute custom Python functions
- Access external APIs and services
- Perform file operations
- Retrieve real-time information
- Automate tasks and workflows
- Chain multiple tools together
- Handle complex multi-step processes

## Architecture

### Base Provider Interface
The `BaseAIProvider` class includes comprehensive tool calling capabilities:
- `register_tool(name: str, function: Callable, description: str = None) -> bool` - Register a function as a callable tool
- `unregister_tool(name: str) -> bool` - Remove a tool
- `execute_tool(name: str, args: Dict[str, Any]) -> Any` - Execute a tool with arguments
- `get_registered_tools() -> Dict[str, Callable]` - Get all registered tools
- `set_tool_config(config: Dict[str, Any]) -> None` - Configure tool behavior
- `get_tool_config() -> Dict[str, Any]` - Get current tool configuration

### Gemini Provider Implementation
The `GeminiProvider` extends the base interface with:
- Automatic function calling using Google's Gemini API
- Function declaration generation from Python signatures
- Tool response handling and conversation continuation
- Configurable tool calling behavior
- Support for complex parameter types and validation

### Provider Manager Integration
The `AIProviderManager` provides:
- Centralized tool registration across all providers
- Automatic tool propagation to active providers
- Tool execution through the manager interface
- Parameter filtering and validation
- Error handling and logging

## Quick Start

### 1. Basic Tool Registration

```python
from src.core.ai_provider_manager import AIProviderManager

# Create provider manager
manager = AIProviderManager()
manager.initialize()

# Define a simple tool
def get_current_time() -> str:
    """Get the current time and date."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Register the tool
manager.register_tool("get_current_time", get_current_time)

# Use in conversation
response = manager.generate_response("What time is it?")
print(response)  # Jeeves will call get_current_time() and respond with the result
```

### 2. Tools with Parameters

```python
def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers."""
    return a + b

def get_weather(location: str) -> str:
    """Get weather information for a location."""
    # Mock implementation - replace with real API call
    weather_data = {
        "New York": "Sunny, 72°F",
        "London": "Rainy, 55°F",
        "Tokyo": "Cloudy, 68°F"
    }
    return weather_data.get(location, f"Weather data not available for {location}")

# Register tools
manager.register_tool("calculate_sum", calculate_sum)
manager.register_tool("get_weather", get_weather)

# Test complex requests
response = manager.generate_response("What's 15 + 27?")
print(response)  # Jeeves will calculate and respond

response = manager.generate_response("What's the weather in Tokyo?")
print(response)  # Jeeves will get weather data and respond
```

### 3. Advanced Tool Usage

```python
def log_thought(thought: str) -> str:
    """Log a thought for internal planning."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Jeeves thought: {thought}")
    return f"Thought logged: {thought}"

def search_files(query: str, directory: str = ".") -> str:
    """Search for files matching the query."""
    import os
    
    results = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if query.lower() in file.lower():
                results.append(os.path.join(root, file))
    
    if results:
        return f"Found {len(results)} files: {', '.join(sorted(results)[:5])}"
    else:
        return f"No files found matching '{query}'"

# Register advanced tools
manager.register_tool("log_thought", log_thought)
manager.register_tool("search_files", search_files)

# Test planning and file operations
response = manager.generate_response(
    "I need to find all Python files in my project. Can you help me plan this?"
)
print(response)  # Jeeves will use log_thought for planning, then search_files
```

## Configuration Options

### Gemini Provider Configuration

```python
config = {
    "model": "gemini-2.0-flash",
    "enable_tool_calling": True,           # Enable/disable tool calling
    "automatic_function_calling": True,    # Enable automatic execution
    "max_tool_calls": 5,                  # Maximum calls per response
    "temperature": 0.7,
    "max_output_tokens": 2048,
    "top_p": 0.95,
    "top_k": 40
}

provider = GeminiProvider(config)
```

### Tool Calling Modes

1. **Automatic Mode** (default): Tools are executed automatically by the AI
2. **Manual Mode**: Tools are declared but execution is controlled manually
3. **Disabled Mode**: Tool calling is completely disabled

## Best Practices

### 1. Function Design

```python
# Good: Clear parameters and return types
def process_data(input_data: str, format_type: str = "json") -> dict:
    """Process input data in the specified format."""
    # Implementation
    return {"result": "processed", "format": format_type}

# Avoid: Vague or complex parameters
def do_something(data, options=None, config={}):
    # Too vague - AI won't know how to call this
    pass
```

### 2. Error Handling

```python
def safe_api_call(endpoint: str) -> str:
    """Make a safe API call with error handling."""
    try:
        import requests
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"API call failed: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
```

### 3. Documentation

```python
def complex_tool(param1: str, param2: int, optional_param: bool = False) -> dict:
    """
    Perform a complex operation with multiple parameters.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter  
        optional_param: Optional boolean flag
        
    Returns:
        Dictionary containing operation results
        
    Raises:
        ValueError: If parameters are invalid
    """
    # Implementation
    pass
```

## Advanced Features

### 1. Tool Response Handling

The system automatically handles tool responses and continues conversations:

```python
def multi_step_process() -> str:
    """Example of a multi-step process."""
    # Step 1: Get data
    data = get_data()
    
    # Step 2: Process data
    processed = process_data(data)
    
    # Step 3: Save results
    save_results(processed)
    
    return "Process completed successfully"

# Jeeves can execute this and understand the flow
response = manager.generate_response("Run the multi-step process")
```

### 2. Context-Aware Tools

```python
def contextual_action(user_context: str, action: str) -> str:
    """Perform actions based on user context."""
    if "file" in user_context.lower() and "create" in action.lower():
        return create_file(user_context)
    elif "search" in action.lower():
        return search_content(user_context)
    else:
        return f"Unknown action: {action} for context: {user_context}"
```

### 3. Tool Chaining

Tools can be chained together automatically:

```python
def get_user_info(user_id: str) -> dict:
    """Get user information."""
    return {"id": user_id, "name": "John Doe", "email": "john@example.com"}

def send_notification(user_info: dict, message: str) -> str:
    """Send notification to user."""
    return f"Notification sent to {user_info['name']}: {message}"

# Jeeves can chain these together
response = manager.generate_response(
    "Send a welcome message to user 123"
)
# Jeeves will: get_user_info("123") -> send_notification(result, "Welcome!")
```

### 4. Parameter Filtering

The system automatically filters parameters to match function signatures:

```python
def my_tool(required_param: str, optional_param: int = 10) -> str:
    """A tool with required and optional parameters."""
    return f"Processed {required_param} with {optional_param}"

# Even if extra parameters are passed, only valid ones are used
result = manager.execute_tool("my_tool", {
    "required_param": "test",
    "optional_param": 20,
    "extra_param": "ignored"  # This will be filtered out
})
```

## Testing Tools

### Manual Testing

```python
# Test tool execution directly
result = manager.execute_tool("calculate_sum", {"a": 10, "b": 20})
print(result)  # 30

# Test with invalid parameters
try:
    result = manager.execute_tool("calculate_sum", {"a": "invalid", "b": 20})
except Exception as e:
    print(f"Error: {e}")
```

### Integration Testing

```python
# Test full conversation flow
test_messages = [
    "What time is it?",
    "Calculate 15 + 27",
    "What's the weather in New York?",
    "Find all Python files in the current directory"
]

for message in test_messages:
    response = manager.generate_response(message)
    print(f"User: {message}")
    print(f"Jeeves: {response}")
    print("-" * 40)
```

### Comprehensive Test Suite

Jeeves includes a comprehensive test suite for tool calling:

```bash
# Run all tool calling tests
uv run pytest tests/test_tool_calling.py -v

# Run specific tool calling test categories
uv run pytest tests/test_tool_calling.py::TestToolCallingImplementationExamples -v

# Run with coverage
uv run pytest tests/test_tool_calling.py --cov=src.core.ai_providers --cov-report=term-missing
```

## Troubleshooting

### Common Issues

1. **Tool Not Found**
   ```
   KeyError: Tool 'my_tool' is not registered
   ```
   Solution: Ensure the tool is registered before use

2. **Parameter Mismatch**
   ```
   TypeError: missing required argument 'param_name'
   ```
   Solution: Check function signature and parameter names

3. **API Errors**
   ```
   Exception: API call failed
   ```
   Solution: Add proper error handling in tool functions

4. **Mock Object Errors**
   ```
   TypeError: object of type 'Mock' has no len()
   ```
   Solution: Ensure proper mocking in tests

### Debug Mode

Enable debug logging to see tool execution details:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Tool executions will be logged
manager.generate_response("Test message")
```

### Test Debugging

```bash
# Run specific test with debug output
uv run pytest tests/test_tool_calling.py::TestToolCallingImplementationExamples::test_search_files_tool -v -s

# Run with detailed error information
uv run pytest tests/test_tool_calling.py --tb=long
```

## Security Considerations

1. **Input Validation**: Always validate tool inputs
2. **Sandboxing**: Restrict file system access to safe directories
3. **Rate Limiting**: Implement rate limits for API calls
4. **Error Handling**: Don't expose sensitive information in errors
5. **Parameter Filtering**: The system automatically filters invalid parameters

## Implementation Examples

The test suite includes practical implementation examples:

- **Logging Tools**: Side-effect tools for internal planning
- **File Operations**: Search and manipulate files safely
- **Tool Chaining**: Multi-step processes and workflows
- **Context-Aware Tools**: Logic based on conversation context
- **Error Handling**: Robust error handling and validation

## Future Enhancements

- Tool permission system
- Tool usage analytics
- Dynamic tool loading
- Tool composition and workflows
- Integration with external tool registries
- Advanced parameter validation
- Tool versioning and updates

## Examples

See the comprehensive test suite for complete working examples:
- `tests/test_tool_calling.py` - Core tool calling functionality
- `tests/test_tool_calling_functionality.py` - Additional tool tests
- `tests/test_ai_providers.py` - Provider-specific tool tests

## API Reference

### BaseAIProvider Methods

- `register_tool(name: str, function: Callable, description: str = None) -> bool`
- `unregister_tool(name: str) -> bool`
- `execute_tool(name: str, args: Dict[str, Any]) -> Any`
- `get_registered_tools() -> Dict[str, Callable]`
- `set_tool_config(config: Dict[str, Any]) -> None`
- `get_tool_config() -> Dict[str, Any]`

### AIProviderManager Methods

- `register_tool(name: str, function: Callable, description: str = None) -> bool`
- `unregister_tool(name: str) -> bool`
- `execute_tool(name: str, args: Dict[str, Any]) -> Any`
- `get_registered_tools() -> Dict[str, Callable]`
- `initialize() -> bool`
- `generate_response(user_message: str, context: List[Dict] = None) -> str`

### GeminiProvider Configuration

- `enable_tool_calling: bool` - Enable/disable tool calling
- `automatic_function_calling: bool` - Enable automatic execution
- `max_tool_calls: int` - Maximum tool calls per response
- `model: str` - Gemini model to use
- `temperature: float` - Response creativity (0.0-1.0)
- `max_output_tokens: int` - Maximum response length
- `top_p: float` - Nucleus sampling parameter
- `top_k: int` - Top-k sampling parameter 