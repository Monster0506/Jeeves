"""
Main application for Jeeves AI Assistant using CustomTkinter.
"""
import customtkinter as ctk
import threading
import logging
from typing import Dict, List, Optional
from ..core.database import DatabaseManager
from ..core.chat_manager import ChatManager
from ..core.ai_engine import AIEngine
from .components import ChatDisplay, Sidebar
from ..utils.dialogs import show_error, show_info
from ..config.settings import APP_SETTINGS, COLORS

logger = logging.getLogger(__name__)
ctk.deactivate_automatic_dpi_awareness()

class JeevesApp:
    """Main application class for Jeeves AI Assistant."""
    
    def __init__(self):
        # Initialize database and managers
        self.db_manager = DatabaseManager()
        self.chat_manager = ChatManager(self.db_manager)
        self.ai_engine = AIEngine(self.chat_manager)
        
        # Setup CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Jeeves AI Assistant")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Initialize UI components
        self._setup_ui()
        self._setup_bindings()
        
        # Load initial data
        self._load_initial_data()
        
        # Register callbacks
        self.chat_manager.register_message_callback(self._on_message_added)
        self.chat_manager.register_thread_callback(self._on_thread_changed)
        
        logger.info("Jeeves application initialized")
    
    def _setup_ui(self):
        """Setup the user interface components."""
        theme = COLORS['dark']
        font_family = APP_SETTINGS['font_family']
        font_large = (font_family, APP_SETTINGS['font_sizes']['large'], 'bold')
        font_normal = (font_family, APP_SETTINGS['font_sizes']['normal'])

        # Configure grid for header, sidebar, and main content
        self.root.grid_rowconfigure(0, weight=0)  # Header
        self.root.grid_rowconfigure(1, weight=1)  # Main content
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)

        # Header bar
        self.header = ctk.CTkFrame(self.root, fg_color=theme['bg_header'], height=56)
        self.header.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.header.grid_columnconfigure(0, weight=1)
        self.header.grid_columnconfigure(1, weight=0)

        # App name/logo
        self.header_label = ctk.CTkLabel(
            self.header,
            text="🧑‍💻 Jeeves",
            font=font_large,
            text_color=theme['accent']
        )
        self.header_label.grid(row=0, column=0, sticky="w", padx=24, pady=8)

        # Global actions (settings, theme switch)
        self.settings_button = ctk.CTkButton(
            self.header,
            text="⚙️",
            width=40,
            height=40,
            fg_color=theme['bg_secondary'],
            hover_color=theme['accent'],
            font=font_normal,
            corner_radius=20,
            command=lambda: show_info("Settings", "Settings coming soon!")
        )
        self.settings_button.grid(row=0, column=1, sticky="e", padx=(0, 24), pady=8)

        # Main content area (below header)
        self.main_frame = ctk.CTkFrame(self.root, fg_color=theme['bg_primary'])
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 0), pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Chat display
        self.chat_display = ChatDisplay(
            self.main_frame,
            on_send_message=self._on_send_message,
            on_export_chat=self._on_export_chat,
            on_search_messages=self._on_search_messages
        )
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        # Sidebar
        self.sidebar = Sidebar(
            self.root,
            on_thread_select=self._on_thread_select,
            on_new_thread=self._on_new_thread,
            on_delete_thread=self._on_delete_thread,
            on_rename_thread=self._on_rename_thread
        )
        self.sidebar.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)

        # Sidebar toggle button (optional, can be moved to header later)
        self.sidebar_toggle = ctk.CTkButton(
            self.root,
            text="☰",
            width=40,
            height=40,
            command=self._toggle_sidebar,
            font=font_normal
        )
        self.sidebar_toggle.grid(row=1, column=1, sticky="ne", padx=(0, 15), pady=(15, 0))
        self.sidebar.grid_remove()
        self.sidebar_visible = False
    
    def _setup_bindings(self):
        """Setup keyboard and window bindings."""
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Bind keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self._on_new_thread())
        self.root.bind("<Control-f>", lambda e: self._on_search_messages())
        self.root.bind("<Control-e>", lambda e: self._on_export_chat())
        self.root.bind("<Control-q>", lambda e: self._on_closing())
    
    def _load_initial_data(self):
        """Load initial data from database."""
        try:
            # Load threads
            threads = self.chat_manager.get_threads()
            self.sidebar.load_threads(threads)
            
            # Set current thread
            if threads:
                current_thread = self.chat_manager.get_current_thread()
                if current_thread:
                    self.sidebar.set_current_thread(current_thread['id'])
                    self._load_thread_messages(current_thread['id'])
                else:
                    # Switch to first thread
                    self.chat_manager.switch_thread(threads[0]['id'])
                    self.sidebar.set_current_thread(threads[0]['id'])
                    self._load_thread_messages(threads[0]['id'])
            
            logger.info("Initial data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load initial data: {e}")
            show_error("Error", f"Failed to load data: {e}")
    
    def _on_thread_select(self, thread_id: int):
        """Handle thread selection."""
        try:
            if self.chat_manager.switch_thread(thread_id):
                self.chat_display.clear_messages()  # Clear chat before loading new thread
                self._load_thread_messages(thread_id)
                self.sidebar.set_current_thread(thread_id)
                logger.info(f"Switched to thread {thread_id}")
        except Exception as e:
            logger.error(f"Failed to switch thread: {e}")
            show_error("Error", f"Failed to switch thread: {e}")
    
    def _on_new_thread(self):
        """Handle new thread creation."""
        try:
            thread_id = self.chat_manager.create_thread("New Chat", "💬")
            self.chat_manager.switch_thread(thread_id)  # Ensure backend switches to new thread
            threads = self.chat_manager.get_threads()
            self.sidebar.load_threads(threads)
            self.sidebar.set_current_thread(thread_id)
            self.chat_display.clear_messages()
            logger.info(f"Created new thread: {thread_id}")
        except Exception as e:
            logger.error(f"Failed to create new thread: {e}")
            show_error("Error", f"Failed to create new thread: {e}")
    
    def _on_delete_thread(self, thread_id: int):
        """Handle thread deletion."""
        try:
            if self.chat_manager.delete_thread(thread_id):
                threads = self.chat_manager.get_threads()
                self.sidebar.load_threads(threads)
                
                # If we deleted the current thread, switch to another one
                current_thread = self.chat_manager.get_current_thread()
                if current_thread:
                    self.sidebar.set_current_thread(current_thread['id'])
                    self._load_thread_messages(current_thread['id'])
                else:
                    self.chat_display.clear_messages()
                
                logger.info(f"Deleted thread: {thread_id}")
        except Exception as e:
            logger.error(f"Failed to delete thread: {e}")
            show_error("Error", f"Failed to delete thread: {e}")
    
    def _on_rename_thread(self, thread_id: int, new_name: str):
        """Handle thread renaming."""
        try:
            if self.chat_manager.update_thread_name(thread_id, new_name):
                threads = self.chat_manager.get_threads()
                self.sidebar.load_threads(threads)
                logger.info(f"Renamed thread {thread_id} to: {new_name}")
        except Exception as e:
            logger.error(f"Failed to rename thread: {e}")
            show_error("Error", f"Failed to rename thread: {e}")
    
    def _on_send_message(self, message: str):
        """Handle sending a message."""
        if not message.strip():
            return
        
        try:
            # Add user message to chat display immediately
            self.chat_display.add_user_message(message)
            
            # Generate AI response in a separate thread
            def generate_response():
                try:
                    response = self.ai_engine.generate_response(message)
                    # Update UI in main thread
                    self.root.after(0, lambda: self.chat_display.add_ai_message(response))
                except Exception as e:
                    logger.error(f"Failed to generate response: {e}")
                    error_msg = f"Sorry, I encountered an error: {e}"
                    self.root.after(0, lambda: self.chat_display.add_ai_message(error_msg))
            
            threading.Thread(target=generate_response, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            show_error("Error", f"Failed to send message: {e}")
    
    def _on_message_added(self, message: Dict):
        """Handle new message added to conversation."""
        # This is called by the chat manager when a message is added to the database
        # We don't need to do anything here since we handle UI updates in _on_send_message
        pass
    
    def _on_thread_changed(self, thread: Dict):
        """Handle thread changes."""
        # Update sidebar if needed
        threads = self.chat_manager.get_threads()
        self.sidebar.load_threads(threads)
        self.chat_display.clear_messages()  # Also clear chat on programmatic thread change
    
    def _load_thread_messages(self, thread_id: int):
        """Load messages for a specific thread."""
        try:
            messages = self.chat_manager.get_messages(thread_id)
            self.chat_display.load_messages(messages)
        except Exception as e:
            logger.error(f"Failed to load messages for thread {thread_id}: {e}")
    
    def _on_export_chat(self):
        """Handle chat export."""
        try:
            current_thread = self.chat_manager.get_current_thread()
            if not current_thread:
                show_info("Info", "No conversation to export")
                return
            
            # For now, export as JSON
            export_path = self.chat_manager.export_conversation(format='json')
            show_info("Export Complete", f"Conversation exported to:\n{export_path}")
        except Exception as e:
            logger.error(f"Failed to export chat: {e}")
            show_error("Error", f"Failed to export chat: {e}")
    
    def _on_search_messages(self):
        """Handle message search."""
        try:
            # For now, just show a placeholder
            show_info("Search", "Message search feature coming soon!")
        except Exception as e:
            logger.error(f"Failed to search messages: {e}")
            show_error("Error", f"Failed to search messages: {e}")
    
    def _toggle_sidebar(self):
        """Toggle sidebar visibility."""
        if self.sidebar_visible:
            self.sidebar.grid_remove()
            self.sidebar_visible = False
        else:
            self.sidebar.grid()
            self.sidebar_visible = True
    
    def _on_closing(self):
        """Handle application closing."""
        try:
            logger.info("Window closing - hiding instead of quitting")
            # Hide the window instead of quitting the application
            self.hide_window()
        except Exception as e:
            logger.error(f"Error during window closing: {e}")
            # Only quit if there's an error
            self.root.quit()
    
    def run(self):
        """Run the application."""
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Application error: {e}")
            show_error("Fatal Error", f"Application error: {e}")
        finally:
            self._on_closing()
    
    def show_window(self):
        """Show the application window."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def hide_window(self):
        """Hide the application window."""
        self.root.withdraw()
    
    def is_visible(self) -> bool:
        """Check if the window is visible."""
        return self.root.winfo_viewable()
    
    def shutdown(self):
        """Properly shutdown the application and close database connections."""
        try:
            # Close database connections
            self.chat_manager.close()
            logger.info("Application shutting down")
            self.root.quit()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            self.root.quit() 