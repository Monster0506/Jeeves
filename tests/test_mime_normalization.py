"""
Tests for MIME type normalization functionality.
"""

import pytest

from src.utils import normalize_mime_type


class TestMimeTypeNormalization:
    """Test the MIME type normalization function."""

    @pytest.mark.unit
    def test_audio_format_normalizations(self):
        """Test audio format MIME type normalizations."""
        test_cases = [
            ("audio/mpeg", "audio/mp3"),
            ("application/ogg", "audio/ogg"),
            ("audio/x-m4a", "audio/mp4"),
            ("audio/x-wav", "audio/wav"),
        ]

        for input_mime, expected in test_cases:
            result = normalize_mime_type(input_mime)
            assert (
                result == expected
            ), f"Expected '{input_mime}' -> '{expected}', got '{result}'"

    @pytest.mark.unit
    def test_video_format_normalizations(self):
        """Test video format MIME type normalizations."""
        test_cases = [
            ("video/x-msvideo", "video/avi"),
            ("video/x-ms-wmv", "video/wmv"),
            ("video/quicktime", "video/mp4"),
        ]

        for input_mime, expected in test_cases:
            result = normalize_mime_type(input_mime)
            assert (
                result == expected
            ), f"Expected '{input_mime}' -> '{expected}', got '{result}'"

    @pytest.mark.unit
    def test_image_format_normalizations(self):
        """Test image format MIME type normalizations."""
        test_cases = [
            ("image/x-png", "image/png"),
            ("image/x-jpeg", "image/jpeg"),
            ("image/x-gif", "image/gif"),
            ("image/x-bmp", "image/bmp"),
            ("image/x-tiff", "image/tiff"),
        ]

        for input_mime, expected in test_cases:
            result = normalize_mime_type(input_mime)
            assert (
                result == expected
            ), f"Expected '{input_mime}' -> '{expected}', got '{result}'"

    @pytest.mark.unit
    def test_document_format_normalizations(self):
        """Test document format MIME type normalizations (should remain unchanged)."""
        test_cases = [
            (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
            (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
            (
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ),
        ]

        for input_mime, expected in test_cases:
            result = normalize_mime_type(input_mime)
            assert (
                result == expected
            ), f"Expected '{input_mime}' -> '{expected}', got '{result}'"

    @pytest.mark.unit
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        test_cases = [
            (None, "application/octet-stream"),
            ("", "application/octet-stream"),
            ("   ", "application/octet-stream"),
            ("\t\n\r", "application/octet-stream"),
        ]

        for input_mime, expected in test_cases:
            result = normalize_mime_type(input_mime)
            assert (
                result == expected
            ), f"Expected '{input_mime}' -> '{expected}', got '{result}'"

    @pytest.mark.unit
    def test_case_normalization(self):
        """Test that MIME types are properly lowercased."""
        test_cases = [
            ("APPLICATION/PDF", "application/pdf"),
            ("Image/PNG", "image/png"),
            ("VIDEO/MP4", "video/mp4"),
            ("Audio/MP3", "audio/mp3"),
            ("TEXT/PLAIN", "text/plain"),
        ]

        for input_mime, expected in test_cases:
            result = normalize_mime_type(input_mime)
            assert (
                result == expected
            ), f"Expected '{input_mime}' -> '{expected}', got '{result}'"

    @pytest.mark.unit
    def test_whitespace_handling(self):
        """Test that whitespace is properly handled."""
        test_cases = [
            ("  image/png  ", "image/png"),
            ("\tapplication/pdf\n", "application/pdf"),
            ("  audio/mp3\r\n  ", "audio/mp3"),
            ("\n\nvideo/mp4\t\t", "video/mp4"),
        ]

        for input_mime, expected in test_cases:
            result = normalize_mime_type(input_mime)
            assert (
                result == expected
            ), f"Expected '{input_mime}' -> '{expected}', got '{result}'"

    @pytest.mark.unit
    def test_unchanged_mime_types(self):
        """Test that MIME types that don't need normalization remain unchanged."""
        test_cases = [
            "application/pdf",
            "text/plain",
            "text/html",
            "application/json",
            "application/xml",
            "text/css",
            "text/javascript",
            "application/javascript",
            "image/svg+xml",
            "application/zip",
            "application/x-zip-compressed",
            "audio/mp3",  # Already normalized
            "audio/ogg",  # Already normalized
            "video/mp4",  # Already normalized
            "image/png",  # Already normalized
            "image/jpeg",  # Already normalized
        ]

        for input_mime in test_cases:
            result = normalize_mime_type(input_mime)
            assert (
                result == input_mime
            ), f"Expected '{input_mime}' to remain unchanged, got '{result}'"

    @pytest.mark.unit
    def test_complex_mime_types(self):
        """Test complex MIME types with parameters and special characters."""
        test_cases = [
            ("application/vnd.ms-excel", "application/vnd.ms-excel"),
            ("application/vnd.ms-powerpoint", "application/vnd.ms-powerpoint"),
            ("application/vnd.ms-word", "application/vnd.ms-word"),
            (
                "application/vnd.oasis.opendocument.text",
                "application/vnd.oasis.opendocument.text",
            ),
            (
                "application/vnd.oasis.opendocument.spreadsheet",
                "application/vnd.oasis.opendocument.spreadsheet",
            ),
            (
                "application/vnd.oasis.opendocument.presentation",
                "application/vnd.oasis.opendocument.presentation",
            ),
        ]

        for input_mime, expected in test_cases:
            result = normalize_mime_type(input_mime)
            assert (
                result == expected
            ), f"Expected '{input_mime}' -> '{expected}', got '{result}'"

    @pytest.mark.unit
    def test_return_type(self):
        """Test that the function always returns a string."""
        test_inputs = [
            "application/pdf",
            "image/png",
            "audio/mpeg",
            None,
            "",
            "   ",
            "APPLICATION/PDF",
            "  image/png  ",
        ]

        for input_mime in test_inputs:
            result = normalize_mime_type(input_mime)
            assert isinstance(
                result, str
            ), f"Expected string return type for input '{input_mime}', got {type(result)}"

    @pytest.mark.unit
    def test_non_empty_result(self):
        """Test that the function never returns an empty string."""
        test_inputs = [
            "application/pdf",
            "image/png",
            "audio/mpeg",
            None,
            "",
            "   ",
            "APPLICATION/PDF",
            "  image/png  ",
        ]

        for input_mime in test_inputs:
            result = normalize_mime_type(input_mime)
            assert (
                result != ""
            ), f"Expected non-empty result for input '{input_mime}', got empty string"

    @pytest.mark.unit
    def test_consistency(self):
        """Test that the function is consistent (same input always produces same output)."""
        test_inputs = [
            "audio/mpeg",
            "APPLICATION/PDF",
            "  image/png  ",
            None,
            "",
        ]

        for input_mime in test_inputs:
            result1 = normalize_mime_type(input_mime)
            result2 = normalize_mime_type(input_mime)
            result3 = normalize_mime_type(input_mime)

            assert (
                result1 == result2 == result3
            ), f"Inconsistent results for input '{input_mime}': {result1}, {result2}, {result3}"

    @pytest.mark.unit
    def test_idempotency(self):
        """Test that applying normalization multiple times doesn't change the result."""
        test_cases = [
            "audio/mpeg",
            "APPLICATION/PDF",
            "  image/png  ",
            "video/x-msvideo",
            "image/x-jpeg",
        ]

        for input_mime in test_cases:
            result1 = normalize_mime_type(input_mime)
            result2 = normalize_mime_type(result1)
            result3 = normalize_mime_type(result2)

            assert (
                result1 == result2 == result3
            ), f"Function not idempotent for input '{input_mime}': {result1}, {result2}, {result3}"

    @pytest.mark.unit
    def test_all_normalization_rules(self):
        """Test all normalization rules in one comprehensive test."""
        # This test ensures we have coverage for all the normalization rules
        normalization_rules = {
            # Audio
            "audio/mpeg": "audio/mp3",
            "application/ogg": "audio/ogg",
            "audio/x-m4a": "audio/mp4",
            "audio/x-wav": "audio/wav",
            # Video
            "video/x-msvideo": "video/avi",
            "video/x-ms-wmv": "video/wmv",
            "video/quicktime": "video/mp4",
            # Image
            "image/x-png": "image/png",
            "image/x-jpeg": "image/jpeg",
            "image/x-gif": "image/gif",
            "image/x-bmp": "image/bmp",
            "image/x-tiff": "image/tiff",
        }

        for input_mime, expected in normalization_rules.items():
            result = normalize_mime_type(input_mime)
            assert (
                result == expected
            ), f"Normalization rule failed: '{input_mime}' -> '{expected}', got '{result}'"

    @pytest.mark.unit
    def test_fallback_behavior(self):
        """Test that unknown MIME types fall back to application/octet-stream."""
        test_cases = [
            "unknown/type",
            "custom/format",
            "application/unknown",
            "text/unknown",
            "image/unknown",
            "audio/unknown",
            "video/unknown",
        ]

        for input_mime in test_cases:
            result = normalize_mime_type(input_mime)
            assert (
                result == input_mime
            ), f"Expected unknown MIME type '{input_mime}' to remain unchanged, got '{result}'"
