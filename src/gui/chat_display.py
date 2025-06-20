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
import tkinter.font as tkfont

logger = logging.getLogger(__name__)
logging.getLogger("markdown_it").setLevel(logging.WARNING)

class MessageBubble(ctk.CTkFrame):
    def __init__(self, parent, sender, message, timestamp, is_user, theme, font_family, max_width=600, **kwargs):
        super().__init__(parent, fg_color="transparent", corner_radius=20, **kwargs)
        self.theme = theme
        self.is_user = is_user
        self.max_width = max_width
        self.font_family = font_family
        self._build_bubble(sender, message, timestamp)

    def _build_bubble(self, sender, message, timestamp):
        # Bubble color and alignment
        bubble_color = self.theme['bubble_user'] if self.is_user else self.theme['bubble_ai']
        text_color = self.theme['text_primary']
        anchor = 'e' if self.is_user else 'w'
        padx = (80, 16) if self.is_user else (16, 80)
        # Bubble frame
        bubble = ctk.CTkFrame(self, fg_color=bubble_color, corner_radius=20)
        bubble.grid(row=0, column=0, sticky=anchor, padx=padx, pady=2)
        bubble.grid_columnconfigure(0, weight=1)
        # Sender/timestamp
        meta_frame = ctk.CTkFrame(bubble, fg_color="transparent")
        meta_frame.grid(row=0, column=0, sticky="w", padx=12, pady=(8, 0))
        sender_label = ctk.CTkLabel(meta_frame, text=sender, font=(self.font_family, 12, "bold"), text_color=text_color)
        sender_label.pack(side="left")
        time_label = ctk.CTkLabel(meta_frame, text=timestamp, font=(self.font_family, 10), text_color=self.theme['text_secondary'])
        time_label.pack(side="left", padx=(8, 0))
        # Markdown message
        msg_frame = ctk.CTkFrame(bubble, fg_color="transparent")
        msg_frame.grid(row=1, column=0, sticky="w", padx=12, pady=(2, 8))
        self._render_markdown(msg_frame, message, text_color)
        # Set max width
        msg_frame.update_idletasks()
        width = min(msg_frame.winfo_reqwidth(), self.max_width)
        bubble.configure(width=width)

    def _render_markdown(self, parent, text, text_color):
        md = MarkdownIt()
        tokens = md.parse(text)
        # Simple markdown rendering: only bold, italic, code, headings, lists, blockquote
        row = 0
        for token in tokens:
            if token.type == "paragraph_open":
                continue
            if token.type == "paragraph_close":
                row += 1
                continue
            if token.type == "inline":
                label = ctk.CTkLabel(parent, text=token.content, font=(self.font_family, 13), text_color=text_color, wraplength=self.max_width-32, anchor="w", justify="left")
                label.grid(row=row, column=0, sticky="w", pady=0)
                row += 1
            if token.type == "fence" or token.type == "code_block":
                code = ctk.CTkLabel(parent, text=token.content, font=("Fira Mono", 12), text_color=self.theme['accent'], fg_color="#23272F", corner_radius=12, padx=8, pady=4, wraplength=self.max_width-32, anchor="w", justify="left")
                code.grid(row=row, column=0, sticky="w", pady=2)
                row += 1
            if token.type == "blockquote_open":
                # Blockquote background
                quote = ctk.CTkLabel(parent, text=token.map, font=(self.font_family, 13, "italic"), text_color=self.theme['text_secondary'], fg_color="#23272F", corner_radius=12, padx=8, pady=4, wraplength=self.max_width-32, anchor="w", justify="left")
                quote.grid(row=row, column=0, sticky="w", pady=2)
                row += 1

class ChatDisplay(ctk.CTkFrame):
    """Modern chat display with bubble design and markdown support."""
    def __init__(self, parent, on_send_message: Callable = None, on_export_chat: Callable = None, on_search_messages: Callable = None):
        super().__init__(parent)
        self.on_send_message = on_send_message
        self.on_export_chat = on_export_chat
        self.on_search_messages = on_search_messages
        self.theme = COLORS['dark']
        self.font_family = APP_SETTINGS['font_family']
        self._setup_ui()
        self._setup_bindings()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        # Scrollable chat area
        self.canvas = tk.Canvas(self, bg=self.theme['bg_chat'], highlightthickness=0, borderwidth=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self, fg_color=self.theme['bg_chat'])
        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        # Input area (unchanged)
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_field = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Type your message here...",
            font=(self.font_family, 12),
            height=40
        )
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="Send",
            command=self._send_message,
            width=80,
            height=40,
            font=(self.font_family, 12)
        )
        self.send_button.grid(row=0, column=1)
        # Toolbar (unchanged)
        self.toolbar_frame = ctk.CTkFrame(self)
        self.toolbar_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.search_button = ctk.CTkButton(
            self.toolbar_frame,
            text="🔍 Search",
            command=self._search_messages,
            width=100,
            height=30,
            font=(self.font_family, 10)
        )
        self.search_button.pack(side="left", padx=(0, 10))
        self.export_button = ctk.CTkButton(
            self.toolbar_frame,
            text="📤 Export",
            command=self._export_chat,
            width=100,
            height=30,
            font=(self.font_family, 10)
        )
        self.export_button.pack(side="left", padx=(0, 10))
        self.clear_button = ctk.CTkButton(
            self.toolbar_frame,
            text="🗑️ Clear",
            command=self.clear_messages,
            width=100,
            height=30,
            font=(self.font_family, 10)
        )
        self.clear_button.pack(side="left")

    def _setup_bindings(self):
        self.input_field.bind("<Return>", lambda e: self._send_message())
        self.input_field.bind("<Shift-Return>", lambda e: self._insert_newline())

    def _send_message(self):
        message = self.input_field.get().strip()
        if message and self.on_send_message:
            self.on_send_message(message)
            self.input_field.delete(0, "end")

    def _insert_newline(self):
        current_text = self.input_field.get()
        cursor_pos = self.input_field.index("insert")
        new_text = current_text[:cursor_pos] + "\n" + current_text[cursor_pos:]
        self.input_field.delete(0, "end")
        self.input_field.insert(0, new_text)
        self.input_field.icursor(cursor_pos + 1)

    def add_user_message(self, message: str):
        self._add_message(message, "You", is_user=True)

    def add_ai_message(self, message: str):
        self._add_message(message, "Jeeves", is_user=False)

    def add_system_message(self, message: str):
        self._add_message(message, "System", is_user=False)

    def _add_message(self, message: str, sender: str, is_user: bool):
        timestamp = datetime.now().strftime("%H:%M")
        bubble = MessageBubble(self.scrollable_frame, sender, message, timestamp, is_user, self.theme, self.font_family)
        bubble.pack(anchor="e" if is_user else "w", pady=8, padx=8, fill=None)
        self.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def load_messages(self, messages: List[Dict]):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        for message in messages:
            sender = message.get('sender', 'unknown')
            content = message.get('content', '')
            timestamp = message.get('timestamp', '')
            is_user = sender == "user" or sender == "You"
            display_sender = "You" if is_user else ("Jeeves" if sender == "ai" else sender.title())
            bubble = MessageBubble(self.scrollable_frame, display_sender, content, timestamp, is_user, self.theme, self.font_family)
            bubble.pack(anchor="e" if is_user else "w", pady=8, padx=8, fill=None)
        self.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def clear_messages(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def _search_messages(self):
        """Trigger message search."""
        if self.on_search_messages:
            self.on_search_messages()
    
    def _export_chat(self):
        """Trigger chat export."""
        if self.on_export_chat:
            self.on_export_chat()

