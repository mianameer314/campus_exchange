"""
Unit tests for app.utils.url_detection.

Covers contains_external_url() and the wording of EXTERNAL_URL_NOTICE.
"""
import pytest
from app.utils.url_detection import contains_external_url, EXTERNAL_URL_NOTICE


# ---------------------------------------------------------------------------
# contains_external_url
# ---------------------------------------------------------------------------

class TestContainsExternalUrl:
    """Tests that confirm URL detection works correctly."""

    # --- positive cases (URL present) ---

    def test_detects_https_url(self):
        assert contains_external_url("https://www.example.com") is True

    def test_detects_http_url(self):
        assert contains_external_url("http://example.com/page") is True

    def test_detects_google_search_url(self):
        long_url = (
            "https://www.google.com/search?q=laptop"
            "&rlz=1C1CHBF&sourceid=chrome&ie=UTF-8"
        )
        assert contains_external_url(long_url) is True

    def test_detects_url_embedded_in_sentence(self):
        assert contains_external_url("Check this out: https://example.com/listing/42") is True

    def test_detects_url_at_end_of_sentence(self):
        assert contains_external_url("Here is the link https://example.com.") is True

    def test_case_insensitive_http(self):
        assert contains_external_url("HTTP://EXAMPLE.COM") is True

    def test_case_insensitive_https(self):
        assert contains_external_url("HTTPS://EXAMPLE.COM/path") is True

    # --- negative cases (no URL present) ---

    def test_plain_text_no_url(self):
        assert contains_external_url("I want to sell my old laptop.") is False

    def test_empty_string(self):
        assert contains_external_url("") is False

    def test_ftp_url_not_detected(self):
        """Only http/https URLs should trigger the notice."""
        assert contains_external_url("ftp://files.example.com/file.zip") is False

    def test_email_address_not_detected(self):
        assert contains_external_url("contact me at user@example.com") is False

    def test_partial_url_without_scheme(self):
        assert contains_external_url("www.example.com") is False

    def test_whitespace_only(self):
        assert contains_external_url("   ") is False


# ---------------------------------------------------------------------------
# EXTERNAL_URL_NOTICE wording
# ---------------------------------------------------------------------------

class TestExternalUrlNotice:
    """Ensures the notice message is concise and mentions key alternatives."""

    def test_notice_is_non_empty_string(self):
        assert isinstance(EXTERNAL_URL_NOTICE, str)
        assert len(EXTERNAL_URL_NOTICE) > 0

    def test_notice_mentions_paste_text_alternative(self):
        assert "paste" in EXTERNAL_URL_NOTICE.lower() or "text" in EXTERNAL_URL_NOTICE.lower()

    def test_notice_mentions_screenshot_alternative(self):
        assert "screenshot" in EXTERNAL_URL_NOTICE.lower()

    def test_notice_mentions_web_browsing_limitation(self):
        assert (
            "web" in EXTERNAL_URL_NOTICE.lower()
            or "link" in EXTERNAL_URL_NOTICE.lower()
            or "external" in EXTERNAL_URL_NOTICE.lower()
        )
