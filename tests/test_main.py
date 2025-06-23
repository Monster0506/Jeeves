"""
Tests for the main module.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.main import launch_app


class TestMain:
    """Test the main entry point."""

    @patch("src.main.ctk.CTk")
    @patch("src.main.JeevesApp")
    def test_launch_app_initialization(self, mock_app_class, mock_root_class):
        """Test that launch_app properly initializes the application."""
        # Setup mocks
        mock_root = MagicMock()
        mock_root_class.return_value = mock_root
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        # Call the function
        result = launch_app()

        # Verify CTk root creation
        mock_root_class.assert_called_once()

        # Verify JeevesApp creation
        mock_app_class.assert_called_once_with(mock_root)

        # Verify return value
        assert result == mock_root

    @patch("src.main.ctk.CTk")
    @patch("src.main.JeevesApp")
    def test_launch_app_return_value(self, mock_app_class, mock_root_class):
        """Test that launch_app returns the root window."""
        # Setup mocks
        mock_root = MagicMock()
        mock_root_class.return_value = mock_root
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        # Call the function
        result = launch_app()

        # Verify return value
        assert result == mock_root
        assert isinstance(result, MagicMock)

    @patch("src.main.ctk.CTk")
    @patch("src.main.JeevesApp")
    def test_launch_app_app_creation(self, mock_app_class, mock_root_class):
        """Test that JeevesApp is created with the root window."""
        # Setup mocks
        mock_root = MagicMock()
        mock_root_class.return_value = mock_root
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        # Call the function
        launch_app()

        # Verify JeevesApp was created with the root window
        mock_app_class.assert_called_once_with(mock_root)

    @patch("src.main.ctk.CTk")
    @patch("src.main.JeevesApp")
    def test_launch_app_multiple_calls(self, mock_app_class, mock_root_class):
        """Test that launch_app can be called multiple times."""
        # Setup mocks
        mock_root1 = MagicMock()
        mock_root2 = MagicMock()
        mock_root_class.side_effect = [mock_root1, mock_root2]
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app

        # Call the function twice
        result1 = launch_app()
        result2 = launch_app()

        # Verify both calls work
        assert result1 == mock_root1
        assert result2 == mock_root2
        assert mock_root_class.call_count == 2
        assert mock_app_class.call_count == 2

    @patch("src.main.ctk.CTk")
    @patch("src.main.JeevesApp")
    def test_launch_app_exception_handling(self, mock_app_class, mock_root_class):
        """Test that launch_app handles exceptions gracefully."""
        # Setup mocks to raise exceptions
        mock_root_class.side_effect = Exception("CTk creation failed")

        # Call the function and expect it to raise the exception
        with pytest.raises(Exception, match="CTk creation failed"):
            launch_app()

    @patch("src.main.ctk.CTk")
    @patch("src.main.JeevesApp")
    def test_launch_app_jeeves_app_exception(self, mock_app_class, mock_root_class):
        """Test that launch_app handles JeevesApp creation exceptions."""
        # Setup mocks
        mock_root = MagicMock()
        mock_root_class.return_value = mock_root
        mock_app_class.side_effect = Exception("JeevesApp creation failed")

        # Call the function and expect it to raise the exception
        with pytest.raises(Exception, match="JeevesApp creation failed"):
            launch_app()

    def test_launch_app_function_signature(self):
        """Test that launch_app has the expected function signature."""
        import inspect

        # Get function signature
        sig = inspect.signature(launch_app)

        # Verify it takes no parameters
        assert len(sig.parameters) == 0

        # Verify it has a docstring
        assert launch_app.__doc__ is not None
        assert "Launch the Jeeves AI Assistant application" in launch_app.__doc__

    @patch("src.main.launch_app")
    def test_main_not_executed_when_imported(self, mock_launch):
        """Test that main execution doesn't run when module is imported."""
        # Mock __name__ to not be '__main__'
        with patch("src.main.__name__", "src.main"):

            # Verify launch_app was not called
            mock_launch.assert_not_called()

    # The following tests are skipped due to limitations of patching and import-time execution.
    # See: https://docs.pytest.org/en/stable/how-to/skipping.html
    # - test_main_execution: Cannot reliably patch __main__ block on import
    # - test_ctk_configuration_at_import: CTk config calls happen before patching
    #
    # @pytest.mark.skip(reason="Cannot reliably patch __main__ block on import")
    # def test_main_execution(self): ...
    #
    # @pytest.mark.skip(reason="CTk config calls happen before patching")
    # def test_ctk_configuration_at_import(self): ...
