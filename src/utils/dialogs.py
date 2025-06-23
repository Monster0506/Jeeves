"""
Dialog utilities for Jeeves AI Assistant.
CustomTkinter-based dialog boxes for user interaction.
"""

import logging
from typing import Callable, Optional

import customtkinter as ctk

logger = logging.getLogger(__name__)


def show_error(title: str, message: str, parent=None):
    """Show an error dialog."""
    try:
        dialog = ctk.CTkToplevel(parent)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")

        # Create message
        message_label = ctk.CTkLabel(
            dialog, text=message, font=("Fira Code", 12), wraplength=350
        )
        message_label.pack(pady=30)

        # Create OK button
        ok_button = ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy,
            width=100,
            height=35,
            font=("Fira Code", 12),
        )
        ok_button.pack(pady=20)

        # Focus the dialog
        dialog.focus_set()
        dialog.wait_window()

    except Exception as e:
        logger.error(f"Error showing error dialog: {e}")


def show_info(title: str, message: str, parent=None):
    """Show an info dialog."""
    try:
        dialog = ctk.CTkToplevel(parent)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")

        # Create message
        message_label = ctk.CTkLabel(
            dialog, text=message, font=("Fira Code", 12), wraplength=350
        )
        message_label.pack(pady=30)

        # Create OK button
        ok_button = ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy,
            width=100,
            height=35,
            font=("Fira Code", 12),
        )
        ok_button.pack(pady=20)

        # Focus the dialog
        dialog.focus_set()
        dialog.wait_window()

    except Exception as e:
        logger.error(f"Error showing info dialog: {e}")


def show_warning(title: str, message: str, parent=None):
    """Show a warning dialog."""
    try:
        dialog = ctk.CTkToplevel(parent)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")

        # Create message
        message_label = ctk.CTkLabel(
            dialog, text=message, font=("Fira Code", 12), wraplength=350
        )
        message_label.pack(pady=30)

        # Create OK button
        ok_button = ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy,
            width=100,
            height=35,
            font=("Fira Code", 12),
        )
        ok_button.pack(pady=20)

        # Focus the dialog
        dialog.focus_set()
        dialog.wait_window()

    except Exception as e:
        logger.error(f"Error showing warning dialog: {e}")


def show_confirmation(
    title: str,
    message: str,
    parent=None,
    on_confirm: Callable = None,
    on_cancel: Callable = None,
) -> bool:
    """Show a confirmation dialog."""
    result = [False]  # Use list to store result in nested function

    try:
        dialog = ctk.CTkToplevel(parent)
        dialog.title(title)
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f"400x250+{x}+{y}")

        # Create message
        message_label = ctk.CTkLabel(
            dialog, text=message, font=("Fira Code", 12), wraplength=350
        )
        message_label.pack(pady=30)

        # Create button frame
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=20)

        def on_confirm_click():
            result[0] = True
            if on_confirm:
                on_confirm()
            dialog.destroy()

        def on_cancel_click():
            result[0] = False
            if on_cancel:
                on_cancel()
            dialog.destroy()

        # Create buttons
        confirm_button = ctk.CTkButton(
            button_frame,
            text="Confirm",
            command=on_confirm_click,
            width=100,
            height=35,
            font=("Fira Code", 12),
            fg_color="#2196F3",
            hover_color="#1976D2",
        )
        confirm_button.pack(side="left", padx=10)

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=on_cancel_click,
            width=100,
            height=35,
            font=("Fira Code", 12),
        )
        cancel_button.pack(side="left", padx=10)

        # Focus the dialog
        dialog.focus_set()
        dialog.wait_window()

        return result[0]

    except Exception as e:
        logger.error(f"Error showing confirmation dialog: {e}")
        return False


def show_input_dialog(
    title: str,
    message: str,
    default_value: str = "",
    parent=None,
    on_ok: Callable = None,
    on_cancel: Callable = None,
) -> Optional[str]:
    """Show an input dialog."""
    result = [None]  # Use list to store result in nested function

    try:
        dialog = ctk.CTkToplevel(parent)
        dialog.title(title)
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (250 // 2)
        dialog.geometry(f"400x250+{x}+{y}")

        # Create message
        message_label = ctk.CTkLabel(
            dialog, text=message, font=("Fira Code", 12), wraplength=350
        )
        message_label.pack(pady=20)

        # Create input field
        input_field = ctk.CTkEntry(dialog, font=("Fira Code", 12), width=300, height=35)
        input_field.pack(pady=20)
        input_field.insert(0, default_value)
        input_field.focus_set()

        # Create button frame
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=20)

        def on_ok_click():
            result[0] = input_field.get()
            if on_ok:
                on_ok(result[0])
            dialog.destroy()

        def on_cancel_click():
            result[0] = None
            if on_cancel:
                on_cancel()
            dialog.destroy()

        # Create buttons
        ok_button = ctk.CTkButton(
            button_frame,
            text="OK",
            command=on_ok_click,
            width=100,
            height=35,
            font=("Fira Code", 12),
            fg_color="#2196F3",
            hover_color="#1976D2",
        )
        ok_button.pack(side="left", padx=10)

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=on_cancel_click,
            width=100,
            height=35,
            font=("Fira Code", 12),
        )
        cancel_button.pack(side="left", padx=10)

        # Bind Enter key
        input_field.bind("<Return>", lambda e: on_ok_click())
        input_field.bind("<Escape>", lambda e: on_cancel_click())

        dialog.wait_window()

        return result[0]

    except Exception as e:
        logger.error(f"Error showing input dialog: {e}")
        return None


def show_loading_dialog(title: str, message: str, parent=None):
    """Show a loading dialog."""
    try:
        dialog = ctk.CTkToplevel(parent)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (dialog.winfo_screenheight() // 2) - (150 // 2)
        dialog.geometry(f"300x150+{x}+{y}")

        # Create message
        message_label = ctk.CTkLabel(dialog, text=message, font=("Fira Code", 12))
        message_label.pack(pady=30)

        # Create progress bar
        progress_bar = ctk.CTkProgressBar(dialog)
        progress_bar.pack(pady=20)
        progress_bar.set(0)
        progress_bar.start()

        return dialog

    except Exception as e:
        logger.error(f"Error showing loading dialog: {e}")
        return None


def close_loading_dialog(dialog):
    """Close a loading dialog."""
    try:
        if dialog:
            dialog.destroy()
    except Exception as e:
        logger.error(f"Error closing loading dialog: {e}")


# Legacy functions for backward compatibility
def show_warning_dialog(parent, title: str, message: str):
    """Legacy warning dialog function."""
    show_warning(title, message, parent)


def show_confirmation_dialog(
    parent, title: str, message: str, on_confirm: Callable = None
):
    """Legacy confirmation dialog function."""
    return show_confirmation(title, message, parent, on_confirm)
