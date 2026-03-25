"""
Utility for detecting external URLs in chat message content.

External web pages cannot be opened or browsed by the assistant in this
environment, so users are guided to paste text or upload screenshots instead.
"""
import re

# Matches http:// and https:// URLs
_URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)

EXTERNAL_URL_NOTICE = (
    "⚠️ Heads up! The assistant can't open external links or web pages. "
    "To get help with what's on a page, you can:\n"
    "• Paste the text from the page directly into this chat, or\n"
    "• Upload a screenshot of what you're seeing.\n"
    "Web browsing is not available in this environment."
)


def contains_external_url(text: str) -> bool:
    """Return True if *text* contains at least one http/https URL."""
    return bool(_URL_RE.search(text))
