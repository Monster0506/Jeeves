"""
Application settings and configuration constants.
"""

from typing import TypedDict

ICONS = {
    "chat": "💬",
    "send": "➤",
    "close": "✕",
    "menu": "☰",
    "new": "✨",
    "project": "📁",
    "code": "🔍",
    "question": "❓",
    "notes": "📝",
    "idea": "💡",
    "support": "🛠️",
    "planning": "📋",
    "docs": "📚",
    "target": "🎯",
    "rocket": "🚀",
    "time": "⏰",
    "date": "📅",
    "brain": "🧠",
    "weather": "🌤️",
    "help": "💡",
    "thinking": "🤔",
    "robot": "🤖",
    "wave": "👋",
}


class ColorsTheme(TypedDict):
    accent_light: str
    accent_primary: str
    accent_secondary: str
    accent_tertiary: str
    active_dark: str
    active_light: str
    bg_card: str
    bg_chat: str
    bg_header: str
    bg_input: str
    bg_overlay: str
    bg_primary: str
    bg_secondary: str
    bg_sidebar: str
    bg_tertiary: str
    border_divider: str
    border_focus: str
    border_primary: str
    border_secondary: str
    bubble_ai: str
    bubble_ai_hover: str
    bubble_system: str
    bubble_user: str
    bubble_user_hover: str
    button_danger: str
    button_danger_hover: str
    button_primary: str
    button_primary_active: str
    button_primary_hover: str
    button_secondary: str
    button_secondary_active: str
    button_secondary_hover: str
    button_success: str
    button_success_hover: str
    button_warning: str
    button_warning_hover: str
    disabled: str
    disabled_bg: str
    error: str
    error_hover: str
    highlight: str
    hover_dark: str
    hover_light: str
    info: str
    info_hover: str
    link: str
    link_hover: str
    selection: str
    shadow_dark: str
    shadow_light: str
    shadow_medium: str
    success: str
    success_hover: str
    text_inverse: str
    text_muted: str
    text_primary: str
    text_secondary: str
    text_tertiary: str
    thread_code: str
    thread_creative: str
    thread_docs: str
    thread_general: str
    thread_planning: str
    thread_support: str
    warning: str
    warning_hover: str


class ColorsType(TypedDict):
    dark: ColorsTheme
    light: ColorsTheme


