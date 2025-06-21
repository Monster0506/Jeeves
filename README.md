# Jeeves - AI Assistant

A modern, modular AI chat assistant built with Python and CustomTkinter, featuring **Google Gemini AI integration** and **advanced tool calling capabilities**.

## Features

- 🎨 **Modern Dark UI** - Beautiful CustomTkinter interface with dark mode
- ⌨️ **Global Hotkey** - Press `Alt+Space` from anywhere to open the chat
- 💬 **Thread Management** - Organize conversations into different threads
- 🤖 **Real AI Integration** - Powered by Google Gemini AI with fallback support
- 🔧 **Tool Calling** - Execute custom functions and tools during conversations
- 🔄 **Modular AI Providers** - Easy to switch between different AI backends
- 📱 **Responsive Design** - Clean, modern interface that adapts to your system
- 🧪 **Comprehensive Testing** - Full test suite with 220+ tests and 95%+ coverage

## AI Integration & Tool Calling

Jeeves now supports **Google Gemini AI** with advanced **tool calling capabilities**:

### Setting up Gemini AI

1. **Get a Gemini API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the key to your clipboard

2. **Set Environment Variable**:
   ```bash
   # On Windows (PowerShell)
   $env:GOOGLE_API_KEY="your-api-key-here"
   
   # On macOS/Linux
   export GOOGLE_API_KEY="your-api-key-here"
   ```

3. **Test the Integration**:
   ```bash
   python test_gemini.py
   ```

### Tool Calling Capabilities

Jeeves can execute custom Python functions and tools during conversations:

```python
from src.core.ai_provider_manager import AIProviderManager

# Create provider manager
manager = AIProviderManager()
manager.initialize()

# Define and register tools
def get_current_time() -> str:
    """Get the current time and date."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers."""
    return a + b

# Register tools
manager.register_tool("get_current_time", get_current_time)
manager.register_tool("calculate_sum", calculate_sum)

# Use in conversation
response = manager.generate_response("What time is it and what's 15 + 27?")
# Jeeves will automatically call both tools and provide results
```

**Tool Calling Features:**
- ✅ **Automatic Execution** - Tools run automatically based on conversation context
- ✅ **Parameter Validation** - Type-safe parameter handling with error checking
- ✅ **Error Handling** - Graceful handling of tool execution errors
- ✅ **Tool Chaining** - Multiple tools can be called in sequence
- ✅ **Context Awareness** - Tools can access conversation context
- ✅ **File Operations** - Search, read, and manipulate files
- ✅ **API Integration** - Make external API calls safely
- ✅ **Custom Logic** - Execute any Python function with proper validation

For detailed tool calling documentation, see [TOOL_CALLING_GUIDE.md](TOOL_CALLING_GUIDE.md).

### AI Providers

Jeeves uses a modular AI provider system:

- **Gemini Provider** (Primary): Google's Gemini AI with full tool calling support
- **Placeholder Provider** (Fallback): Simple keyword-based responses when AI is unavailable

The system automatically selects the best available provider and falls back gracefully if needed.

## Project Structure

```
Jeeves/
├── src/                    # Main source code
│   ├── config/            # Configuration and settings
│   │   ├── __init__.py
│   │   └── settings.py    # App settings, colors, icons, AI config
│   ├── core/              # Core business logic
│   │   ├── __init__.py
│   │   ├── ai_engine.py   # AI response generation
│   │   ├── ai_providers/  # Modular AI provider system
│   │   │   ├── __init__.py
│   │   │   ├── base_provider.py      # Base provider with tool calling
│   │   │   ├── gemini_provider.py    # Gemini AI with function calling
│   │   │   └── placeholder_provider.py
│   │   ├── ai_provider_manager.py    # Provider and tool management
│   │   ├── chat_manager.py
│   │   └── database.py
│   ├── gui/               # User interface components
│   │   ├── __init__.py
│   │   ├── app.py         # Main application class
│   │   └── components.py  # Reusable UI components
│   ├── utils/             # Utility functions
│   │   ├── __init__.py
│   │   └── dialogs.py     # Dialog utilities
│   ├── __init__.py
│   └── main.py           # Application entry point
├── tests/                 # Comprehensive test suite
│   ├── test_ai_providers.py           # AI provider unit tests
│   ├── test_ai_provider_manager.py    # Provider manager tests
│   ├── test_tool_calling.py           # Tool calling functionality tests
│   ├── test_tool_calling_functionality.py  # Additional tool tests
│   ├── test_integration.py            # Integration tests
│   ├── test_api.py                    # API integration tests
│   └── README.md                      # Testing documentation
├── main.py               # Global hotkey launcher
├── test_gemini.py        # Gemini integration test script
├── TOOL_CALLING_GUIDE.md # Comprehensive tool calling documentation
├── pyproject.toml        # Project configuration
└── README.md            # This file
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Jeeves
   ```

