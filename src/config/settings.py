"""
Application settings and configuration constants.
"""

# Icon definitions
ICONS = {
    'chat': '💬',
    'send': '➤',
    'close': '✕',
    'menu': '☰',
    'new': '✨',
    'project': '📁',
    'code': '🔍',
    'question': '❓',
    'notes': '📝',
    'idea': '💡',
    'support': '🛠️',
    'planning': '📋',
    'docs': '📚',
    'target': '🎯',
    'rocket': '🚀',
    'time': '⏰',
    'date': '📅',
    'brain': '🧠',
    'weather': '🌤️',
    'help': '💡',
    'thinking': '🤔',
    'robot': '🤖',
    'wave': '👋'
}

# Color schemes
COLORS = {
    'light': {
        'bg_primary': 'gray90',
        'bg_secondary': 'gray85',
        'bg_sidebar': 'gray85',
        'bg_header': 'gray80',
        'bg_chat': 'gray92',
        'text_primary': 'gray10',
        'text_secondary': 'gray30',
        'accent': '#3b82f6',
        'accent_alt': '#1d4ed8',
        'accent_blue': '#3b82f6',
        'accent_green': '#10b981',
        'accent_purple': '#8b5cf6',
        'bubble_user': '#3b82f6',
        'bubble_ai': 'gray85',
    },
    'dark': {
        'bg_primary': 'gray13',
        'bg_secondary': 'gray17',
        'bg_sidebar': 'gray17',
        'bg_header': 'gray15',
        'bg_chat': 'gray11',
        'text_primary': 'gray90',
        'text_secondary': 'gray70',
        'accent': '#3b82f6',
        'accent_alt': '#60a5fa',
        'accent_blue': '#3b82f6',
        'accent_green': '#10b981',
        'accent_purple': '#8b5cf6',
        'bubble_user': '#3b82f6',
        'bubble_ai': 'gray17',
    }
}

# App settings
APP_SETTINGS = {
    'title': 'Jeeves - AI Assistant',
    'default_width': 1200,
    'default_height': 800,
    'min_width': 800,
    'min_height': 600,
    'sidebar_width': 300,
    'font_family': 'Fira Code',
    'font_sizes': {
        'small': 11,
        'normal': 14,
        'medium': 16,
        'large': 18,
        'xlarge': 20
    }
}

# AI Provider settings
AI_PROVIDER_SETTINGS = {
    'default_provider': 'gemini',
    'providers': {
        'gemini': {
            'enabled': True,
            'model': 'gemini-2.0-flash',
            'max_output_tokens': 2048,
            'temperature': 0.7,
            'top_p': 0.95,
            'top_k': 40,
            'system_instruction': None,  # Use default
            'api_key_env_var': 'GOOGLE_API_KEY'
        },
        'placeholder': {
            'enabled': True,
            'fallback': True
        }
    },
    'provider_order': ['gemini', 'placeholder']
}

# Thread data for sidebar
DEFAULT_THREADS = [
    ('project', 'Project Discussion'),
    ('code', 'Code Review'),
    ('question', 'General Questions'),
    ('notes', 'Meeting Notes'),
    ('idea', 'Ideas & Brainstorming'),
    ('support', 'Technical Support'),
    ('planning', 'Planning Session'),
    ('docs', 'Documentation Help'),
    ('target', 'Goal Setting'),
    ('rocket', 'Feature Planning')
] 