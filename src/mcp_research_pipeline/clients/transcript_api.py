"""Adapter wrapping TranscriptAPI.com REST endpoints via httpx."""

from __future__ import annotations

import httpx

BASE_URL = "https://transcriptapi.com/api/v2"


class TranscriptAPIClient:
    """Async client for TranscriptAPI.com YouTube search and data endpoints."""

    def __init__(self, api_key: str) -> None:
        self._client = httpx.AsyncClient(
            base_url=BASE_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0,
        )

    async def search(
        self, query: str, result_type: str = "video", limit: int = 20
    ) -> dict:
        """Search YouTube for videos or channels. Costs 1 credit."""
        resp = await self._client.get(
            "/youtube/search",
            params={"q": query, "type": result_type, "limit": limit},
        )
        resp.raise_for_status()
        return resp.json()

    async def channel_latest(self, channel: str) -> dict:
        """Get the 15 most recent videos from a channel. FREE."""
        resp = await self._client.get(
            "/youtube/channel/latest", params={"channel": channel}
        )
        resp.raise_for_status()
        return resp.json()

    async def channel_videos(
        self, channel: str | None = None, continuation: str | None = None
    ) -> dict:
        """Paginated list of all channel videos. 1 credit/page."""
        params: dict[str, str] = {}
        if channel:
            params["channel"] = channel
        if continuation:
            params["continuation"] = continuation
        resp = await self._client.get("/youtube/channel/videos", params=params)
        resp.raise_for_status()
        return resp.json()

    async def playlist_videos(
        self, playlist: str | None = None, continuation: str | None = None
    ) -> dict:
        """Paginated list of playlist videos. 1 credit/page."""
        params: dict[str, str] = {}
        if playlist:
            params["playlist"] = playlist
        if continuation:
            params["continuation"] = continuation
        resp = await self._client.get("/youtube/playlist/videos", params=params)
        resp.raise_for_status()
        return resp.json()

    async def close(self) -> None:
        await self._client.aclose()