2. **Install dependencies**
   ```bash
   uv install
   ```

3. **Set up Gemini AI** (Optional but recommended)
   ```bash
   # Set your API key
   export GOOGLE_API_KEY="your-api-key-here"
   
   # Test the integration
   python test_gemini.py
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## Usage

### Starting the App
- Run `python main.py` to start the global hotkey listener
- Press `Alt+Space` from anywhere to open the chat window
- Press `Ctrl+C` to exit the application

### Using the Chat
- **Send Messages**: Type in the input field and press Enter or click Send
- **AI Responses**: Get intelligent responses from Google Gemini AI
- **Tool Execution**: Ask Jeeves to perform tasks like calculations, file operations, or API calls
- **New Chat**: Click the "✨ New Chat" button to start a fresh conversation
- **Thread Management**: Use the sidebar to switch between different conversation threads
- **Toggle Sidebar**: Click the close button (✕) to hide the sidebar, then use the menu button (☰) to reopen it

### Example Tool Interactions
```
User: "What time is it?"
Jeeves: "The current time is 2024-01-15 14:30:25"

User: "Calculate 15 + 27"
Jeeves: "The sum of 15 and 27 is 42"

User: "Find all Python files in my project"
Jeeves: "I found 3 Python files: main.py, test_gemini.py, src/main.py"

User: "What's the weather in Tokyo?"
Jeeves: "The weather in Tokyo is Cloudy, 68°F"
```

### Supported Commands
- Ask for the **time** or **date**
- Request **calculations** and **mathematical operations**
- **File operations** like searching and reading files
- **API calls** to external services
- Say **hello** or **hi** for a greeting
- Ask about the **weather** (placeholder response)
- Ask for **help** to see available features
- Ask about the **model** being used
- **Any question** - Gemini AI will provide intelligent responses!

## Architecture

### Modular AI Design with Tool Calling
The application features a clean, modular AI architecture with advanced tool calling:

- **AI Provider Interface** (`src/core/ai_providers/base_provider.py`): Abstract base class with tool calling support
- **Gemini Provider** (`src/core/ai_providers/gemini_provider.py`): Google Gemini AI with function calling integration
- **Placeholder Provider** (`src/core/ai_providers/placeholder_provider.py`): Fallback responses with tool awareness
- **Provider Manager** (`src/core/ai_provider_manager.py`): Manages providers and centralized tool registration

### Key Components

#### AI Engine (`src/core/ai_engine.py`)
- Orchestrates AI providers
- Manages conversation context
- Handles provider switching
- Provides analytics and insights

#### Tool Calling System
- **Tool Registration**: Register custom Python functions as callable tools
- **Parameter Validation**: Type-safe parameter handling with error checking
- **Execution Engine**: Safe execution of tools with proper error handling
- **Response Integration**: Seamless integration of tool results into conversations

#### GUI Components (`src/gui/components.py`)
- **ChatDisplay**: Enhanced text display with message styling
- **Sidebar**: Thread management and navigation

#### Main App (`src/gui/app.py`)
- Orchestrates all components
- Handles user interactions
- Manages application state

## Development

### Adding New AI Providers

1. **Create Provider Class**: Extend `BaseAIProvider` in `src/core/ai_providers/`
2. **Implement Required Methods**: `initialize()`, `generate_response()`, `is_available()`
3. **Add Tool Calling Support**: Implement tool registration and execution methods
4. **Register Provider**: Add to `AIProviderManager._register_providers()`
5. **Test Integration**: Use the comprehensive test suite

### Adding New Tools

1. **Define Tool Function**: Create a Python function with clear parameters and return types
2. **Add Documentation**: Include docstrings explaining the tool's purpose
3. **Register Tool**: Use `manager.register_tool("tool_name", function)`
4. **Test Tool**: Add tests to the tool calling test suite

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all functions and classes
- Keep modules focused and single-purpose
- Write comprehensive tests for new features

## Dependencies

- **customtkinter**: Modern GUI framework
- **pynput**: Global keyboard listening
- **pillow**: Image processing (for future features)
- **google-genai**: Google Gemini AI integration
- **pytest**: Testing framework
- **pytest-cov**: Test coverage reporting

## Testing

Jeeves includes a comprehensive testing framework with **220+ tests** and **95%+ coverage**:

### 🧪 Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interaction between components  
- **API Tests**: Test actual external API calls (Gemini)
- **Tool Calling Tests**: Test function execution and tool management
- **Performance Tests**: Test response times and scalability

### 🚀 Running Tests

#### Quick Start
```bash
# Run all tests (220+ tests)
uv run pytest tests/ -v

