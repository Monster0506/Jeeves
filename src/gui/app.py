"""
Main application for Jeeves AI Assistant using CustomTkinter.
"""

import hashlib
import logging
import shutil
import threading
import tkinter as tk  # Import tkinter for event typing
from pathlib import Path
from typing import Any, Optional

import customtkinter as ctk

from ..config.settings import APP_SETTINGS, COLORS
from ..core.ai_engine import AIEngine
from ..core.chat_manager import ChatManager
from ..core.database import DatabaseManager
from ..core.file_handler import JeevesFileHandler
from ..utils import normalize_mime_type
from ..utils.dialogs import show_error, show_info
from .components import ChatDisplay, Sidebar
from .finder_panel import FinderPanel

logger = logging.getLogger(__name__)
ctk.deactivate_automatic_dpi_awareness()


class JeevesApp:
    """Main application class for Jeeves AI Assistant."""

    def __init__(self) -> None:
        # Initialize database and managers
        self.db_manager = DatabaseManager()
        self.chat_manager = ChatManager(self.db_manager)
        self.ai_engine = AIEngine(self.chat_manager)
        self.file_handler = JeevesFileHandler()

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

    def _setup_ui(self) -> None:
        """Setup the user interface components."""
        theme = COLORS["dark"]
        font_family = APP_SETTINGS["font_family"]
        font_large = (font_family, APP_SETTINGS["font_sizes"]["large"], "bold")

        # Configure grid for header, sidebar, and main content
        self.root.grid_rowconfigure(0, weight=0)  # Header
        self.root.grid_rowconfigure(1, weight=1)  # Main content
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)

        # Header bar with enhanced styling and consistent spacing
        self.header = ctk.CTkFrame(
            self.root,
            fg_color=theme["bg_header"],
            height=64,  # Increased from 56 for better proportions
            corner_radius=0,
            border_width=0,
        )
        self.header.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.header.grid_columnconfigure(0, weight=1)
        self.header.grid_columnconfigure(1, weight=0)

        # Add a subtle border at the bottom of the header
        self.header_border = ctk.CTkFrame(self.root, fg_color=theme["border_divider"], height=1, corner_radius=0)
        self.header_border.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(63, 0))

        # App name/logo with enhanced styling and better spacing
        self.header_label = ctk.CTkLabel(
            self.header,
            text="🧑‍💻 Jeeves",
            font=font_large,
            text_color=theme["accent_primary"],
        )
        self.header_label.grid(row=0, column=0, sticky="w", padx=24, pady=16)  # Increased padding

        # Global actions with enhanced styling and consistent spacing
        self.settings_button = ctk.CTkButton(
            self.header,
            text="⚙️",
            width=56,  # Increased for better proportions
            height=56,  # Increased for better proportions
            fg_color=theme["button_secondary"],
            hover_color=theme["button_secondary_hover"],
            font=(font_family, 16, "bold"),  # Larger, bold font for icon
            corner_radius=28,  # Increased for modern look
            text_color=theme["text_primary"],
            border_width=1,  # Subtle border for definition
            border_color=theme["border_secondary"],
            command=lambda: show_info("Settings", "Settings coming soon!"),
        )
        self.settings_button.grid(row=0, column=1, sticky="e", padx=(0, 24), pady=8)  # Consistent padding

        # Add enhanced hover effects to settings button
        def on_settings_enter(event: tk.Event) -> None:
            self.settings_button.configure(corner_radius=30)  # Slightly larger radius on hover

        def on_settings_leave(event: tk.Event) -> None:
            self.settings_button.configure(corner_radius=28)  # Return to normal radius

        self.settings_button.bind("<Enter>", on_settings_enter)
        self.settings_button.bind("<Leave>", on_settings_leave)

        # Main content area with enhanced styling and better spacing
        self.main_frame = ctk.CTkFrame(self.root, fg_color=theme["bg_primary"], corner_radius=0, border_width=0)
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=16)  # Consistent margins
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Chat display
        self.chat_display = ChatDisplay(
            self.main_frame,
            on_send_message=self._on_send_message,
            on_export_chat=self._on_export_chat,
            on_search_messages=self._on_search_messages,
            on_attachment=self._on_attachment,
        )
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)  # Consistent internal spacing

        # Sidebar with better spacing
        self.sidebar = Sidebar(
            self.root,
            on_thread_select=self._on_thread_select,
            on_new_thread=self._on_new_thread,
            on_delete_thread=self._on_delete_thread,
            on_rename_thread=self._on_rename_thread,
        )
        self.sidebar.grid(row=1, column=1, sticky="nsew", padx=(8, 16), pady=16)  # Consistent spacing

        # Sidebar toggle button with enhanced styling and better positioning
        self.sidebar_toggle = ctk.CTkButton(
            self.root,
            text="☰",
            width=56,  # Increased for better proportions
            height=56,  # Increased for better proportions
            command=self._toggle_sidebar,
            font=(font_family, 16, "bold"),  # Larger, bold font for icon
            fg_color=theme["button_secondary"],
            hover_color=theme["button_secondary_hover"],
            text_color=theme["text_primary"],
            corner_radius=28,  # Increased for modern look
            border_width=1,  # Subtle border for definition
            border_color=theme["border_secondary"],
        )
        self.sidebar_toggle.grid(row=1, column=1, sticky="ne", padx=(0, 24), pady=(24, 0))  # Better positioning

        # Add enhanced hover effects to sidebar toggle button
        def on_toggle_enter(event: tk.Event) -> None:
            self.sidebar_toggle.configure(corner_radius=30)  # Slightly larger radius on hover

        def on_toggle_leave(event: tk.Event) -> None:
            self.sidebar_toggle.configure(corner_radius=28)  # Return to normal radius

        self.sidebar_toggle.bind("<Enter>", on_toggle_enter)
        self.sidebar_toggle.bind("<Leave>", on_toggle_leave)

        self.sidebar.grid_remove()
        self.sidebar_visible = False

        # Finder panel
        self.finder_panel = FinderPanel(self.root, on_search=self._perform_search)

    def _setup_bindings(self) -> None:
        """Setup keyboard and window bindings."""
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Bind keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self._on_new_thread())
        self.root.bind("<Control-f>", lambda e: self._on_search_messages())
        self.root.bind("<Control-e>", lambda e: self._on_export_chat())
        self.root.bind("<Control-q>", lambda e: self._on_closing())
        self.root.bind("<Escape>", lambda e: self.finder_panel.hide())

    def _load_initial_data(self) -> None:
        """Load initial data from database."""
        try:
            # Load threads
            threads = self.chat_manager.get_threads()
            self.sidebar.load_threads(threads)

            # Set current thread
            if threads:
                current_thread = self.chat_manager.get_current_thread()
                if current_thread:
                    self.sidebar.set_current_thread(current_thread["id"])
                    self._load_thread_messages(current_thread["id"])
                else:
                    # Switch to first thread
                    self.chat_manager.switch_thread(threads[0]["id"])
                    self.sidebar.set_current_thread(threads[0]["id"])
                    self._load_thread_messages(threads[0]["id"])

            logger.info("Initial data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load initial data: {e}")
            show_error("Error", f"Failed to load data: {e}")

    def _on_thread_select(self, thread_id: int) -> None:
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

    def _on_new_thread(self) -> None:
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

    def _on_delete_thread(self, thread_id: int) -> None:
        """Handle thread deletion."""
        try:
            if self.chat_manager.delete_thread(thread_id):
                threads = self.chat_manager.get_threads()
                self.sidebar.load_threads(threads)

                # If we deleted the current thread, switch to another one
                current_thread = self.chat_manager.get_current_thread()
                if current_thread:
                    self.sidebar.set_current_thread(current_thread["id"])
                    self._load_thread_messages(current_thread["id"])
                else:
                    self.chat_display.clear_messages()

                logger.info(f"Deleted thread: {thread_id}")
        except Exception as e:
            logger.error(f"Failed to delete thread: {e}")
            show_error("Error", f"Failed to delete thread: {e}")

    def _on_rename_thread(self, thread_id: int, new_name: str) -> None:
        """Handle thread renaming."""
        try:
            if self.chat_manager.update_thread_name(thread_id, new_name):
                threads = self.chat_manager.get_threads()
                self.sidebar.load_threads(threads)
                logger.info(f"Renamed thread {thread_id} to: {new_name}")
        except Exception as e:
            logger.error(f"Failed to rename thread: {e}")
            show_error("Error", f"Failed to rename thread: {e}")

    def _on_send_message(self, message: str, attachments: Optional[list[dict]] = None) -> None:
        """Handle sending a message."""
        # The message no longer contains attachment text, so no cleaning is needed.

        try:
            # Add user message to chat display immediately
            # We construct the display text here, including attachments
            display_message = message
            if attachments:
                attachment_text = "\n\n**Attachments:**\n"
                for att in attachments:
                    file_size_mb = att.get("size", 0) / 1024 / 1024
                    attachment_text += f"- {att.get('name', '...')} ({file_size_mb:.1f}MB)\n"
                display_message += attachment_text

            self.chat_display.add_user_message(display_message)

            # Process attachments for the backend
            processed_attachments = []
            if attachments:
                for attachment in attachments:
                    processed = self._process_attachment(attachment)
                    if processed:
                        processed_attachments.append(processed)

            # Generate AI response in a separate thread
            def generate_response() -> None:
                try:
                    response = self.ai_engine.generate_response(message, attachments=processed_attachments)
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

    def _on_attachment(self, attachment_info: dict[str, Any]) -> None:
        """Handle file attachment processing."""
        try:
            # For now, we'll just log the attachment info
            # In the future, this could involve:
            # - Copying files to a secure location
            # - Processing file content for AI analysis
            # - Storing file metadata in the database
            logger.info(f"Processing attachment: {attachment_info['name']} ({attachment_info['size']} bytes)")

            # You could add file processing logic here
            # For example, copying to sandbox directory:
            # from ..core.file_handler import JeevesFileHandler
            # file_handler = JeevesFileHandler()
            # file_handler.copy_file(attachment_info['path'], f"attachments/{attachment_info['name']}")

        except Exception as e:
            logger.error(f"Failed to process attachment: {e}")
            show_error("Error", f"Failed to process attachment: {e}")

    def _process_attachment(self, attachment_info: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Process an attachment and prepare it for storage in the sandbox."""
        try:
            import mimetypes
            from pathlib import Path

            from ..core.file_handler import JeevesFileHandler

            file_path = Path(attachment_info["path"])

            logger.info(f"Processing attachment: {attachment_info['name']} from {file_path}")

            # Initialize file handler for sandbox operations
            file_handler = JeevesFileHandler()

            # Check if the file is already in the attachments directory
            sandbox_root = file_handler.get_sandbox_root()
            file_absolute_path = file_path.resolve()

            # Check if the file is already within the attachments directory
            if str(file_absolute_path).startswith(str(Path(sandbox_root) / "attachments")):
                logger.info(f"File {attachment_info['name']} is already in attachments directory, using directly")

                # Get the relative path from sandbox root
                sandbox_path = str(file_absolute_path.relative_to(sandbox_root))

                # Generate file hash for integrity checking
                file_hash = self._calculate_file_hash(file_path)

                # Determine MIME type and normalize it
                mime_type_guess, _ = mimetypes.guess_type(str(file_path))
                mime_type = normalize_mime_type(mime_type_guess or "application/octet-stream")  # Provide default if None

                # Create processed attachment info using existing file
                processed_attachment: dict[str, Any] = {
                    "file_name": attachment_info["name"],
                    "original_path": str(file_path),
                    "sandbox_path": sandbox_path,
                    "sandbox_absolute_path": str(file_absolute_path),
                    "file_size": attachment_info["size"],
                    "mime_type": mime_type,
                    "hash": file_hash,
                    "type": attachment_info["type"],
                    "extension": attachment_info["extension"],
                }

                logger.info(f"Using existing file in attachments: {attachment_info['name']} -> {sandbox_path} ({mime_type}, {file_hash[:8]}...)")
                return processed_attachment

            # File is not in attachments directory, proceed with normal copy process
            # Generate a unique filename to avoid conflicts
            import uuid

            unique_id = uuid.uuid4().hex[:8]
            sandbox_filename = f"{unique_id}_{attachment_info['name']}"
            sandbox_path = f"attachments/{sandbox_filename}"

            # Get the absolute path in the sandbox
            sandbox_absolute_path = file_handler.get_absolute_path(sandbox_path)

            # Ensure the attachments directory exists
            file_handler.ensure_directory_exists("attachments")

            # Copy file directly to sandbox using shutil
            logger.info(f"Copying file to sandbox: {sandbox_path}")
            try:
                shutil.copy2(file_path, sandbox_absolute_path)
                logger.info(f"Successfully copied file to sandbox: {sandbox_absolute_path}")
            except Exception as e:
                logger.error(f"Failed to copy file to sandbox: {e}")
                return None

            # Generate file hash for integrity checking
            file_hash = self._calculate_file_hash(file_path)

            # Determine MIME type and normalize it
            mime_type_guess, _ = mimetypes.guess_type(str(file_path))
            mime_type = normalize_mime_type(mime_type_guess or "application/octet-stream")  # Provide default if None

            # Create processed attachment info with sandbox path
            processed_attachment = {
                "file_name": attachment_info["name"],
                "original_path": str(file_path),
                "sandbox_path": sandbox_path,
                "sandbox_absolute_path": sandbox_absolute_path,
                "file_size": attachment_info["size"],
                "mime_type": mime_type,
                "hash": file_hash,
                "type": attachment_info["type"],
                "extension": attachment_info["extension"],
            }

            logger.info(f"Successfully processed attachment: {attachment_info['name']} -> {sandbox_path} ({mime_type}, {file_hash[:8]}...)")
            return processed_attachment

        except Exception as e:
            logger.error(f"Failed to process attachment {attachment_info['name']}: {e}")
            return None

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate file hash: {e}")
            return ""

    def _on_message_added(self, message: dict[str, Any]) -> None:
        """Handle new message added to conversation."""
        # This is called by the chat manager when a message is added to the database
        # We don't need to do anything here since we handle UI updates in _on_send_message
        pass

    def _on_thread_changed(self, thread: dict[str, Any]) -> None:
        """Handle thread changes."""
        # Update sidebar if needed
        threads = self.chat_manager.get_threads()
        self.sidebar.load_threads(threads)
        self.chat_display.clear_messages()  # Also clear chat on programmatic thread change

    def _load_thread_messages(self, thread_id: int) -> None:
        """Load messages for a specific thread."""
        try:
            messages = self.chat_manager.get_messages(thread_id)
            self.chat_display.load_messages(messages)
        except Exception as e:
            logger.error(f"Failed to load messages for thread {thread_id}: {e}")

    def _on_export_chat(self) -> None:
        """Handle chat export."""
        try:
            current_thread = self.chat_manager.get_current_thread()
            if not current_thread:
                show_info("Info", "No conversation to export")
                return

            # For now, export as JSON
            export_path = self.chat_manager.export_conversation(format="json")
            show_info("Export Complete", f"Conversation exported to:\n{export_path}")
        except Exception as e:
            logger.error(f"Failed to export chat: {e}")
            show_error("Error", f"Failed to export chat: {e}")

    def _perform_search(self, query: str) -> None:
        """Perform a search and display the results in the finder panel."""
        try:
            results = []

            # Search chat history
            chat_results = self.chat_manager.search_messages(query)
            for res in chat_results:
                results.append(f"[CHAT] {res['thread_name']}: {res['content']}")

            # Search files in sandbox
            file_results = self.file_handler.search_file_contents(relative_root_path=".", pattern=query)
            for res in file_results:
                results.append(f"[FILE] {res['file_path']}:{res['line_number']} - {res['line_content']}")

            self.finder_panel.show_results(results)
        except Exception as e:
            logger.error(f"Failed to perform search: {e}")
            show_error("Error", f"Failed to perform search: {e}")

    def _on_search_messages(self) -> None:
        """Handle message search."""
        self.finder_panel.show()

    def _toggle_sidebar(self) -> None:
        """Toggle sidebar visibility."""
        if self.sidebar_visible:
            self.sidebar.grid_remove()
            self.sidebar_visible = False
        else:
            self.sidebar.grid()
            self.sidebar_visible = True

    def _on_closing(self) -> None:
        """Handle application closing."""
        try:
            logger.info("Window closing - hiding instead of quitting")
            # Hide the window instead of quitting the application
            self.hide_window()
        except Exception as e:
            logger.error(f"Error during window closing: {e}")
            # Only quit if there's an error
            self.root.quit()

    def run(self) -> None:
        """Run the application."""
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Application error: {e}")
            show_error("Fatal Error", f"Application error: {e}")
        finally:
            self._on_closing()

    def show_window(self) -> None:
        """Show the application window."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide_window(self) -> None:
        """Hide the application window."""
        self.root.withdraw()

    def is_visible(self) -> bool:
        """Check if the window is visible."""
        # winfo_viewable returns 1 if visible, 0 if hidden. Convert to bool.
        return bool(self.root.winfo_viewable())

    def shutdown(self) -> None:
        """Properly shutdown the application and close database connections."""
        try:
            # Close database connections
            self.chat_manager.close()
            logger.info("Application shutting down")
            self.root.quit()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            self.root.quit()
