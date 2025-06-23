import logging
from typing import (
    Any,
    Callable,
    Optional,
    TypedDict,
)

import customtkinter as ctk

from ..config.settings import APP_SETTINGS as _APP_SETTINGS_RAW
from ..config.settings import COLORS as _COLORS_RAW


class FontSizes(TypedDict):
    large: int
    normal: int


class AppSettingsType(TypedDict):
    font_family: str
    font_sizes: FontSizes


class ColorsTheme(TypedDict):
    bg_sidebar: str
    accent_primary: str
    button_primary: str
    text_inverse: str
    button_primary_hover: str
    border_divider: str
    thread_general: str
    thread_code: str
    thread_planning: str
    thread_creative: str
    thread_support: str
    thread_docs: str
    button_secondary: str
    text_primary: str
    button_secondary_hover: str
    border_focus: str
    border_secondary: str
    text_secondary: str
    error: str
    warning: str
    success: str
    info: str


class ColorsType(TypedDict):
    dark: ColorsTheme


APP_SETTINGS: AppSettingsType = _APP_SETTINGS_RAW  # type: ignore[assignment]
COLORS: ColorsType = _COLORS_RAW  # type: ignore[assignment]


logger = logging.getLogger(__name__)


class Sidebar(ctk.CTkFrame):
    """Sidebar component with thread management."""

    def __init__(
        self,
        parent: Any,
        on_thread_select: Optional[Callable[[int], None]] = None,
        on_new_thread: Optional[Callable[[], None]] = None,
        on_delete_thread: Optional[Callable[[int], None]] = None,
        on_rename_thread: Optional[Callable[[int, str], None]] = None,
    ):
        theme: ColorsTheme = COLORS["dark"]
        font_family: str = APP_SETTINGS["font_family"]
        font_large: tuple[str, int, str] = (
            font_family,
            APP_SETTINGS["font_sizes"]["large"],
            "bold",
        )
        font_normal: tuple[str, int] = (
            font_family,
            APP_SETTINGS["font_sizes"]["normal"],
        )
        super().__init__(parent, width=300, fg_color=theme["bg_sidebar"])

        self.on_thread_select = on_thread_select
        self.on_new_thread = on_new_thread
        self.on_delete_thread = on_delete_thread
        self.on_rename_thread = on_rename_thread

        self.threads: list[dict[str, Any]] = []
        self.current_thread_id: Optional[int] = None

        self._setup_ui(theme, font_large, font_normal)

    def _setup_ui(self, theme: ColorsTheme, font_large: tuple[str, int, str], font_normal: tuple[str, int]) -> None:
        """Setup the user interface."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Give weight to the threads_frame row

        # Sidebar header with enhanced styling and consistent spacing
        self.header_frame = ctk.CTkFrame(self, fg_color=theme["bg_sidebar"], border_width=0, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Conversations",
            font=font_large,
            text_color=theme["accent_primary"],
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=24, pady=24)  # Increased padding

        self.new_thread_button = ctk.CTkButton(
            self.header_frame,
            text="✨ New Chat",  # Added sparkle icon for better visual appeal
            command=self._create_new_thread,
            width=140,  # Increased for better proportions with icon
            height=44,  # Increased for better proportions
            font=(font_normal[0], 12, "bold"),  # Made bold for primary action
            fg_color=theme["button_primary"],
            text_color=theme["text_inverse"],
            hover_color=theme["button_primary_hover"],
            corner_radius=22,  # Increased for modern look
            border_width=0,  # Clean look without borders
        )
        self.new_thread_button.grid(row=0, column=1, padx=(0, 24), pady=16)  # Consistent spacing

        # Add enhanced hover effects to new thread button
        def on_new_button_enter(event: Any) -> None:
            self.new_thread_button.configure(corner_radius=24)

        def on_new_button_leave(event: Any) -> None:
            self.new_thread_button.configure(corner_radius=22)

        self.new_thread_button.bind("<Enter>", on_new_button_enter)
        self.new_thread_button.bind("<Leave>", on_new_button_leave)

        # Add a subtle divider below the header
        self.header_divider = ctk.CTkFrame(self, fg_color=theme["border_divider"], height=1, corner_radius=0)
        self.header_divider.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 0))

        # Threads list with enhanced styling and consistent spacing
        self.threads_frame = ctk.CTkScrollableFrame(self, fg_color=theme["bg_sidebar"], corner_radius=0)
        self.threads_frame.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)  # Updated row to 2
        self.threads_frame.grid_columnconfigure(0, weight=1)
        self.thread_buttons: list[ctk.CTkButton] = []

    def _create_new_thread(self) -> None:
        """Create a new thread."""
        if self.on_new_thread:
            self.on_new_thread()

    def load_threads(self, threads: list[dict[str, Any]]) -> None:
        """Load threads into the sidebar."""
        try:
            self.threads = threads
            self._update_thread_buttons()
        except Exception as e:
            logger.error(f"Error loading threads: {e}")

    def _update_thread_buttons(self) -> None:
        try:
            for button in self.thread_buttons:
                button.destroy()
            self.thread_buttons.clear()
            theme: ColorsTheme = COLORS["dark"]
            font_family: str = APP_SETTINGS["font_family"]
            font_normal: tuple[str, int] = (
                font_family,
                APP_SETTINGS["font_sizes"]["normal"],
            )
            for i, thread in enumerate(self.threads):
                button = self._create_thread_button(thread, i, theme, font_normal)
                if button:
                    self.thread_buttons.append(button)
        except Exception as e:
            logger.error(f"Error updating thread buttons: {e}")

    def _create_thread_button(self, thread: dict[str, Any], index: int, theme: ColorsTheme, font_normal: tuple[str, int]) -> Optional[ctk.CTkButton]:
        try:
            button_frame = ctk.CTkFrame(self.threads_frame, fg_color=theme["bg_sidebar"], corner_radius=0)
            button_frame.grid(row=index, column=0, sticky="ew", pady=8, padx=16)  # Consistent spacing
            button_frame.grid_columnconfigure(0, weight=1)

            is_active: bool = thread["id"] == self.current_thread_id

            # Determine thread color based on type
            thread_type: str = thread.get("type", "general")
            thread_color_map: dict[str, str] = {
                "general": theme.get("thread_general", theme["accent_primary"]),
                "code": theme.get("thread_code", theme["success"]),
                "planning": theme.get("thread_planning", theme["warning"]),
                "creative": theme.get("thread_creative", theme["accent_primary"]),
                "support": theme.get("thread_support", theme["error"]),
                "docs": theme.get("thread_docs", theme["info"]),
            }
            thread_color: str = thread_color_map.get(thread_type, theme["accent_primary"])

            button = ctk.CTkButton(
                button_frame,
                text=f"{thread.get('icon', '💬')} {thread.get('name', 'Unknown')}",
                command=lambda: self._select_thread(thread["id"]),
                anchor="w",
                height=52,  # Increased for better proportions
                font=(
                    font_normal[0],
                    12,
                    "bold" if is_active else "normal",
                ),  # Bold for active thread
                fg_color=thread_color if is_active else theme["button_secondary"],
                text_color=(theme["text_inverse"] if is_active else theme["text_primary"]),
                hover_color=(theme["button_primary_hover"] if is_active else theme["button_secondary_hover"]),
                corner_radius=26,  # Increased for modern look
                border_width=2 if is_active else 1,  # Thicker border for active state
                border_color=(theme["border_focus"] if is_active else theme["border_secondary"]),
            )
            button.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=0)  # Consistent spacing

            menu_button = ctk.CTkButton(
                button_frame,
                text="⋮",
                command=lambda: self._show_thread_menu(thread),
                width=44,  # Increased for better proportions
                height=44,  # Increased for better proportions
                font=(font_normal[0], 14, "bold"),  # Larger, bold font for menu icon
                fg_color=theme["button_secondary"],
                text_color=theme["text_secondary"],
                hover_color=theme["button_secondary_hover"],
                corner_radius=22,  # Increased for modern look
                border_width=1,  # Subtle border for definition
                border_color=theme["border_secondary"],
            )
            menu_button.grid(row=0, column=1, padx=(0, 0), pady=0)
            return button
        except Exception as e:
            logger.error(f"Error creating thread button: {e}")
            return None

    def _select_thread(self, thread_id: int) -> None:
        """Select a thread."""
        if self.on_thread_select:
            self.on_thread_select(thread_id)

    def _show_thread_menu(self, thread: dict[str, Any]) -> None:
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
                font=("Fira Code", 12),
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
                hover_color="#d32f2f",
            )
            delete_button.pack(pady=10)

            cancel_button = ctk.CTkButton(
                menu,
                text="Cancel",
                command=menu.destroy,
                width=180,
                height=30,
                font=("Fira Code", 12),
            )
            cancel_button.pack(pady=10)

        except Exception as e:
            logger.error(f"Error showing thread menu: {e}")

    def _rename_thread(self, thread: dict[str, Any], menu: ctk.CTkToplevel) -> None:
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
            entry.insert(0, thread.get("name", ""))
            entry.pack(pady=10)
            entry.focus_set()

            # Create buttons
            button_frame = ctk.CTkFrame(dialog)
            button_frame.pack(pady=10)

            save_button = ctk.CTkButton(
                button_frame,
                text="Save",
                command=lambda: self._save_rename(thread["id"], entry.get(), dialog),
                width=80,
                height=30,
                font=("Fira Code", 12),
            )
            save_button.pack(side="left", padx=5)

            cancel_button = ctk.CTkButton(
                button_frame,
                text="Cancel",
                command=dialog.destroy,
                width=80,
                height=30,
                font=("Fira Code", 12),
            )
            cancel_button.pack(side="left", padx=5)

            # Bind Enter key
            entry.bind(
                "<Return>",
                lambda e: self._save_rename(thread["id"], entry.get(), dialog),
            )

        except Exception as e:
            logger.error(f"Error renaming thread: {e}")

    def _save_rename(self, thread_id: int, new_name: str, dialog: ctk.CTkToplevel) -> None:
        """Save the renamed thread."""
        try:
            if new_name.strip():
                if self.on_rename_thread:
                    self.on_rename_thread(thread_id, new_name.strip())
            dialog.destroy()
        except Exception as e:
            logger.error(f"Error saving rename: {e}")

    def _delete_thread(self, thread: dict[str, Any], menu: ctk.CTkToplevel) -> None:
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
                font=("Fira Code", 12),
            )
            message.pack(pady=20)

            # Create buttons
            button_frame = ctk.CTkFrame(dialog)
            button_frame.pack(pady=10)

            delete_button = ctk.CTkButton(
                button_frame,
                text="Delete",
                command=lambda: self._confirm_delete(thread["id"], dialog),
                width=80,
                height=30,
                font=("Fira Code", 12),
                fg_color="#f44336",
                hover_color="#d32f2f",
            )
            delete_button.pack(side="left", padx=5)

            cancel_button = ctk.CTkButton(
                button_frame,
                text="Cancel",
                command=dialog.destroy,
                width=80,
                height=30,
                font=("Fira Code", 12),
            )
            cancel_button.pack(side="left", padx=5)

        except Exception as e:
            logger.error(f"Error deleting thread: {e}")

    def _confirm_delete(self, thread_id: int, dialog: ctk.CTkToplevel) -> None:
        """Confirm thread deletion."""
        try:
            if self.on_delete_thread:
                self.on_delete_thread(thread_id)
            dialog.destroy()
        except Exception as e:
            logger.error(f"Error confirming delete: {e}")

    def set_current_thread(self, thread_id: int) -> None:
        """Set the current active thread."""
        self.current_thread_id = thread_id
        self._update_thread_buttons()
