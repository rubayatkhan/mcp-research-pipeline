"""Error translation helpers — convert library exceptions to user-friendly messages."""

from __future__ import annotations

import httpx


def translate_youtube_error(exc: Exception) -> str:
    name = type(exc).__name__
    if name == "TranscriptsDisabled":
        return "Transcripts are disabled for this video."
    if name == "NoTranscriptFound":
        return f"No transcript found in the requested language(s). {exc}"
    if name == "VideoUnavailable":
        return "This video is unavailable or does not exist."
    return f"YouTube transcript error: {exc}"


def translate_httpx_error(exc: httpx.HTTPStatusError) -> str:
    status = exc.response.status_code
    messages = {
        401: "Invalid TranscriptAPI key. Check your TRANSCRIPT_API_KEY env var.",
        402: "TranscriptAPI credits exhausted. Top up at transcriptapi.com/billing.",
        404: "Resource not found on YouTube / TranscriptAPI.",
        408: "TranscriptAPI request timed out. Try again.",
        422: "Invalid request parameters. Check your input.",
        429: "TranscriptAPI rate limit hit (300 req/min). Wait a moment and retry.",
    }
    return messages.get(status, f"TranscriptAPI error ({status}): {exc.response.text[:200]}")


def translate_notebooklm_error(exc: Exception) -> str:
    msg = str(exc).lower()
    if "storage_state" in msg or "auth" in msg or "cookie" in msg:
        return (
            "NotebookLM authentication failed. "
            "Run 'notebooklm login' in a terminal to authenticate, "
            "then restart the MCP server."
        )
    if "rate" in msg or "limit" in msg:
        return "NotebookLM rate limit hit. Wait a few minutes and try again."
    return f"NotebookLM error: {exc}"
