"""
Reusable GUI components for the chat application.
"""
import customtkinter as ctk
import threading
from datetime import datetime, timedelta
from typing import Callable, List, Dict, Optional
from ..config.settings import ICONS, APP_SETTINGS, DEFAULT_THREADS
import logging
import time

logger = logging.getLogger(__name__)


class ChatDisplay(ctk.CTkFrame):
    """Chat display component for showing messages."""
    
    def __init__(self, parent, on_send_message: Callable = None, 
                 on_export_chat: Callable = None, on_search_messages: Callable = None):
        super().__init__(parent)
        
        self.on_send_message = on_send_message
        self.on_export_chat = on_export_chat
        self.on_search_messages = on_search_messages
        
        self._setup_ui()
        self._setup_bindings()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        
        # Create chat area
        self.chat_frame = ctk.CTkFrame(self)
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_frame.grid_rowconfigure(0, weight=1)
        
        # Create text widget for messages
        self.chat_text = ctk.CTkTextbox(
            self.chat_frame,
            font=("Fira Code", 12),
            wrap="word",
            state="disabled"
        )
        self.chat_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Create scrollbar
        self.scrollbar = ctk.CTkScrollbar(
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
                prefix = f"[{timestamp}] 👤 You: "
                tag = "user"
            elif sender == "ai":
                prefix = f"[{timestamp}] 🤖 Jeeves: "
                tag = "ai"
            elif sender == "system":
                prefix = f"[{timestamp}] ⚙️ System: "
                tag = "system"
            else:
                prefix = f"[{timestamp}] 💬 {sender.title()}: "
                tag = "other"
            
            # Insert message
            self.chat_text.insert("end", prefix, tag)
            self.chat_text.insert("end", message + "\n\n")
            
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
                    prefix = f"[{formatted_time}] 👤 You: "
                    tag = "user"
                elif sender == "ai":
                    prefix = f"[{formatted_time}] 🤖 Jeeves: "
                    tag = "ai"
                elif sender == "system":
                    prefix = f"[{formatted_time}] ⚙️ System: "
                    tag = "system"
                else:
                    prefix = f"[{formatted_time}] 💬 {sender.title()}: "
                    tag = "other"
                
                self.chat_text.insert("end", prefix, tag)
                self.chat_text.insert("end", content + "\n\n")
                
                # Configure tags
                self.chat_text.tag_config("user", foreground="#4CAF50")
                self.chat_text.tag_config("ai", foreground="#2196F3")
                self.chat_text.tag_config("system", foreground="#FF9800")
                self.chat_text.tag_config("other", foreground="#9E9E9E")
                
                self.chat_text.configure(state="disabled")
            
            # Scroll to bottom
            self.chat_text.see("end")
            
        except Exception as e:
            logger.error(f"Error loading messages: {e}")
    
    def clear_messages(self):
        """Clear all messages from the chat display."""
        try:
            self.chat_text.configure(state="normal")
            self.chat_text.delete("1.0", "end")
            self.chat_text.configure(state="disabled")
        except Exception as e:
            logger.error(f"Error clearing messages: {e}")


class Sidebar(ctk.CTkFrame):
    """Sidebar component with thread management."""
    
    def __init__(self, parent, on_thread_select: Callable = None, 
                 on_new_thread: Callable = None, on_delete_thread: Callable = None,
                 on_rename_thread: Callable = None):
        super().__init__(parent, width=300)
        
        self.on_thread_select = on_thread_select
        self.on_new_thread = on_new_thread
        self.on_delete_thread = on_delete_thread
        self.on_rename_thread = on_rename_thread
        
        self.threads = []
        self.current_thread_id = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create header
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Create title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Conversations",
            font=("Fira Code", 16, "bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        # Create new thread button
        self.new_thread_button = ctk.CTkButton(
            self.header_frame,
            text="+ New",
            command=self._create_new_thread,
            width=80,
            height=30,
            font=("Fira Code", 12)
        )
        self.new_thread_button.grid(row=0, column=1, padx=(0, 10), pady=10)
        
        # Create threads list
        self.threads_frame = ctk.CTkScrollableFrame(self)
        self.threads_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.threads_frame.grid_columnconfigure(0, weight=1)
        
        # Create thread buttons list
        self.thread_buttons = []
    
    def _create_new_thread(self):
        """Create a new thread."""
        if self.on_new_thread:
            self.on_new_thread()
    
    def load_threads(self, threads: List[Dict]):
        """Load threads into the sidebar."""
        try:
            self.threads = threads
            self._update_thread_buttons()
        except Exception as e:
            logger.error(f"Error loading threads: {e}")
    
    def _update_thread_buttons(self):
        """Update the thread buttons display."""
        try:
            # Clear existing buttons
            for button in self.thread_buttons:
                button.destroy()
            self.thread_buttons.clear()
            
            # Create new buttons
            for i, thread in enumerate(self.threads):
                button = self._create_thread_button(thread, i)
                self.thread_buttons.append(button)
                
        except Exception as e:
            logger.error(f"Error updating thread buttons: {e}")
    
    def _create_thread_button(self, thread: Dict, index: int) -> ctk.CTkButton:
        """Create a button for a thread."""
        try:
            # Create button frame
            button_frame = ctk.CTkFrame(self.threads_frame)
            button_frame.grid(row=index, column=0, sticky="ew", pady=2)
            button_frame.grid_columnconfigure(0, weight=1)
            
            # Create main button
            button = ctk.CTkButton(
                button_frame,
                text=f"{thread.get('icon', '💬')} {thread.get('name', 'Unknown')}",
                command=lambda: self._select_thread(thread['id']),
                anchor="w",
                height=40,
                font=("Fira Code", 12)
            )
            button.grid(row=0, column=0, sticky="ew", padx=(5, 0), pady=5)
            
            # Create context menu button
            menu_button = ctk.CTkButton(
                button_frame,
                text="⋮",
                command=lambda: self._show_thread_menu(thread),
                width=30,
                height=30,
                font=("Fira Code", 14)
            )
            menu_button.grid(row=0, column=1, padx=(5, 5), pady=5)
            
            # Highlight current thread
            if thread['id'] == self.current_thread_id:
                button.configure(fg_color="#2196F3")
            
            return button
            
        except Exception as e:
            logger.error(f"Error creating thread button: {e}")
            return None
    
    def _select_thread(self, thread_id: int):
        """Select a thread."""
        if self.on_thread_select:
            self.on_thread_select(thread_id)
    
    def _show_thread_menu(self, thread: Dict):
        """Show context menu for a thread."""
        try:
            # Create popup menu
            menu = ctk.CTkToplevel(self)
            menu.title("Thread Options")
            menu.geometry("200x150")
            menu.resizable(False, False)
            menu.transient(self)
            menu.grab_set()
            
            # Center the menu
            menu.update_idletasks()
            x = (menu.winfo_screenwidth() // 2) - (200 // 2)
            y = (menu.winfo_screenheight() // 2) - (150 // 2)
            menu.geometry(f"200x150+{x}+{y}")
            
            # Create menu buttons
            rename_button = ctk.CTkButton(
                menu,
                text="Rename",
                command=lambda: self._rename_thread(thread, menu),
                width=180,
                height=30,
                font=("Fira Code", 12)
            )
            rename_button.pack(pady=10)
            
            delete_button = ctk.CTkButton(
                menu,
                text="Delete",
                command=lambda: self._delete_thread(thread, menu),
                width=180,
                height=30,
                font=("Fira Code", 12),
                fg_color="#f44336",
                hover_color="#d32f2f"
            )
            delete_button.pack(pady=10)
            
            cancel_button = ctk.CTkButton(
                menu,
                text="Cancel",
                command=menu.destroy,
                width=180,
                height=30,
                font=("Fira Code", 12)
            )
            cancel_button.pack(pady=10)
            
        except Exception as e:
            logger.error(f"Error showing thread menu: {e}")
    
    def _rename_thread(self, thread: Dict, menu):
        """Rename a thread."""
        try:
            menu.destroy()
            
            # Create rename dialog
            dialog = ctk.CTkToplevel(self)
            dialog.title("Rename Thread")
            dialog.geometry("300x150")
            dialog.resizable(False, False)
            dialog.transient(self)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
            y = (dialog.winfo_screenheight() // 2) - (150 // 2)
            dialog.geometry(f"300x150+{x}+{y}")
            
            # Create input field
            label = ctk.CTkLabel(dialog, text="New name:", font=("Fira Code", 12))
            label.pack(pady=10)
            
            entry = ctk.CTkEntry(dialog, font=("Fira Code", 12))
            entry.insert(0, thread.get('name', ''))
            entry.pack(pady=10)
            entry.focus_set()
            
            # Create buttons
            button_frame = ctk.CTkFrame(dialog)
            button_frame.pack(pady=10)
            
            save_button = ctk.CTkButton(
                button_frame,
                text="Save",
                command=lambda: self._save_rename(thread['id'], entry.get(), dialog),
                width=80,
                height=30,
                font=("Fira Code", 12)
            )
            save_button.pack(side="left", padx=5)
            
            cancel_button = ctk.CTkButton(
                button_frame,
                text="Cancel",
                command=dialog.destroy,
                width=80,
                height=30,
                font=("Fira Code", 12)
            )
            cancel_button.pack(side="left", padx=5)
            
            # Bind Enter key
            entry.bind("<Return>", lambda e: self._save_rename(thread['id'], entry.get(), dialog))
            
        except Exception as e:
            logger.error(f"Error renaming thread: {e}")
    
    def _save_rename(self, thread_id: int, new_name: str, dialog):
        """Save the renamed thread."""
        try:
            if new_name.strip():
                if self.on_rename_thread:
                    self.on_rename_thread(thread_id, new_name.strip())
            dialog.destroy()
        except Exception as e:
            logger.error(f"Error saving rename: {e}")
    
    def _delete_thread(self, thread: Dict, menu):
        """Delete a thread."""
        try:
            menu.destroy()
            
            # Create confirmation dialog
            dialog = ctk.CTkToplevel(self)
            dialog.title("Delete Thread")
            dialog.geometry("300x150")
            dialog.resizable(False, False)
            dialog.transient(self)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
            y = (dialog.winfo_screenheight() // 2) - (150 // 2)
            dialog.geometry(f"300x150+{x}+{y}")
            
            # Create message
            message = ctk.CTkLabel(
                dialog, 
                text=f"Delete '{thread.get('name', 'Unknown')}'?\nThis action cannot be undone.",
                font=("Fira Code", 12)
            )
            message.pack(pady=20)
            
            # Create buttons
            button_frame = ctk.CTkFrame(dialog)
            button_frame.pack(pady=10)
            
            delete_button = ctk.CTkButton(
                button_frame,
                text="Delete",
                command=lambda: self._confirm_delete(thread['id'], dialog),
                width=80,
                height=30,
                font=("Fira Code", 12),
                fg_color="#f44336",
                hover_color="#d32f2f"
            )
            delete_button.pack(side="left", padx=5)
            
            cancel_button = ctk.CTkButton(
                button_frame,
                text="Cancel",
                command=dialog.destroy,
                width=80,
                height=30,
                font=("Fira Code", 12)
            )
            cancel_button.pack(side="left", padx=5)
            
        except Exception as e:
            logger.error(f"Error deleting thread: {e}")
    
    def _confirm_delete(self, thread_id: int, dialog):
        """Confirm thread deletion."""
        try:
            if self.on_delete_thread:
                self.on_delete_thread(thread_id)
            dialog.destroy()
        except Exception as e:
            logger.error(f"Error confirming delete: {e}")
    
    def set_current_thread(self, thread_id: int):
        """Set the current active thread."""
        self.current_thread_id = thread_id
        self._update_thread_buttons() 