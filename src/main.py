"""
Main entry point for the Jeeves AI Assistant.
"""

import customtkinter as ctk

from .gui.app import JeevesApp

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
ctk.deactivate_automatic_dpi_awareness()


def launch_app():
    """Launch the Jeeves AI Assistant application."""
    root = ctk.CTk()
    app = JeevesApp(root)  # noqa: F841

    return root


if __name__ == "__main__":
    root = launch_app()
    root.mainloop()
