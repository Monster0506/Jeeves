"""
Legacy import aggregator for Jeeves GUI components.
This file exists for backward compatibility. Use chat_display.py and sidebar.py directly.
"""
logger = logging.getLogger(__name__)
from .chat_display import ChatDisplay
from .sidebar import Sidebar 