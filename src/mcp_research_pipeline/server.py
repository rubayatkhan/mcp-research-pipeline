"""FastMCP server definition with lifespan-managed clients."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastmcp import FastMCP

from .config import Settings
from .clients.youtube_transcript import YouTubeTranscriptClient
from .clients.transcript_api import TranscriptAPIClient
from .clients.notebooklm import NotebookLMClientWrapper

logger = logging.getLogger(__name__)

# Shared client state — populated during lifespan
yt_client: YouTubeTranscriptClient | None = None
api_client: TranscriptAPIClient | None = None
nlm_client: NotebookLMClientWrapper | None = None


@asynccontextmanager
async def lifespan(server: FastMCP):
    """Initialize shared clients at startup, tear down on shutdown."""
    global yt_client, api_client, nlm_client

    settings = Settings()

    # YouTube transcript client (always available, no API key needed)
    yt_client = YouTubeTranscriptClient()
    logger.info("YouTube transcript client ready")

    # TranscriptAPI.com client (optional, needs API key)
    if settings.has_transcript_api:
        api_client = TranscriptAPIClient(api_key=settings.transcript_api_key)
        logger.info("TranscriptAPI.com client ready (search enabled)")
    else:
        api_client = None
        logger.info(
            "TRANSCRIPT_API_KEY not set — YouTube search/channel/playlist "
            "tools will be unavailable. Set the env var to enable them."
        )

    # NotebookLM client (needs prior `notebooklm login`)
    try:
        storage_path = settings.notebooklm_storage_path
        if storage_path == "~/.notebooklm/storage_state.json":
            nlm_client = await NotebookLMClientWrapper.create()
        else:
            nlm_client = await NotebookLMClientWrapper.create(storage_path=storage_path)
        logger.info("NotebookLM client ready")
    except Exception as e:
        nlm_client = None
        logger.warning(
            "NotebookLM client failed to initialize: %s. "
            "Run 'notebooklm login' to authenticate.",
            e,
        )

    try:
        yield
    finally:
        if api_client:
            await api_client.close()
        if nlm_client:
            await nlm_client.close()


mcp = FastMCP(
    name="mcp-research-pipeline",
    instructions=(
        "Research pipeline server providing YouTube transcript extraction, "
        "YouTube search (via TranscriptAPI.com), and NotebookLM notebook "
        "management. Use get_transcript to extract video transcripts (free), "
        "search_youtube to find videos, and NotebookLM tools to create "
        "research notebooks, add sources, ask questions, and generate "
        "deliverables like podcasts, quizzes, and infographics."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# Import tool modules — decorators register tools on the mcp instance
from .tools import youtube, notebook, artifacts, pipeline  # noqa: E402, F401


def main():
    """Console script entry point."""
    mcp.run(transport="stdio")
