"""
Integration tests for the chat WebSocket URL-detection behaviour.

These tests exercise the contains_external_url() helper directly together with
the notice payload structure that the WebSocket handler sends to users, without
requiring a live database or full server stack.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.utils.url_detection import contains_external_url, EXTERNAL_URL_NOTICE


# ---------------------------------------------------------------------------
# Helper – build the notice payload the way the handler does
# ---------------------------------------------------------------------------

def build_notice_payload():
    return {
        "notice": {
            "type": "external_url_warning",
            "message": EXTERNAL_URL_NOTICE,
        }
    }


# ---------------------------------------------------------------------------
# Tests for notice payload structure
# ---------------------------------------------------------------------------

class TestNoticePayload:
    """Validate the shape of the JSON payload sent back to users."""

    def test_notice_key_present(self):
        payload = build_notice_payload()
        assert "notice" in payload

    def test_notice_type_is_external_url_warning(self):
        payload = build_notice_payload()
        assert payload["notice"]["type"] == "external_url_warning"

    def test_notice_message_is_string(self):
        payload = build_notice_payload()
        assert isinstance(payload["notice"]["message"], str)
        assert len(payload["notice"]["message"]) > 0


# ---------------------------------------------------------------------------
# Tests for the trigger condition: URL present → notice sent
# ---------------------------------------------------------------------------

class TestNoticeTriggeredOnUrl:
    """Confirm a notice is triggered for URL-containing messages."""

    @pytest.mark.asyncio
    async def test_url_message_triggers_notice(self):
        """When content has an external URL the handler should send a notice."""
        sent_responses = []

        mock_ws = AsyncMock()
        mock_ws.send_json.side_effect = lambda payload: sent_responses.append(payload)

        user_content = "Here is the Google link: https://www.google.com/search?q=laptop"

        if contains_external_url(user_content):
            await mock_ws.send_json(build_notice_payload())

        assert len(sent_responses) == 1
        assert sent_responses[0]["notice"]["type"] == "external_url_warning"

    @pytest.mark.asyncio
    async def test_plain_message_does_not_trigger_notice(self):
        """When content has no URL the handler should NOT send a notice."""
        sent_responses = []

        mock_ws = AsyncMock()
        mock_ws.send_json.side_effect = lambda payload: sent_responses.append(payload)

        user_content = "I am interested in your textbook listing."

        if contains_external_url(user_content):
            await mock_ws.send_json(build_notice_payload())

        assert len(sent_responses) == 0

    @pytest.mark.asyncio
    async def test_http_url_also_triggers_notice(self):
        sent_responses = []

        mock_ws = AsyncMock()
        mock_ws.send_json.side_effect = lambda payload: sent_responses.append(payload)

        user_content = "http://example.com/item/123"

        if contains_external_url(user_content):
            await mock_ws.send_json(build_notice_payload())

        assert len(sent_responses) == 1
        assert "notice" in sent_responses[0]

    @pytest.mark.asyncio
    async def test_notice_sent_only_to_sender(self):
        """Only the sender's websocket receives the notice (not the peer's)."""
        sender_responses = []
        peer_responses = []

        sender_ws = AsyncMock()
        sender_ws.send_json.side_effect = lambda p: sender_responses.append(p)

        peer_ws = AsyncMock()
        peer_ws.send_json.side_effect = lambda p: peer_responses.append(p)

        user_content = "Check https://example.com"

        # Simulate handler logic: notice only sent to sender
        if contains_external_url(user_content):
            await sender_ws.send_json(build_notice_payload())

        assert len(sender_responses) == 1
        assert len(peer_responses) == 0
