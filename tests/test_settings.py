"""
Tests for the settings module.
"""
import pytest
from src.config.settings import ICONS, COLORS, APP_SETTINGS, AI_PROVIDER_SETTINGS, DEFAULT_THREADS
from src.core.file_handler import JeevesFileHandler
import os


class TestSettings:
    """Test the settings configuration."""

    def test_icons_structure(self):
        """Test that ICONS dictionary has expected structure."""
        assert isinstance(ICONS, dict)
        assert len(ICONS) > 0
        
        # Check for some expected icons
        expected_icons = ['chat', 'send', 'close', 'menu', 'new', 'project']
        for icon_name in expected_icons:
            assert icon_name in ICONS
            assert isinstance(ICONS[icon_name], str)
            assert len(ICONS[icon_name]) > 0

    def test_colors_structure(self):
        """Test that COLORS dictionary has expected structure."""
        assert isinstance(COLORS, dict)
        assert 'dark' in COLORS
        assert 'light' in COLORS
        
        # Test dark theme structure
        dark_colors = COLORS['dark']
        assert isinstance(dark_colors, dict)
        
        # Check for expected color categories
        expected_categories = [
            'bg_primary', 'text_primary', 'border_primary', 
            'accent_primary', 'success', 'error', 'warning'
        ]
        for category in expected_categories:
            assert category in dark_colors
            assert isinstance(dark_colors[category], str)
            assert dark_colors[category].startswith('#')
            assert len(dark_colors[category]) == 7  # Hex color format

    def test_light_theme_structure(self):
        """Test that light theme has expected structure."""
        light_colors = COLORS['light']
        assert isinstance(light_colors, dict)
        
        # Check for expected color categories
        expected_categories = [
            'bg_primary', 'text_primary', 'border_primary', 
            'accent_primary', 'success', 'error', 'warning'
        ]
        for category in expected_categories:
            assert category in light_colors
            assert isinstance(light_colors[category], str)
            assert light_colors[category].startswith('#')
            assert len(light_colors[category]) == 7  # Hex color format

    def test_app_settings_structure(self):
        """Test that APP_SETTINGS has expected structure."""
        assert isinstance(APP_SETTINGS, dict)
        
        # Check required app settings
        assert 'title' in APP_SETTINGS
        assert 'default_width' in APP_SETTINGS
        assert 'default_height' in APP_SETTINGS
        assert 'min_width' in APP_SETTINGS
        assert 'min_height' in APP_SETTINGS
        assert 'sidebar_width' in APP_SETTINGS
        assert 'font_family' in APP_SETTINGS
        assert 'font_sizes' in APP_SETTINGS
        
        # Check data types
        assert isinstance(APP_SETTINGS['title'], str)
        assert isinstance(APP_SETTINGS['default_width'], int)
        assert isinstance(APP_SETTINGS['default_height'], int)
        assert isinstance(APP_SETTINGS['min_width'], int)
        assert isinstance(APP_SETTINGS['min_height'], int)
        assert isinstance(APP_SETTINGS['sidebar_width'], int)
        assert isinstance(APP_SETTINGS['font_family'], str)
        assert isinstance(APP_SETTINGS['font_sizes'], dict)

    def test_font_sizes_structure(self):
        """Test that font_sizes has expected structure."""
        font_sizes = APP_SETTINGS['font_sizes']
        expected_sizes = ['small', 'normal', 'medium', 'large', 'xlarge']
        
        for size_name in expected_sizes:
            assert size_name in font_sizes
            assert isinstance(font_sizes[size_name], int)
            assert font_sizes[size_name] > 0

    def test_ai_provider_settings_structure(self):
        """Test that AI_PROVIDER_SETTINGS has expected structure."""
        assert isinstance(AI_PROVIDER_SETTINGS, dict)
        
        # Check required settings
        assert 'default_provider' in AI_PROVIDER_SETTINGS
        assert 'providers' in AI_PROVIDER_SETTINGS
        assert 'provider_order' in AI_PROVIDER_SETTINGS
        
        # Check data types
        assert isinstance(AI_PROVIDER_SETTINGS['default_provider'], str)
        assert isinstance(AI_PROVIDER_SETTINGS['providers'], dict)
        assert isinstance(AI_PROVIDER_SETTINGS['provider_order'], list)

    def test_providers_configuration(self):
        """Test that providers configuration is valid."""
        providers = AI_PROVIDER_SETTINGS['providers']
        
        # Check for expected providers
        assert 'gemini' in providers
        assert 'placeholder' in providers
        
        # Check gemini provider settings
        gemini_config = providers['gemini']
        assert isinstance(gemini_config, dict)
        assert 'enabled' in gemini_config
        assert 'model' in gemini_config
        assert 'max_output_tokens' in gemini_config
        assert 'temperature' in gemini_config
        assert 'top_p' in gemini_config
        assert 'top_k' in gemini_config
        assert 'api_key_env_var' in gemini_config
        
        # Check data types
        assert isinstance(gemini_config['enabled'], bool)
        assert isinstance(gemini_config['model'], str)
        assert isinstance(gemini_config['max_output_tokens'], int)
        assert isinstance(gemini_config['temperature'], (int, float))
        assert isinstance(gemini_config['top_p'], (int, float))
        assert isinstance(gemini_config['top_k'], int)
        assert isinstance(gemini_config['api_key_env_var'], str)

    def test_placeholder_provider_configuration(self):
        """Test that placeholder provider configuration is valid."""
        providers = AI_PROVIDER_SETTINGS['providers']
        placeholder_config = providers['placeholder']
        
        assert isinstance(placeholder_config, dict)
        assert 'enabled' in placeholder_config
        assert 'fallback' in placeholder_config
        
        # Check data types
        assert isinstance(placeholder_config['enabled'], bool)
        assert isinstance(placeholder_config['fallback'], bool)

    def test_provider_order(self):
        """Test that provider_order is valid."""
        provider_order = AI_PROVIDER_SETTINGS['provider_order']
        providers = AI_PROVIDER_SETTINGS['providers']
        
        assert isinstance(provider_order, list)
        assert len(provider_order) > 0
        
        # Check that all providers in order exist in providers config
        for provider_name in provider_order:
            assert provider_name in providers

    def test_default_threads_structure(self):
        """Test that DEFAULT_THREADS has expected structure."""
        assert isinstance(DEFAULT_THREADS, list)
        assert len(DEFAULT_THREADS) > 0
        
        for thread_tuple in DEFAULT_THREADS:
            assert isinstance(thread_tuple, tuple)
            assert len(thread_tuple) == 2
            assert isinstance(thread_tuple[0], str)  # thread type
            assert isinstance(thread_tuple[1], str)  # thread name

    def test_color_consistency(self):
        """Test that both themes have the same color categories."""
        dark_colors = COLORS['dark']
        light_colors = COLORS['light']
        
        # Check that both themes have the same keys
        assert set(dark_colors.keys()) == set(light_colors.keys())
        
        # Check that all colors are valid hex format
        for theme_colors in [dark_colors, light_colors]:
            for color_name, color_value in theme_colors.items():
                assert isinstance(color_value, str)
                assert color_value.startswith('#')
                assert len(color_value) == 7
                # Check that it's a valid hex color
                assert all(c in '0123456789abcdefABCDEF' for c in color_value[1:])

    def test_app_settings_validation(self):
        """Test that app settings have valid values."""
        # Check window dimensions
        assert APP_SETTINGS['default_width'] >= APP_SETTINGS['min_width']
        assert APP_SETTINGS['default_height'] >= APP_SETTINGS['min_height']
        assert APP_SETTINGS['min_width'] > 0
        assert APP_SETTINGS['min_height'] > 0
        assert APP_SETTINGS['sidebar_width'] > 0
        
        # Check font sizes are in ascending order
        font_sizes = APP_SETTINGS['font_sizes']
        size_values = list(font_sizes.values())
        assert size_values == sorted(size_values)

    def test_ai_settings_validation(self):
        """Test that AI provider settings have valid values."""
        providers = AI_PROVIDER_SETTINGS['providers']
        gemini_config = providers['gemini']
        
        # Check parameter ranges
        assert 0 <= gemini_config['temperature'] <= 2
        assert 0 <= gemini_config['top_p'] <= 1
        assert gemini_config['top_k'] > 0
        assert gemini_config['max_output_tokens'] > 0
        
        # Check that default provider exists
        default_provider = AI_PROVIDER_SETTINGS['default_provider']
        assert default_provider in providers
        assert providers[default_provider]['enabled'] is True


def test_sandbox_directory_setting():
    """Test that sandbox directory is configured in settings."""
    assert 'sandbox_directory' in APP_SETTINGS
    assert APP_SETTINGS['sandbox_directory'] == '~/.jeeves'


def test_file_handler_uses_setting():
    """Test that JeevesFileHandler uses the setting from config."""
    file_handler = JeevesFileHandler()
    sandbox_root = file_handler.get_sandbox_root()
    
    # The sandbox root should be the expanded version of the setting
    expected_path = os.path.expanduser(APP_SETTINGS['sandbox_directory'])
    assert os.path.normpath(sandbox_root) == os.path.normpath(expected_path)


def test_file_handler_custom_directory():
    """Test that JeevesFileHandler can use a custom directory."""
    custom_dir = "/tmp/test_sandbox"
    file_handler = JeevesFileHandler(custom_dir)
    sandbox_root = file_handler.get_sandbox_root()

    assert os.path.abspath(os.path.normpath(sandbox_root)) == os.path.abspath(os.path.normpath(custom_dir)) 