# Run fast tests (unit + integration, no API calls)
uv run pytest tests/ -m "not api" -v

# Run tool calling tests specifically
uv run pytest tests/test_tool_calling.py -v
```

#### Advanced Testing
```bash
# Run with coverage report
uv run pytest tests/ --cov=src --cov-report=html

# Run specific test categories
uv run pytest tests/ -m unit -v
uv run pytest tests/ -m integration -v
uv run pytest tests/ -m api -v

# Run with detailed output
uv run pytest tests/ -v -s --tb=long
```

### 📊 Test Coverage

The testing framework provides comprehensive coverage:

- **Unit Tests**: 95%+ line coverage
- **Integration Tests**: 90%+ integration coverage  
- **API Tests**: 85%+ API functionality coverage
- **Tool Calling Tests**: 100% tool functionality coverage

### 🔧 Test Configuration

#### Environment Variables
- `GOOGLE_API_KEY` - Required for API tests
- `JEEVES_TEST_MODE` - Set to 'true' for test environment

#### Test Dependencies
All test dependencies are managed through `uv`:
```bash
uv sync --group test
```

### 📁 Test Structure
```
tests/
├── __init__.py                    # Test package initialization
├── conftest.py                    # Pytest configuration and shared fixtures
├── test_ai_providers.py           # Unit tests for AI providers
├── test_ai_provider_manager.py    # Unit tests for provider manager
├── test_tool_calling.py           # Tool calling functionality tests
├── test_tool_calling_functionality.py  # Additional tool calling tests
├── test_integration.py            # Integration tests
├── test_api.py                    # API tests (external service calls)
└── README.md                      # Detailed testing documentation
```

### 🛠️ Development Workflow

When adding new features:
1. Write unit tests for new functionality
2. Add integration tests for component interactions
3. Add tool calling tests if new tools are involved
4. Add API tests if external services are involved
5. Ensure all tests pass before submitting PR

For detailed testing documentation, see [tests/README.md](tests/README.md).

## Future Enhancements

- [x] Real AI integration (Google Gemini)
- [x] Modular AI provider system
- [x] Advanced tool calling capabilities
- [x] Comprehensive testing framework
- [ ] OpenAI/Anthropic integration
- [x] Persistent chat history
- [ ] File attachments
- [ ] Voice input/output
- [ ] Custom themes
- [ ] Plugin system
- [ ] Multi-language support
- [ ] Tool marketplace
- [ ] Advanced tool workflows

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add comprehensive tests
5. Ensure all existing tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Available Tools

Jeeves comes with **11 powerful built-in tools** that enable advanced functionality and automation. These tools are automatically available in conversations and can be called by the AI to perform various tasks.

### 🗂️ **Chat Management Tools**

#### `rename_chat_thread`
Rename chat threads for better organization.
```python
# Rename current thread
response = manager.generate_response("Rename this thread to 'Project Planning'")

# Rename specific thread
response = manager.generate_response("Rename thread 5 to 'Bug Fixes'")
```

#### `search_chat_history`
Search through conversation history across all threads.
```python
# Search all threads
response = manager.generate_response("Search for 'API integration' in chat history")

# Search specific thread with limit
response = manager.generate_response("Find mentions of 'database' in thread 3, limit to 5 results")
```

#### `get_available_threads`
List all chat threads with message counts and activity info.
```python
response = manager.generate_response("Show me all my chat threads")
```

#### `get_current_thread_info`
Get detailed information about the current active thread.
```python
response = manager.generate_response("What thread am I currently in?")
```

#### `export_current_conversation`
Export the current conversation to JSON or text format.
```python
# Export as JSON
response = manager.generate_response("Export this conversation as JSON")