COLORS: ColorsType = {
    "dark": {
        # Background Colors
        "bg_primary": "#0f172a",  # Main app background
        "bg_secondary": "#1e293b",  # Cards, panels
        "bg_tertiary": "#334155",  # Elevated elements
        "bg_header": "#1e293b",  # Header background
        "bg_sidebar": "#1e293b",  # Sidebar background
        "bg_chat": "#0f172a",  # Chat area background
        "bg_input": "#334155",  # Input field background
        "bg_card": "#1e293b",  # Card backgrounds
        "bg_overlay": "#0f172a",  # Modal overlays
        # Text Colors
        "text_primary": "#f8fafc",  # Main text
        "text_secondary": "#94a3b8",  # Secondary text
        "text_tertiary": "#64748b",  # Disabled text
        "text_inverse": "#0f172a",  # Text on colored backgrounds
        "text_muted": "#64748b",  # Muted text
        # Border Colors
        "border_primary": "#334155",  # Main borders
        "border_secondary": "#475569",  # Subtle borders
        "border_focus": "#3b82f6",  # Focus borders
        "border_divider": "#334155",  # Dividers
        # Primary Accent Colors
        "accent_primary": "#3b82f6",  # Main accent
        "accent_secondary": "#1e40af",  # Secondary accent
        "accent_tertiary": "#60a5fa",  # Tertiary accent
        "accent_light": "#93c5fd",  # Light accent
        # Semantic Status Colors
        "success": "#059669",  # Success states
        "success_hover": "#10b981",  # Success hover
        "warning": "#d97706",  # Warning states
        "warning_hover": "#f59e0b",  # Warning hover
        "error": "#dc2626",  # Error states
        "error_hover": "#ef4444",  # Error hover
        "info": "#3b82f6",  # Info states
        "info_hover": "#60a5fa",  # Info hover
        # Thread Type Colors
        "thread_general": "#3b82f6",  # General conversations
        "thread_code": "#059669",  # Programming discussions
        "thread_planning": "#d97706",  # Project planning
        "thread_creative": "#7c3aed",  # Brainstorming, ideas
        "thread_support": "#dc2626",  # Technical issues
        "thread_docs": "#0891b2",  # Documentation, notes
        # Chat Bubble Colors
        "bubble_user": "#3b82f6",  # User message bubbles
        "bubble_user_hover": "#1e40af",  # User bubble hover
        "bubble_ai": "#1e293b",  # AI message bubbles
        "bubble_ai_hover": "#334155",  # AI bubble hover
        "bubble_system": "#334155",  # System message bubbles
        # Button Colors
        "button_primary": "#3b82f6",
        "button_primary_hover": "#60a5fa",
        "button_primary_active": "#1e40af",
        "button_secondary": "#334155",
        "button_secondary_hover": "#475569",
        "button_secondary_active": "#1e293b",
        "button_success": "#059669",
        "button_success_hover": "#10b981",
        "button_warning": "#d97706",
        "button_warning_hover": "#f59e0b",
        "button_danger": "#dc2626",
        "button_danger_hover": "#ef4444",
        # Interactive States
        "hover_light": "#334155",
        "hover_dark": "#475569",
        "active_light": "#1e293b",
        "active_dark": "#334155",
        "disabled": "#64748b",
        "disabled_bg": "#1e293b",
        # Shadow Colors (for reference, not used in CTk)
        "shadow_light": "#000000",
        "shadow_medium": "#000000",
        "shadow_dark": "#000000",
        # Special Colors
        "selection": "#3b82f6",  # Text selection
        "highlight": "#fef3c7",  # Search highlights
        "link": "#60a5fa",  # Links
        "link_hover": "#93c5fd",  # Link hover
    },
    "light": {
        # Background Colors
        "bg_primary": "#ffffff",  # Main app background
        "bg_secondary": "#f8fafc",  # Cards, panels
        "bg_tertiary": "#f1f5f9",  # Elevated elements
        "bg_header": "#f8fafc",  # Header background
        "bg_sidebar": "#f1f5f9",  # Sidebar background
        "bg_chat": "#ffffff",  # Chat area background
        "bg_input": "#f8fafc",  # Input field background
        "bg_card": "#ffffff",  # Card backgrounds
        "bg_overlay": "#000000",  # Modal overlays
        # Text Colors
        "text_primary": "#0f172a",  # Main text
        "text_secondary": "#475569",  # Secondary text
        "text_tertiary": "#64748b",  # Disabled text
        "text_inverse": "#ffffff",  # Text on colored backgrounds
        "text_muted": "#64748b",  # Muted text
        # Border Colors
        "border_primary": "#e2e8f0",  # Main borders
        "border_secondary": "#cbd5e1",  # Subtle borders
        "border_focus": "#3b82f6",  # Focus borders
        "border_divider": "#e2e8f0",  # Dividers
        # Primary Accent Colors
        "accent_primary": "#1e40af",  # Main accent
        "accent_secondary": "#3b82f6",  # Secondary accent
        "accent_tertiary": "#60a5fa",  # Tertiary accent
        "accent_light": "#93c5fd",  # Light accent
        # Semantic Status Colors
        "success": "#059669",  # Success states
        "success_hover": "#10b981",  # Success hover
        "warning": "#d97706",  # Warning states
        "warning_hover": "#f59e0b",  # Warning hover
        "error": "#dc2626",  # Error states
        "error_hover": "#ef4444",  # Error hover
        "info": "#1e40af",  # Info states
        "info_hover": "#3b82f6",  # Info hover
        # Thread Type Colors
        "thread_general": "#1e40af",  # General conversations
        "thread_code": "#059669",  # Programming discussions
        "thread_planning": "#d97706",  # Project planning
        "thread_creative": "#7c3aed",  # Brainstorming, ideas
        "thread_support": "#dc2626",  # Technical issues
        "thread_docs": "#0891b2",  # Documentation, notes
        # Chat Bubble Colors
        "bubble_user": "#1e40af",  # User message bubbles
        "bubble_user_hover": "#3b82f6",  # User bubble hover
        "bubble_ai": "#f1f5f9",  # AI message bubbles
        "bubble_ai_hover": "#e2e8f0",  # AI bubble hover
        "bubble_system": "#f8fafc",  # System message bubbles
        # Button Colors
        "button_primary": "#1e40af",
        "button_primary_hover": "#3b82f6",
        "button_primary_active": "#1e3a8a",
        "button_secondary": "#f1f5f9",
        "button_secondary_hover": "#e2e8f0",
        "button_secondary_active": "#cbd5e1",
        "button_success": "#059669",
        "button_success_hover": "#10b981",
        "button_warning": "#d97706",
        "button_warning_hover": "#f59e0b",
        "button_danger": "#dc2626",
        "button_danger_hover": "#ef4444",
        # Interactive States
        "hover_light": "#f8fafc",
        "hover_dark": "#f1f5f9",
        "active_light": "#e2e8f0",
        "active_dark": "#cbd5e1",
        "disabled": "#94a3b8",
        "disabled_bg": "#f1f5f9",
        # Shadow Colors (for reference, not used in CTk)
        "shadow_light": "#000000",
        "shadow_medium": "#000000",
        "shadow_dark": "#000000",
        # Special Colors
        "selection": "#3b82f6",  # Text selection
        "highlight": "#fef3c7",  # Search highlights
        "link": "#1e40af",  # Links
        "link_hover": "#3b82f6",  # Link hover
    },
}


