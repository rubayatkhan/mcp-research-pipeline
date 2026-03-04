"""YouTube URL parsing and video ID extraction."""

from __future__ import annotations

import re

_PATTERNS = [
    r"(?:youtube\.com/watch\?.*?v=)([\w-]{11})",
    r"(?:youtu\.be/)([\w-]{11})",
    r"(?:youtube\.com/embed/)([\w-]{11})",
    r"(?:youtube\.com/v/)([\w-]{11})",
    r"(?:youtube\.com/shorts/)([\w-]{11})",
]
_BARE_ID = re.compile(r"^[\w-]{11}$")


def extract_video_id(video: str) -> str:
    """Extract an 11-character YouTube video ID from a URL or bare ID.

    Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://youtube.com/embed/VIDEO_ID
        - https://youtube.com/v/VIDEO_ID
        - https://youtube.com/shorts/VIDEO_ID
        - Bare 11-character video IDs

    Raises:
        ValueError: If no valid video ID can be extracted.
    """
    video = video.strip()
    if _BARE_ID.match(video):
        return video
    for pattern in _PATTERNS:
        match = re.search(pattern, video)
        if match:
            return match.group(1)
    raise ValueError(
        f"Could not extract YouTube video ID from: {video!r}. "
        "Provide a YouTube URL or an 11-character video ID."
    )
