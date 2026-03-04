"""Tests for YouTube tool functions (mocked clients)."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from mcp_research_pipeline.tools import youtube


@pytest.mark.asyncio
async def test_get_transcript_returns_json():
    """get_transcript should return serialized JSON from the client."""
    mock_result = {
        "video_id": "dQw4w9WgXcQ",
        "language": "English",
        "language_code": "en",
        "is_generated": True,
        "snippets": [{"text": "Hello", "start_seconds": 0.0, "duration_seconds": 1.0}],
    }

    mock_client = AsyncMock()
    mock_client.fetch_transcript.return_value = mock_result

    with patch("mcp_research_pipeline.tools.youtube.yt_client", mock_client):
        # Need to also patch the module-level import inside the function
        with patch("mcp_research_pipeline.server.yt_client", mock_client):
            result = await youtube.get_transcript("dQw4w9WgXcQ")

    data = json.loads(result)
    assert data["video_id"] == "dQw4w9WgXcQ"
    assert len(data["snippets"]) == 1


@pytest.mark.asyncio
async def test_get_transcript_client_not_initialized():
    """get_transcript returns error if client is None."""
    with patch("mcp_research_pipeline.server.yt_client", None):
        result = await youtube.get_transcript("dQw4w9WgXcQ")

    data = json.loads(result)
    assert "error" in data


@pytest.mark.asyncio
async def test_search_youtube_without_api_key():
    """search_youtube returns error when api_client is None."""
    with patch("mcp_research_pipeline.server.api_client", None):
        result = await youtube.search_youtube("python tutorial")

    data = json.loads(result)
    assert "error" in data
    assert "TRANSCRIPT_API_KEY" in data["error"]


@pytest.mark.asyncio
async def test_search_youtube_success():
    """search_youtube forwards to api_client.search()."""
    mock_result = {"results": [{"title": "Video 1", "videoId": "abc12345678"}]}
    mock_client = AsyncMock()
    mock_client.search.return_value = mock_result

    with patch("mcp_research_pipeline.server.api_client", mock_client):
        result = await youtube.search_youtube("test query", limit=5)

    data = json.loads(result)
    assert data["results"][0]["title"] == "Video 1"
    mock_client.search.assert_called_once_with("test query", result_type="video", limit=5)
