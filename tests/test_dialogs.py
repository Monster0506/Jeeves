"""
Tests for the dialogs module.
"""

import pytest
from unittest.mock import patch, MagicMock, call
from src.utils.dialogs import (
    show_error,
    show_info,
    show_warning,
    show_confirmation,
    show_input_dialog,
    show_loading_dialog,
    close_loading_dialog,
    show_warning_dialog,
    show_confirmation_dialog,
)


class TestDialogs:
    """Test the dialog utilities."""

    @patch("src.utils.dialogs.ctk.CTkToplevel")
    @patch("src.utils.dialogs.ctk.CTkLabel")
    @patch("src.utils.dialogs.ctk.CTkButton")
    def test_show_error_dialog(self, mock_button, mock_label, mock_toplevel):
        """Test show_error dialog creation."""
        # Setup mocks
        mock_dialog = MagicMock()
        mock_toplevel.return_value = mock_dialog
        mock_dialog.winfo_screenwidth.return_value = 1920
        mock_dialog.winfo_screenheight.return_value = 1080

        mock_label_instance = MagicMock()
        mock_label.return_value = mock_label_instance

        mock_button_instance = MagicMock()
        mock_button.return_value = mock_button_instance

        # Call the function
        show_error("Test Error", "This is a test error message")

        # Verify dialog creation
        mock_toplevel.assert_called_once()
        mock_dialog.title.assert_called_once_with("Test Error")
        mock_dialog.geometry.assert_called()
        mock_dialog.resizable.assert_called_once_with(False, False)
        mock_dialog.transient.assert_called_once_with(None)
        mock_dialog.grab_set.assert_called_once()

        # Verify label creation
        mock_label.assert_called_once()
        mock_label_instance.pack.assert_called_once_with(pady=30)

        # Verify button creation
        mock_button.assert_called_once()
        mock_button_instance.pack.assert_called_once_with(pady=20)

        # Verify dialog focus and wait
        mock_dialog.focus_set.assert_called_once()
        mock_dialog.wait_window.assert_called_once()

    @patch("src.utils.dialogs.ctk.CTkToplevel")
    @patch("src.utils.dialogs.ctk.CTkLabel")
    @patch("src.utils.dialogs.ctk.CTkButton")
    def test_show_info_dialog(self, mock_button, mock_label, mock_toplevel):
        """Test show_info dialog creation."""
        # Setup mocks
        mock_dialog = MagicMock()
        mock_toplevel.return_value = mock_dialog
        mock_dialog.winfo_screenwidth.return_value = 1920
        mock_dialog.winfo_screenheight.return_value = 1080

        mock_label_instance = MagicMock()
        mock_label.return_value = mock_label_instance

        mock_button_instance = MagicMock()
        mock_button.return_value = mock_button_instance

        # Call the function
        show_info("Test Info", "This is a test info message")

        # Verify dialog creation
        mock_toplevel.assert_called_once()
        mock_dialog.title.assert_called_once_with("Test Info")
        mock_dialog.geometry.assert_called()
        mock_dialog.resizable.assert_called_once_with(False, False)
        mock_dialog.transient.assert_called_once_with(None)
        mock_dialog.grab_set.assert_called_once()

        # Verify label creation
        mock_label.assert_called_once()
        mock_label_instance.pack.assert_called_once_with(pady=30)

        # Verify button creation
        mock_button.assert_called_once()
        mock_button_instance.pack.assert_called_once_with(pady=20)

        # Verify dialog focus and wait
        mock_dialog.focus_set.assert_called_once()
        mock_dialog.wait_window.assert_called_once()

    @patch("src.utils.dialogs.ctk.CTkToplevel")
    @patch("src.utils.dialogs.ctk.CTkLabel")
    @patch("src.utils.dialogs.ctk.CTkButton")
    def test_show_warning_dialog(self, mock_button, mock_label, mock_toplevel):
        """Test show_warning dialog creation."""
        # Setup mocks
        mock_dialog = MagicMock()
        mock_toplevel.return_value = mock_dialog
        mock_dialog.winfo_screenwidth.return_value = 1920
        mock_dialog.winfo_screenheight.return_value = 1080

        mock_label_instance = MagicMock()
        mock_label.return_value = mock_label_instance

        mock_button_instance = MagicMock()
        mock_button.return_value = mock_button_instance

        # Call the function
        show_warning("Test Warning", "This is a test warning message")

        # Verify dialog creation
        mock_toplevel.assert_called_once()
        mock_dialog.title.assert_called_once_with("Test Warning")
        mock_dialog.geometry.assert_called()
        mock_dialog.resizable.assert_called_once_with(False, False)
        mock_dialog.transient.assert_called_once_with(None)
        mock_dialog.grab_set.assert_called_once()

        # Verify label creation
        mock_label.assert_called_once()
        mock_label_instance.pack.assert_called_once_with(pady=30)

        # Verify button creation
        mock_button.assert_called_once()
        mock_button_instance.pack.assert_called_once_with(pady=20)

        # Verify dialog focus and wait
        mock_dialog.focus_set.assert_called_once()
        mock_dialog.wait_window.assert_called_once()

    @patch("src.utils.dialogs.ctk.CTkToplevel")
    @patch("src.utils.dialogs.ctk.CTkLabel")
    @patch("src.utils.dialogs.ctk.CTkFrame")
    @patch("src.utils.dialogs.ctk.CTkButton")
    def test_show_confirmation_dialog(
        self, mock_button, mock_frame, mock_label, mock_toplevel
    ):
        """Test show_confirmation dialog creation."""
        # Setup mocks
        mock_dialog = MagicMock()
        mock_toplevel.return_value = mock_dialog
        mock_dialog.winfo_screenwidth.return_value = 1920
        mock_dialog.winfo_screenheight.return_value = 1080

        mock_label_instance = MagicMock()
        mock_label.return_value = mock_label_instance

        mock_frame_instance = MagicMock()
        mock_frame.return_value = mock_frame_instance

        mock_button_instance = MagicMock()
        mock_button.return_value = mock_button_instance

        # Call the function
        result = show_confirmation(
            "Test Confirm", "This is a test confirmation message"
        )

        # Verify dialog creation
        mock_toplevel.assert_called_once()
        mock_dialog.title.assert_called_once_with("Test Confirm")
        mock_dialog.geometry.assert_called()
        mock_dialog.resizable.assert_called_once_with(False, False)
        mock_dialog.transient.assert_called_once_with(None)
        mock_dialog.grab_set.assert_called_once()

        # Verify label creation
        mock_label.assert_called_once()
        mock_label_instance.pack.assert_called_once_with(pady=30)

        # Verify frame creation
        mock_frame.assert_called_once()
        mock_frame_instance.pack.assert_called_once_with(pady=20)

        # Verify button creation (should be called twice for confirm and cancel)
        assert mock_button.call_count == 2

        # Verify dialog focus and wait
        mock_dialog.focus_set.assert_called_once()
        mock_dialog.wait_window.assert_called_once()

        # Verify return value (should be False by default since no button was clicked)
        assert result is False

    @patch("src.utils.dialogs.ctk.CTkToplevel")
    @patch("src.utils.dialogs.ctk.CTkLabel")
    @patch("src.utils.dialogs.ctk.CTkEntry")
    @patch("src.utils.dialogs.ctk.CTkFrame")
    @patch("src.utils.dialogs.ctk.CTkButton")
    def test_show_input_dialog(
        self, mock_button, mock_frame, mock_entry, mock_label, mock_toplevel
    ):
        """Test show_input_dialog creation."""
        # Setup mocks
        mock_dialog = MagicMock()
        mock_toplevel.return_value = mock_dialog
        mock_dialog.winfo_screenwidth.return_value = 1920
        mock_dialog.winfo_screenheight.return_value = 1080

        mock_label_instance = MagicMock()
        mock_label.return_value = mock_label_instance

        mock_entry_instance = MagicMock()
        mock_entry.return_value = mock_entry_instance
        mock_entry_instance.get.return_value = "test input"

        mock_frame_instance = MagicMock()
        mock_frame.return_value = mock_frame_instance

        mock_button_instance = MagicMock()
        mock_button.return_value = mock_button_instance

        # Call the function
        result = show_input_dialog(
            "Test Input", "Please enter some text:", "default value"
        )

        # Verify dialog creation
        mock_toplevel.assert_called_once()
        mock_dialog.title.assert_called_once_with("Test Input")
        mock_dialog.geometry.assert_called()
        mock_dialog.resizable.assert_called_once_with(False, False)
        mock_dialog.transient.assert_called_once_with(None)
        mock_dialog.grab_set.assert_called_once()

        # Verify label creation
        mock_label.assert_called_once()
        mock_label_instance.pack.assert_called_once_with(pady=20)

        # Verify entry creation
        mock_entry.assert_called_once()
        mock_entry_instance.pack.assert_called_once_with(pady=20)

        # Verify frame creation
        mock_frame.assert_called_once()
        mock_frame_instance.pack.assert_called_once_with(pady=20)

        # Verify button creation (should be called twice for OK and Cancel)
        assert mock_button.call_count == 2

        # Verify dialog wait
        mock_dialog.wait_window.assert_called_once()

        # Verify return value (should be None by default since no button was clicked)
        assert result is None

    @patch("src.utils.dialogs.ctk.CTkToplevel")
    @patch("src.utils.dialogs.ctk.CTkLabel")
    @patch("src.utils.dialogs.ctk.CTkProgressBar")
    def test_show_loading_dialog(self, mock_progress, mock_label, mock_toplevel):
        """Test show_loading_dialog creation."""
        # Setup mocks
        mock_dialog = MagicMock()
        mock_toplevel.return_value = mock_dialog
        mock_dialog.winfo_screenwidth.return_value = 1920
        mock_dialog.winfo_screenheight.return_value = 1080

        mock_label_instance = MagicMock()
        mock_label.return_value = mock_label_instance

        mock_progress_instance = MagicMock()
        mock_progress.return_value = mock_progress_instance

        # Call the function
        result = show_loading_dialog("Test Loading", "Please wait...")

        # Verify dialog creation
        mock_toplevel.assert_called_once()
        mock_dialog.title.assert_called_once_with("Test Loading")
        mock_dialog.geometry.assert_called()
        mock_dialog.resizable.assert_called_once_with(False, False)
        mock_dialog.transient.assert_called_once_with(None)
        mock_dialog.grab_set.assert_called_once()

        # Verify label creation
        mock_label.assert_called_once()
        mock_label_instance.pack.assert_called_once_with(pady=30)

        # Verify progress bar creation
        mock_progress.assert_called_once()
        mock_progress_instance.pack.assert_called_once_with(pady=20)

        # Verify return value
        assert result == mock_dialog

    def test_close_loading_dialog(self):
        """Test close_loading_dialog."""
        # Setup mock dialog
        mock_dialog = MagicMock()

        # Call the function
        close_loading_dialog(mock_dialog)

        # Verify dialog is destroyed
        mock_dialog.destroy.assert_called_once()

    @patch("src.utils.dialogs.show_warning")
    def test_show_warning_dialog_wrapper(self, mock_show_warning):
        """Test show_warning_dialog wrapper function."""
        # Setup mock parent
        mock_parent = MagicMock()

        # Call the function
        show_warning_dialog(mock_parent, "Test Warning", "This is a test warning")

        # Verify show_warning was called with correct parameters
        mock_show_warning.assert_called_once_with(
            "Test Warning", "This is a test warning", mock_parent
        )

    @patch("src.utils.dialogs.show_confirmation")
    def test_show_confirmation_dialog_wrapper(self, mock_show_confirmation):
        """Test show_confirmation_dialog wrapper function."""
        # Setup mock parent and callback
        mock_parent = MagicMock()
        mock_callback = MagicMock()

        # Call the function
        show_confirmation_dialog(
            mock_parent, "Test Confirm", "This is a test confirmation", mock_callback
        )

        # Verify show_confirmation was called with correct parameters
        mock_show_confirmation.assert_called_once_with(
            "Test Confirm", "This is a test confirmation", mock_parent, mock_callback
        )

    @patch("src.utils.dialogs.logger")
    @patch("src.utils.dialogs.ctk.CTkToplevel")
    def test_show_error_dialog_exception_handling(self, mock_toplevel, mock_logger):
        """Test show_error dialog exception handling."""
        # Setup mock to raise exception
        mock_toplevel.side_effect = Exception("Dialog creation failed")

        # Call the function
        show_error("Test Error", "This is a test error message")

        # Verify error was logged
        mock_logger.error.assert_called_once()
        assert "Error showing error dialog" in mock_logger.error.call_args[0][0]

    @patch("src.utils.dialogs.logger")
    @patch("src.utils.dialogs.ctk.CTkToplevel")
    def test_show_info_dialog_exception_handling(self, mock_toplevel, mock_logger):
        """Test show_info dialog exception handling."""
        # Setup mock to raise exception
        mock_toplevel.side_effect = Exception("Dialog creation failed")

        # Call the function
        show_info("Test Info", "This is a test info message")

        # Verify error was logged
        mock_logger.error.assert_called_once()
        assert "Error showing info dialog" in mock_logger.error.call_args[0][0]

    @patch("src.utils.dialogs.logger")
    @patch("src.utils.dialogs.ctk.CTkToplevel")
    def test_show_warning_dialog_exception_handling(self, mock_toplevel, mock_logger):
        """Test show_warning dialog exception handling."""
        # Setup mock to raise exception
        mock_toplevel.side_effect = Exception("Dialog creation failed")

        # Call the function
        show_warning("Test Warning", "This is a test warning message")

        # Verify error was logged
        mock_logger.error.assert_called_once()
        assert "Error showing warning dialog" in mock_logger.error.call_args[0][0]

    @patch("src.utils.dialogs.ctk.CTkToplevel")
    @patch("src.utils.dialogs.ctk.CTkLabel")
    @patch("src.utils.dialogs.ctk.CTkFrame")
    @patch("src.utils.dialogs.ctk.CTkButton")
    def test_show_confirmation_with_callbacks(
        self, mock_button, mock_frame, mock_label, mock_toplevel
    ):
        """Test show_confirmation with callback functions."""
        # Setup mocks
        mock_dialog = MagicMock()
        mock_toplevel.return_value = mock_dialog
        mock_dialog.winfo_screenwidth.return_value = 1920
        mock_dialog.winfo_screenheight.return_value = 1080

        mock_label_instance = MagicMock()
        mock_label.return_value = mock_label_instance

        mock_frame_instance = MagicMock()
        mock_frame.return_value = mock_frame_instance

        mock_button_instance = MagicMock()
        mock_button.return_value = mock_button_instance

        # Setup callbacks
        confirm_callback = MagicMock()
        cancel_callback = MagicMock()

        # Call the function
        result = show_confirmation(
            "Test Confirm",
            "This is a test confirmation message",
            on_confirm=confirm_callback,
            on_cancel=cancel_callback,
        )

        # Verify callbacks were not called yet (no button clicked)
        confirm_callback.assert_not_called()
        cancel_callback.assert_not_called()

        # Verify return value
        assert result is False

    @patch("src.utils.dialogs.ctk.CTkToplevel")
    @patch("src.utils.dialogs.ctk.CTkLabel")
    @patch("src.utils.dialogs.ctk.CTkEntry")
    @patch("src.utils.dialogs.ctk.CTkFrame")
    @patch("src.utils.dialogs.ctk.CTkButton")
    def test_show_input_dialog_with_callbacks(
        self, mock_button, mock_frame, mock_entry, mock_label, mock_toplevel
    ):
        """Test show_input_dialog with callback functions."""
        # Setup mocks
        mock_dialog = MagicMock()
        mock_toplevel.return_value = mock_dialog
        mock_dialog.winfo_screenwidth.return_value = 1920
        mock_dialog.winfo_screenheight.return_value = 1080

        mock_label_instance = MagicMock()
        mock_label.return_value = mock_label_instance

        mock_entry_instance = MagicMock()
        mock_entry.return_value = mock_entry_instance
        mock_entry_instance.get.return_value = "test input"

        mock_frame_instance = MagicMock()
        mock_frame.return_value = mock_frame_instance

        mock_button_instance = MagicMock()
        mock_button.return_value = mock_button_instance

        # Setup callbacks
        ok_callback = MagicMock()
        cancel_callback = MagicMock()

        # Call the function
        result = show_input_dialog(
            "Test Input",
            "Please enter some text:",
            "default value",
            on_ok=ok_callback,
            on_cancel=cancel_callback,
        )

        # Verify callbacks were not called yet (no button clicked)
        ok_callback.assert_not_called()
        cancel_callback.assert_not_called()

        # Verify return value
        assert result is None

    def test_dialog_functions_have_docstrings(self):
        """Test that all dialog functions have docstrings."""
        functions = [
            show_error,
            show_info,
            show_warning,
            show_confirmation,
            show_input_dialog,
            show_loading_dialog,
            close_loading_dialog,
            show_warning_dialog,
            show_confirmation_dialog,
        ]

        for func in functions:
            assert func.__doc__ is not None
            assert len(func.__doc__.strip()) > 0

    def test_close_loading_dialog_with_none(self):
        """Test close_loading_dialog with None parameter."""
        # Should not raise an error when called with None
        close_loading_dialog(None)

    def test_show_warning_dialog_wrapper_with_none_parent(self):
        """Test show_warning_dialog wrapper with None parent."""
        with patch("src.utils.dialogs.show_warning") as mock_show_warning:
            show_warning_dialog(None, "Test Warning", "This is a test warning")
            mock_show_warning.assert_called_once_with(
                "Test Warning", "This is a test warning", None
            )

    def test_show_confirmation_dialog_wrapper_with_none_parent(self):
        """Test show_confirmation_dialog wrapper with None parent."""
        with patch("src.utils.dialogs.show_confirmation") as mock_show_confirmation:
            mock_show_confirmation.return_value = False
            result = show_confirmation_dialog(
                None, "Test Confirm", "This is a test confirmation"
            )
            mock_show_confirmation.assert_called_once_with(
                "Test Confirm", "This is a test confirmation", None, None
            )
            assert result is False

    def test_show_confirmation_dialog_wrapper_with_callback(self):
        """Test show_confirmation_dialog wrapper with callback."""
        with patch("src.utils.dialogs.show_confirmation") as mock_show_confirmation:
            mock_show_confirmation.return_value = False
            mock_callback = MagicMock()
            result = show_confirmation_dialog(
                None, "Test Confirm", "This is a test confirmation", mock_callback
            )
            mock_show_confirmation.assert_called_once_with(
                "Test Confirm", "This is a test confirmation", None, mock_callback
            )
            assert result is False

    def test_dialogs_module_import(self):
        """Test that the dialogs module can be imported and functions exist."""
        # This test ensures the module is imported for coverage
        import src.utils.dialogs as dialogs

        # Verify all expected functions exist
        assert hasattr(dialogs, "show_error")
        assert hasattr(dialogs, "show_info")
        assert hasattr(dialogs, "show_warning")
        assert hasattr(dialogs, "show_confirmation")
        assert hasattr(dialogs, "show_input_dialog")
        assert hasattr(dialogs, "show_loading_dialog")
        assert hasattr(dialogs, "close_loading_dialog")
        assert hasattr(dialogs, "show_warning_dialog")
        assert hasattr(dialogs, "show_confirmation_dialog")

        # Verify they are callable
        assert callable(dialogs.show_error)
        assert callable(dialogs.show_info)
        assert callable(dialogs.show_warning)
        assert callable(dialogs.show_confirmation)
        assert callable(dialogs.show_input_dialog)
        assert callable(dialogs.show_loading_dialog)
        assert callable(dialogs.close_loading_dialog)
        assert callable(dialogs.show_warning_dialog)
        assert callable(dialogs.show_confirmation_dialog)