# Export as text
response = manager.generate_response("Save this conversation as a text file")
```

#### `get_conversation_summary`
Get a summary of the current conversation with statistics.
```python
response = manager.generate_response("Summarize this conversation")
```

### 📝 **File Management Tools**

#### `note_manager`
Manage personal notes in the `~/.jeeves/notes/` directory.
```python
# Create a new note
response = manager.generate_response("Create a note called 'meeting_notes' with content 'Discuss API design'")

# Read a note
response = manager.generate_response("Read my meeting_notes")

# Append to existing note
response = manager.generate_response("Add 'Follow up on database migration' to meeting_notes")

# List all notes
response = manager.generate_response("Show me all my notes")

# Delete a note
response = manager.generate_response("Delete the meeting_notes file")
```

#### `todo_list_manager`
Manage a centralized todo list in `~/.jeeves/todo.md`.
```python
# Add a new task
response = manager.generate_response("Add 'Review pull request #123' to my todo list")

# List all tasks
response = manager.generate_response("Show me my todo list")

# Complete a task
response = manager.generate_response("Mark task 3 as complete")

# Delete a task
response = manager.generate_response("Remove task 2 from my todo list")

# Clear all tasks
response = manager.generate_response("Clear my entire todo list")
```

#### `content_searcher`
Search for files and content within the `~/.jeeves/` sandbox.
```python
# Search file contents
response = manager.generate_response("Search for 'database' in all my files")

# Search by filename
response = manager.generate_response("Find files with 'config' in the name")

# Search both content and filenames
response = manager.generate_response("Search for 'API' in both content and filenames")

# Search with file pattern
response = manager.generate_response("Search for 'password' in all .md files")

# Non-recursive search
response = manager.generate_response("Search for 'test' only in the current directory")
```

### 🧠 **Memory & Logging Tools**

#### `persistent_memory_manager`
Manage Jeeves's long-term memory in `~/.jeeves/MEMORY.md`.
```python
# Add a memory entry
response = manager.generate_response("Remember that I prefer dark mode interfaces")

# List all memories
response = manager.generate_response("Show me all my memories")

# Remove a memory entry
response = manager.generate_response("Remove memory entry 5")

# Clear all memories
response = manager.generate_response("Clear all my memories")
```

#### `scratchpad_logger`
Log internal thoughts to session-specific scratchpad files.
```python
# Log thoughts for current session
response = manager.generate_response("Log this thought: 'User seems interested in API documentation'")

# Log with specific session name
response = manager.generate_response("Log to session 'project_planning': 'Need to research authentication methods'")
```

### 🔧 **Tool Usage Examples**

#### Complex Workflows
```python
# Multi-step workflow
response = manager.generate_response("""
1. Create a note called 'project_ideas'
2. Add 'Build a task management app' to my todo list
3. Remember that I'm working on productivity tools
4. Search for any existing notes about task management
""")

# Research and documentation
response = manager.generate_response("""
1. Search my notes for 'API documentation'
2. If found, read the content
3. If not found, create a new note with 'Need to document API endpoints'
4. Add 'Write API documentation' to my todo list
""")
```

#### Context-Aware Interactions
```python
# Contextual responses
response = manager.generate_response("Based on our conversation, what should I remember about your preferences?")

# Historical analysis
response = manager.generate_response("Search our chat history for patterns in my coding questions")
```

### 🛡️ **Security & Safety**

All tools operate within a sandboxed environment (`~/.jeeves/`) and include:
- **Input validation** for all parameters
- **Error handling** with graceful fallbacks
- **File operation safety** with soft deletes
- **Parameter filtering** to prevent injection attacks
- **Logging** for audit trails

### 📊 **Tool Statistics**

- **Total Tools**: 11
- **Chat Management**: 6 tools
- **File Management**: 3 tools  
- **Memory & Logging**: 2 tools
- **Categories**: 3 main categories
- **Safety Features**: 5+ security measures

For detailed tool calling documentation and advanced usage examples, see [TOOL_CALLING_GUIDE.md](TOOL_CALLING_GUIDE.md).
