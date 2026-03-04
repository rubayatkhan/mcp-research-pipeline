"""Adapter wrapping the sync youtube-transcript-api library for async use."""

from __future__ import annotations

import asyncio

from youtube_transcript_api import YouTubeTranscriptApi

from ..utils.youtube_url import extract_video_id


class YouTubeTranscriptClient:
    """Async wrapper around YouTubeTranscriptApi.

    The underlying library is synchronous, so we run fetch calls in a
    thread via asyncio.to_thread() to avoid blocking the event loop.
    """

    def __init__(self) -> None:
        self._api = YouTubeTranscriptApi()

    async def fetch_transcript(
        self,
        video: str,
        languages: list[str] | None = None,
        preserve_formatting: bool = False,
    ) -> dict:
        """Fetch a transcript and return it as a serializable dict.

        Args:
            video: YouTube URL or 11-char video ID.
            languages: Language codes in priority order. Defaults to ["en"].
            preserve_formatting: Keep HTML tags like <i> and <b>.

        Returns:
            Dict with video_id, language, is_generated, and snippets array.
        """
        video_id = extract_video_id(video)
        langs = languages or ["en"]

        transcript = await asyncio.to_thread(
            self._api.fetch, video_id, languages=langs
        )

        return {
            "video_id": video_id,
            "language": transcript.language,
            "language_code": transcript.language_code,
            "is_generated": transcript.is_generated,
            "snippets": [
                {
                    "text": s.text,
                    "start_seconds": s.start,
                    "duration_seconds": s.duration,
                }
                for s in transcript.snippets
            ],
        }
