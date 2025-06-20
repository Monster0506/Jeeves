# Jeeves - AI Assistant

A modern, modular AI chat assistant built with Python and CustomTkinter, featuring **Google Gemini AI integration**.

## Features

- 🎨 **Modern Dark UI** - Beautiful CustomTkinter interface with dark mode
- ⌨️ **Global Hotkey** - Press `Alt+Space` from anywhere to open the chat
- 💬 **Thread Management** - Organize conversations into different threads
- 🤖 **Real AI Integration** - Powered by Google Gemini AI with fallback support
- 🔄 **Modular AI Providers** - Easy to switch between different AI backends
- 📱 **Responsive Design** - Clean, modern interface that adapts to your system

## AI Integration

Jeeves now supports **Google Gemini AI** for intelligent, contextual responses:

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

### AI Providers

Jeeves uses a modular AI provider system:

- **Gemini Provider** (Primary): Google's Gemini AI for intelligent responses
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
│   │   ├── ai_engine.py   # AI response generation (refactored)
│   │   ├── ai_providers/  # Modular AI provider system
│   │   │   ├── __init__.py
│   │   │   ├── base_provider.py
│   │   │   ├── gemini_provider.py
│   │   │   └── placeholder_provider.py
│   │   ├── ai_provider_manager.py
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
├── main.py               # Global hotkey launcher
├── test_gemini.py        # Gemini integration test script
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
- **New Chat**: Click the "✨ New Chat" button to start a fresh conversation
- **Thread Management**: Use the sidebar to switch between different conversation threads
- **Toggle Sidebar**: Click the close button (✕) to hide the sidebar, then use the menu button (☰) to reopen it

### Supported Commands
- Ask for the **time** or **date**
- Say **hello** or **hi** for a greeting
- Ask about the **weather** (placeholder response)
- Ask for **help** to see available features
- Ask about the **model** being used
- **Any question** - Gemini AI will provide intelligent responses!

## Architecture

### Modular AI Design
The application now features a clean, modular AI architecture:

- **AI Provider Interface** (`src/core/ai_providers/base_provider.py`): Abstract base class for all AI backends
- **Gemini Provider** (`src/core/ai_providers/gemini_provider.py`): Google Gemini AI integration
- **Placeholder Provider** (`src/core/ai_providers/placeholder_provider.py`): Fallback responses
- **Provider Manager** (`src/core/ai_provider_manager.py`): Manages multiple providers and switching

### Key Components

#### AI Engine (`src/core/ai_engine.py`)
- Orchestrates AI providers
- Manages conversation context
- Handles provider switching
- Provides analytics and insights

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
3. **Register Provider**: Add to `AIProviderManager._register_providers()`
4. **Test Integration**: Use the test script pattern

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all functions and classes
- Keep modules focused and single-purpose

## Dependencies

- **customtkinter**: Modern GUI framework
- **pynput**: Global keyboard listening
- **pillow**: Image processing (for future features)
- **google-genai**: Google Gemini AI integration

## Future Enhancements

- [x] Real AI integration (Google Gemini)
- [x] Modular AI provider system
- [ ] OpenAI/Anthropic integration
- [ ] Persistent chat history
- [ ] File attachments
- [ ] Voice input/output
- [ ] Custom themes
- [ ] Plugin system
- [ ] Multi-language support

## Testing

Jeeves includes a comprehensive testing framework to ensure code quality and reliability.

### 🧪 Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interaction between components  
- **API Tests**: Test actual external API calls (Gemini)
- **Performance Tests**: Test response times and scalability

### 🚀 Running Tests

#### Quick Start
```bash
# Run fast tests (unit + integration, no API calls)
python run_tests.py --type fast

# Run all tests
python run_tests.py --type all

# Run specific test categories
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type api
```

#### Advanced Testing
```bash
# Run with coverage report
python run_tests.py --type coverage

# Run code linting
python run_tests.py --type lint

# Run type checking
python run_tests.py --type types

# Run security checks
python run_tests.py --type security

# Run performance tests
python run_tests.py --type performance
```

#### Direct Pytest Commands
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ai_providers.py -v

# Run tests with specific marker
pytest tests/ -m unit -v
pytest tests/ -m "not slow" -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### 📊 Test Coverage

The testing framework provides comprehensive coverage:

- **Unit Tests**: 90%+ line coverage target
- **Integration Tests**: 80%+ integration coverage target  
- **API Tests**: 70%+ API functionality coverage target

### 🔧 Test Configuration

#### Environment Variables
- `GOOGLE_API_KEY` - Required for API tests
- `JEEVES_TEST_MODE` - Set to 'true' for test environment

#### Test Dependencies
Install test dependencies:
```bash
pip install -e ".[test]"
```

### 📁 Test Structure
```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and shared fixtures
├── test_ai_providers.py     # Unit tests for AI providers
├── test_ai_provider_manager.py  # Unit tests for provider manager
├── test_integration.py      # Integration tests
├── test_api.py              # API tests (external service calls)
└── README.md                # Detailed testing documentation
```

### 🛠️ Development Workflow

When adding new features:
1. Write unit tests for new functionality
2. Add integration tests for component interactions
3. Add API tests if external services are involved
4. Ensure all tests pass before submitting PR

For detailed testing documentation, see [tests/README.md](tests/README.md).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
