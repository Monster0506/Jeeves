"""
Chat display component for Jeeves GUI.
"""
import customtkinter as ctk
import tkinter as tk
from typing import Callable, List, Dict
from datetime import datetime, timedelta
from markdown_it import MarkdownIt
import logging
from ..config.settings import COLORS, APP_SETTINGS

logger = logging.getLogger(__name__)
logging.getLogger("markdown_it").setLevel(logging.WARNING)

# --- Paste the full ChatDisplay class here, unchanged --- 
class ChatDisplay(ctk.CTkFrame):
    """Chat display component for showing messages."""
    
    def __init__(self, parent, on_send_message: Callable = None, 
                 on_export_chat: Callable = None, on_search_messages: Callable = None):
        super().__init__(parent)
        
        self.on_send_message = on_send_message
        self.on_export_chat = on_export_chat
        self.on_search_messages = on_search_messages

        # Initialize markdown parser
        self.md = MarkdownIt()
        
        self._setup_ui()
        self._setup_bindings()
        self._configure_markdown_styles()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        
        # Create chat area frame
        self.chat_frame = ctk.CTkFrame(self)
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_frame.grid_rowconfigure(0, weight=1)
        
        # Create standard tkinter Text widget for messages
        self.chat_text = tk.Text(
            self.chat_frame,
            font=("Fira Code", 12),
            wrap="word",
            state="disabled",
            bg=COLORS['dark']['bg_primary'],
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            relief="flat",
            borderwidth=0
        )
        self.chat_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Create standard tkinter Scrollbar
        self.scrollbar = tk.Scrollbar(
            self.chat_frame,
            command=self.chat_text.yview
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns", pady=10)
        self.chat_text.configure(yscrollcommand=self.scrollbar.set)
        
        # Create input area
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        # Create input field
        self.input_field = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Type your message here...",
            font=("Fira Code", 12),
            height=40
        )
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Create send button
        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="Send",
            command=self._send_message,
            width=80,
            height=40,
            font=("Fira Code", 12)
        )
        self.send_button.grid(row=0, column=1)
        
        # Create toolbar
        self.toolbar_frame = ctk.CTkFrame(self)
        self.toolbar_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # Create toolbar buttons
        self.search_button = ctk.CTkButton(
            self.toolbar_frame,
            text="🔍 Search",
            command=self._search_messages,
            width=100,
            height=30,
            font=("Fira Code", 10)
        )
        self.search_button.pack(side="left", padx=(0, 10))
        
        self.export_button = ctk.CTkButton(
            self.toolbar_frame,
            text="📤 Export",
            command=self._export_chat,
            width=100,
            height=30,
            font=("Fira Code", 10)
        )
        self.export_button.pack(side="left", padx=(0, 10))
        
        self.clear_button = ctk.CTkButton(
            self.toolbar_frame,
            text="🗑️ Clear",
            command=self.clear_messages,
            width=100,
            height=30,
            font=("Fira Code", 10)
        )
        self.clear_button.pack(side="left")
    
    def _get_ctk_color(self, color):
        # Helper to get a color string from CTk color tuple or string
        if isinstance(color, (tuple, list)):
            return color[0]
        return color
    
    def _setup_bindings(self):
        """Setup keyboard bindings."""
        self.input_field.bind("<Return>", lambda e: self._send_message())
        self.input_field.bind("<Shift-Return>", lambda e: self._insert_newline())
    
    def _send_message(self):
        """Send the current message."""
        message = self.input_field.get().strip()
        if message and self.on_send_message:
            self.on_send_message(message)
            self.input_field.delete(0, "end")
    
    def _insert_newline(self):
        """Insert a newline in the input field."""
        current_text = self.input_field.get()
        cursor_pos = self.input_field.index("insert")
        new_text = current_text[:cursor_pos] + "\n" + current_text[cursor_pos:]
        self.input_field.delete(0, "end")
        self.input_field.insert(0, new_text)
        self.input_field.icursor(cursor_pos + 1)
    
    def _search_messages(self):
        """Trigger message search."""
        if self.on_search_messages:
            self.on_search_messages()
    
    def _export_chat(self):
        """Trigger chat export."""
        if self.on_export_chat:
            self.on_export_chat()
    
    def _configure_markdown_styles(self):
        """Configure styles for markdown rendering."""
        # Fonts
        self.bold_font = ("Fira Code", 12, "bold")
        self.italic_font = ("Fira Code", 12, "italic")
        self.code_font = ("Courier New", 12)
        self.h1_font = ("Fira Code", 18, "bold")
        self.h2_font = ("Fira Code", 16, "bold")
        self.h3_font = ("Fira Code", 14, "bold")

        # Tags
        self.chat_text.tag_config("bold", font=self.bold_font)
        self.chat_text.tag_config("italic", font=self.italic_font)
        self.chat_text.tag_config("code", font=self.code_font, background="#2E2E2E", lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_text.tag_config("h1", font=self.h1_font, foreground="#FFD700")
        self.chat_text.tag_config("h2", font=self.h2_font, foreground="#FFA500")
        self.chat_text.tag_config("h3", font=self.h3_font, foreground="#87CEEB")
        self.chat_text.tag_config("user", foreground="#4CAF50")
        self.chat_text.tag_config("ai", foreground="#2196F3")
        self.chat_text.tag_config("system", foreground="#FF9800")
        self.chat_text.tag_config("other", foreground="#9E9E9E")

    def _render_markdown(self, text: str, initial_tag: str):
        """Render markdown text to the chat widget."""
        tokens = self.md.parse(text)
        
        active_tags = []

        for token in tokens:
            if token.type == "paragraph_open":
                continue
            if token.type == "paragraph_close":
                self.chat_text.insert("end", "\n")
                continue

            if token.type.endswith("_open"):
                tag_name = token.tag
                if token.tag == "em":
                    tag_name = "italic"
                elif token.tag == "strong":
                    tag_name = "bold"
                elif token.tag == "code_inline":
                    tag_name = "code"
                elif token.tag in ["h1", "h2", "h3"]:
                    tag_name = token.tag
                
                active_tags.append(tag_name)

            elif token.type.endswith("_close"):
                active_tags.pop()

            elif token.type == "text":
                tags_to_apply = tuple([initial_tag] + active_tags)
                self.chat_text.insert("end", token.content, tags_to_apply)
            
            elif token.type == "code_fence":
                tags_to_apply = tuple([initial_tag, "code"])
                self.chat_text.insert("end", token.content, tags_to_apply)

            elif token.type == "bullet_list_open":
                continue
            elif token.type == "bullet_list_close":
                continue
            elif token.type == "list_item_open":
                self.chat_text.insert("end", "  • ", initial_tag)
            elif token.type == "list_item_close":
                self.chat_text.insert("end", "\n")
                
            elif token.type == "heading_open":
                active_tags.append(token.tag)
            elif token.type == "heading_close":
                active_tags.pop()
                self.chat_text.insert("end", "\n")
                
            elif token.type == "inline":
                self._render_markdown_inline(token.children, initial_tag)

    def _render_markdown_inline(self, tokens: List, initial_tag: str):
        """Render inline markdown tokens."""
        active_tags = []
        for token in tokens:
            if token.type.endswith("_open"):
                tag_name = token.tag
                if token.tag == "em":
                    tag_name = "italic"
                elif token.tag == "strong":
                    tag_name = "bold"
                elif token.tag == "code_inline":
                    tag_name = "code"
                active_tags.append(tag_name)
            elif token.type.endswith("_close"):
                active_tags.pop()
            elif token.type == "text":
                tags_to_apply = tuple([initial_tag] + active_tags)
                self.chat_text.insert("end", token.content, tags_to_apply)

    def add_user_message(self, message: str):
        """Add a user message to the chat."""
        self._add_message(message, "user")
    
    def add_ai_message(self, message: str):
        """Add an AI message to the chat."""
        self._add_message(message, "ai")
    
    def add_system_message(self, message: str):
        """Add a system message to the chat."""
        self._add_message(message, "system")
    
    def _add_message(self, message: str, sender: str):
        """Add a message to the chat display."""
        try:
            self.chat_text.configure(state="normal")
            
            # Get current timestamp
            timestamp = datetime.now().strftime("%H:%M")
            
            # Format message based on sender
            if sender == "user":
                prefix = f"[{timestamp}] 👤 You:\n"
                tag = "user"
            elif sender == "ai":
                prefix = f"[{timestamp}] 🤖 Jeeves:\n"
                tag = "ai"
            elif sender == "system":
                prefix = f"[{timestamp}] ⚙️ System:\n"
                tag = "system"
            else:
                prefix = f"[{timestamp}] 💬 {sender.title()}:\n"
                tag = "other"
            
            # Insert message
            self.chat_text.insert("end", prefix, tag)
            self._render_markdown(message, tag)
            self.chat_text.insert("end", "\n\n")
            
            # Configure tags for styling
            self.chat_text.tag_config("user", foreground="#4CAF50")
            self.chat_text.tag_config("ai", foreground="#2196F3")
            self.chat_text.tag_config("system", foreground="#FF9800")
            self.chat_text.tag_config("other", foreground="#9E9E9E")
            
            # Scroll to bottom
            self.chat_text.see("end")
            
            self.chat_text.configure(state="disabled")
            
        except Exception as e:
            logger.error(f"Error adding message: {e}")
    
    def load_messages(self, messages: List[Dict]):
        """Load messages from database."""
        try:
            self.clear_messages()
            
            for message in messages:
                sender = message.get('sender', 'unknown')
                content = message.get('content', '')
                timestamp = message.get('timestamp', '')
                
                # Parse timestamp if it's a string
                if timestamp and isinstance(timestamp, str):
                    try:
                        # SQLite CURRENT_TIMESTAMP stores UTC time, convert to local time (EST/EDT)
                        dt = datetime.fromisoformat(timestamp)
                        # Apply timezone offset (subtract 4 hours to convert UTC to EST)
                        dt = dt - timedelta(hours=4)
                        formatted_time = dt.strftime("%H:%M")
                    except Exception as e:
                        logger.warning(f"Could not parse timestamp '{timestamp}': {e}")
                        formatted_time = "??:??"
                else:
                    formatted_time = "??:??"
                
                # Add message with proper formatting
                self.chat_text.configure(state="normal")
                
                if sender == "user":
                    prefix = f"[{formatted_time}] 👤 You:\n"
                    tag = "user"
                elif sender == "ai":
                    prefix = f"[{formatted_time}] 🤖 Jeeves:\n"
                    tag = "ai"
                elif sender == "system":
                    prefix = f"[{formatted_time}] ⚙️ System:\n"
                    tag = "system"
                else:
                    prefix = f"[{formatted_time}] 💬 {sender.title()}:\n"
                    tag = "other"
                
                self.chat_text.insert("end", prefix, tag)
                self._render_markdown(content, tag)
                self.chat_text.insert("end", "\n\n")
                
                # Configure tags
                self.chat_text.tag_config("user", foreground="#4CAF50")
                self.chat_text.tag_config("ai", foreground="#2196F3")
                self.chat_text.tag_config("system", foreground="#FF9800")
                self.chat_text.tag_config("other", foreground="#9E9E9E")
                
                self.chat_text.configure(state="disabled")
            
            # Scroll to bottom
            self.chat_text.see("end")
            
        except Exception as e:
            logger.error(f"Failed to load messages: {e}")
    
    def clear_messages(self):
        """Clear all messages from the chat display."""
        try:
            self.chat_text.configure(state="normal")
            self.chat_text.delete("1.0", "end")
            self.chat_text.configure(state="disabled")
        except Exception as e:
            logger.error(f"Error clearing messages: {e}")

