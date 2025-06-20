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
        'bg_primary': '#F5F6FA',
        'bg_secondary': '#FFFFFF',
        'bg_sidebar': '#F0F1F5',
        'bg_header': '#FFFFFF',
        'bg_chat': '#F5F6FA',
        'bubble_user': '#E3F2FD',
        'bubble_ai': '#E8EAF6',
        'bubble_border': '#E0E0E0',
        'text_primary': '#181A20',
        'text_secondary': '#555A64',
        'accent': '#3B82F6',
        'accent_alt': '#6366F1',
        'danger': '#EF4444',
    },
    'dark': {
        'bg_primary': '#181A20',
        'bg_secondary': '#23272F',
        'bg_sidebar': '#20232A',
        'bg_header': '#23272F',
        'bg_chat': '#181A20',
        'bubble_user': '#1E293B',
        'bubble_ai': '#23272F',
        'bubble_border': '#22242B',
        'text_primary': '#F5F6FA',
        'text_secondary': '#A0A4AE',
        'accent': '#3B82F6',
        'accent_alt': '#6366F1',
        'danger': '#EF4444',
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
    'font_family': 'Inter, Segoe UI, Fira Code, Arial, sans-serif',
    'font_sizes': {
        'small': 10,
        'normal': 13,
        'medium': 15,
        'large': 18,
        'xlarge': 22
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