"""
Sidebar component for Jeeves GUI.
"""
import customtkinter as ctk
from typing import Callable, List, Dict
from ..config.settings import COLORS, APP_SETTINGS
import logging

logger = logging.getLogger(__name__)

class Sidebar(ctk.CTkFrame):
    """Sidebar component with thread management."""
    
    def __init__(self, parent, on_thread_select: Callable = None, 
                 on_new_thread: Callable = None, on_delete_thread: Callable = None,
                 on_rename_thread: Callable = None):
        theme = COLORS['dark']
        font_family = APP_SETTINGS['font_family']
        font_large = (font_family, APP_SETTINGS['font_sizes']['large'], 'bold')
        font_normal = (font_family, APP_SETTINGS['font_sizes']['normal'])
        super().__init__(parent, width=300, fg_color=theme['bg_sidebar'])
        
        self.on_thread_select = on_thread_select
        self.on_new_thread = on_new_thread
        self.on_delete_thread = on_delete_thread
        self.on_rename_thread = on_rename_thread
        
        self.threads = []
        self.current_thread_id = None
        
        self._setup_ui(theme, font_large, font_normal)
    
    def _setup_ui(self, theme, font_large, font_normal):
        """Setup the user interface."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Sidebar header
        self.header_frame = ctk.CTkFrame(self, fg_color=theme['bg_sidebar'])
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 0))
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Conversations",
            font=font_large,
            text_color=theme['accent']
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=24, pady=18)
        
        self.new_thread_button = ctk.CTkButton(
            self.header_frame,
            text="+ New",
            command=self._create_new_thread,
            width=120,
            height=38,
            font=font_normal,
            fg_color=theme['accent'],
            text_color=theme['bg_primary'],
            hover_color=theme['accent_alt'],
            corner_radius=19
        )
        self.new_thread_button.grid(row=0, column=1, padx=(0, 18), pady=12)
        
        # Threads list
        self.threads_frame = ctk.CTkScrollableFrame(self, fg_color=theme['bg_sidebar'])
        self.threads_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=(0, 0))
        self.threads_frame.grid_columnconfigure(0, weight=1)
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
        try:
            for button in self.thread_buttons:
                button.destroy()
            self.thread_buttons.clear()
            theme = COLORS['dark']
            font_family = APP_SETTINGS['font_family']
            font_normal = (font_family, APP_SETTINGS['font_sizes']['normal'])
            for i, thread in enumerate(self.threads):
                button = self._create_thread_button(thread, i, theme, font_normal)
                self.thread_buttons.append(button)
        except Exception as e:
            logger.error(f"Error updating thread buttons: {e}")
    
    def _create_thread_button(self, thread: Dict, index: int, theme, font_normal) -> ctk.CTkButton:
        try:
            button_frame = ctk.CTkFrame(self.threads_frame, fg_color=theme['bg_sidebar'])
            button_frame.grid(row=index, column=0, sticky="ew", pady=6, padx=18)
            button_frame.grid_columnconfigure(0, weight=1)
            is_active = thread['id'] == self.current_thread_id
            button = ctk.CTkButton(
                button_frame,
                text=f"{thread.get('icon', '💬')} {thread.get('name', 'Unknown')}",
                command=lambda: self._select_thread(thread['id']),
                anchor="w",
                height=44,
                font=font_normal,
                fg_color=theme['accent'] if is_active else theme['bubble_ai'],
                text_color=theme['bg_primary'] if is_active else theme['text_primary'],
                hover_color=theme['accent_alt'] if is_active else theme['bubble_user'],
                corner_radius=22,
                border_width=0
            )
            button.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=0)
            menu_button = ctk.CTkButton(
                button_frame,
                text="⋮",
                command=lambda: self._show_thread_menu(thread),
                width=36,
                height=36,
                font=font_normal,
                fg_color=theme['bubble_ai'],
                text_color=theme['text_secondary'],
                hover_color=theme['bubble_user'],
                corner_radius=18,
                border_width=0
            )
            menu_button.grid(row=0, column=1, padx=(0, 0), pady=0)
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
