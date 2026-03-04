"""YouTube tools — transcript extraction, search, channel, and playlist."""

from __future__ import annotations

import json
import logging

import httpx

from ..server import mcp, yt_client, api_client
from ..utils.errors import translate_youtube_error, translate_httpx_error

logger = logging.getLogger(__name__)


@mcp.tool()
async def get_transcript(
    video: str,
    languages: list[str] | None = None,
    preserve_formatting: bool = False,
) -> str:
    """Fetch the transcript of a YouTube video.

    Args:
        video: YouTube URL or 11-character video ID.
        languages: Language codes in priority order (default: ["en"]).
        preserve_formatting: Keep HTML formatting tags like <i> and <b>.

    Returns:
        JSON with video_id, language, is_generated, and snippets array.
        Each snippet has text, start_seconds, and duration_seconds.
    """
    from ..server import yt_client

    if yt_client is None:
        return json.dumps({"error": "YouTube transcript client not initialized."})

    try:
        result = await yt_client.fetch_transcript(
            video, languages=languages, preserve_formatting=preserve_formatting
        )
        return json.dumps(result, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": translate_youtube_error(exc)})


# --- TranscriptAPI-powered tools (require TRANSCRIPT_API_KEY) ---


def _require_api_client() -> str | None:
    """Return an error JSON string if the TranscriptAPI client is unavailable."""
    from ..server import api_client

    if api_client is None:
        return json.dumps({
            "error": "YouTube search requires a TranscriptAPI.com API key. "
            "Set the TRANSCRIPT_API_KEY environment variable and restart."
        })
    return None


@mcp.tool()
async def search_youtube(
    query: str,
    result_type: str = "video",
    limit: int = 20,
) -> str:
    """Search YouTube for videos or channels. Costs 1 TranscriptAPI credit.

    Args:
        query: Search query string.
        result_type: "video" or "channel" (default: "video").
        limit: Maximum number of results (default: 20).
    """
    from ..server import api_client

    err = _require_api_client()
    if err:
        return err

    try:
        result = await api_client.search(query, result_type=result_type, limit=limit)
        return json.dumps(result, ensure_ascii=False)
    except httpx.HTTPStatusError as exc:
        return json.dumps({"error": translate_httpx_error(exc)})
    except Exception as exc:
        return json.dumps({"error": f"Search failed: {exc}"})


@mcp.tool()
async def get_channel_latest(channel: str) -> str:
    """Get the 15 most recent videos from a YouTube channel. FREE — no credits.

    Args:
        channel: Channel handle (e.g. "@3blue1brown") or channel URL.
    """
    from ..server import api_client

    err = _require_api_client()
    if err:
        return err

    try:
        result = await api_client.channel_latest(channel)
        return json.dumps(result, ensure_ascii=False)
    except httpx.HTTPStatusError as exc:
        return json.dumps({"error": translate_httpx_error(exc)})
    except Exception as exc:
        return json.dumps({"error": f"Channel latest failed: {exc}"})


@mcp.tool()
async def get_channel_videos(
    channel: str | None = None,
    continuation: str | None = None,
) -> str:
    """Paginated list of all videos from a YouTube channel. Costs 1 credit/page.

    Args:
        channel: Channel handle or URL (required for first page).
        continuation: Continuation token from previous response (for next page).
    """
    from ..server import api_client

    err = _require_api_client()
    if err:
        return err

    try:
        result = await api_client.channel_videos(
            channel=channel, continuation=continuation
        )
        return json.dumps(result, ensure_ascii=False)
    except httpx.HTTPStatusError as exc:
        return json.dumps({"error": translate_httpx_error(exc)})
    except Exception as exc:
        return json.dumps({"error": f"Channel videos failed: {exc}"})


@mcp.tool()
async def get_playlist_videos(
    playlist: str | None = None,
    continuation: str | None = None,
) -> str:
    """Paginated list of videos in a YouTube playlist. Costs 1 credit/page.

    Args:
        playlist: Playlist ID or URL (required for first page).
        continuation: Continuation token from previous response (for next page).
    """
    from ..server import api_client

    err = _require_api_client()
    if err:
        return err

    try:
        result = await api_client.playlist_videos(
            playlist=playlist, continuation=continuation
        )
        return json.dumps(result, ensure_ascii=False)
    except httpx.HTTPStatusError as exc:
        return json.dumps({"error": translate_httpx_error(exc)})
    except Exception as exc:
        return json.dumps({"error": f"Playlist videos failed: {exc}"})