class FontSizes(TypedDict):
    small: int
    large: int
    normal: int
    medium: int
    xlarge: int


class AppSettingsType(TypedDict):
    font_family: str
    font_sizes: FontSizes
    title: str
    default_width: int
    default_height: int
    min_width: int
    min_height: int
    sidebar_width: int
    sandbox_directory: str


# App settings
APP_SETTINGS: AppSettingsType = {
    "title": "Jeeves - AI Assistant",
    "default_width": 1200,
    "default_height": 800,
    "min_width": 800,
    "min_height": 600,
    "sidebar_width": 300,
    "font_family": "Fira Code",
    "font_sizes": {"small": 11, "normal": 14, "medium": 16, "large": 18, "xlarge": 20},
    "sandbox_directory": "~/.jeeves",  # Centralized sandbox directory configuration
}

# AI Provider settings
AI_PROVIDER_SETTINGS = {
    "default_provider": "gemini",
    "providers": {
        "gemini": {
            "enabled": True,
            "model": "gemini-2.5-flash-lite-preview-06-17",
            "max_output_tokens": 2048,
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "system_instruction": None,  # Use default
            "api_key_env_var": "GOOGLE_API_KEY",
        },
        "placeholder": {"enabled": True, "fallback": True},
    },
    "provider_order": ["gemini", "placeholder"],
}

# Thread data for sidebar
DEFAULT_THREADS = [
    ("project", "Project Discussion"),
    ("code", "Code Review"),
    ("question", "General Questions"),
    ("notes", "Meeting Notes"),
    ("idea", "Ideas & Brainstorming"),
    ("support", "Technical Support"),
    ("planning", "Planning Session"),
    ("docs", "Documentation Help"),
    ("target", "Goal Setting"),
    ("rocket", "Feature Planning"),
]
