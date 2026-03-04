"""Composite research_topic tool — end-to-end pipeline."""

from __future__ import annotations

import json
import logging

import httpx

from ..server import mcp
from ..utils.errors import (
    translate_httpx_error,
    translate_notebooklm_error,
    translate_youtube_error,
)

logger = logging.getLogger(__name__)


@mcp.tool()
async def research_topic(
    query: str,
    max_videos: int = 5,
    question: str | None = None,
    notebook_name: str | None = None,
) -> str:
    """End-to-end research pipeline: search YouTube, create a NotebookLM
    notebook, add video sources, and optionally ask a question.

    This tool orchestrates the full workflow:
    1. Search YouTube for videos matching the query
    2. Create a new NotebookLM notebook
    3. Add each video as a YouTube source
    4. Optionally ask a question against all sources

    Requires both TRANSCRIPT_API_KEY (for search) and NotebookLM login.

    Args:
        query: Research topic to search YouTube for.
        max_videos: Maximum number of videos to add as sources (default: 5).
        question: Optional question to ask after adding sources.
        notebook_name: Name for the notebook (default: "Research: {query}").

    Returns:
        JSON with notebook_id, sources added, and optional answer.
    """
    from ..server import api_client, nlm_client

    # Validate both clients are available
    if api_client is None:
        return json.dumps({
            "error": "research_topic requires TRANSCRIPT_API_KEY for YouTube search. "
            "Set the env var and restart."
        })
    if nlm_client is None:
        return json.dumps({
            "error": "research_topic requires NotebookLM. "
            "Run 'notebooklm login' and restart."
        })

    result: dict = {"query": query, "steps": []}

    # Step 1: Search YouTube
    try:
        search_results = await api_client.search(query, result_type="video", limit=max_videos)
        videos = search_results.get("results", search_results.get("data", []))
        if not videos:
            return json.dumps({
                "error": f"No YouTube videos found for: {query!r}",
                "search_response": search_results,
            })
        result["steps"].append({"step": "search", "videos_found": len(videos)})
    except httpx.HTTPStatusError as exc:
        return json.dumps({"error": f"Search failed: {translate_httpx_error(exc)}"})
    except Exception as exc:
        return json.dumps({"error": f"Search failed: {exc}"})

    # Step 2: Create notebook
    name = notebook_name or f"Research: {query}"
    try:
        notebook = await nlm_client.create_notebook(name)
        notebook_id = notebook["notebook_id"]
        result["notebook_id"] = notebook_id
        result["notebook_name"] = notebook["name"]
        result["steps"].append({"step": "create_notebook", "notebook_id": notebook_id})
    except Exception as exc:
        return json.dumps({"error": f"Notebook creation failed: {translate_notebooklm_error(exc)}"})

    # Step 3: Add video sources
    sources_added = []
    sources_failed = []

    for video in videos[:max_videos]:
        # TranscriptAPI search results may have different field names
        video_id = (
            video.get("videoId")
            or video.get("video_id")
            or video.get("id", {}).get("videoId", "")
        )
        video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else video.get("url", "")
        title = video.get("title", video_id)

        if not video_url:
            sources_failed.append({"title": title, "error": "No video URL found"})
            continue

        try:
            source = await nlm_client.add_source(
                notebook_id, "youtube", video_url, wait=True
            )
            sources_added.append({
                "video_title": title,
                "source_id": source["source_id"],
                "status": source["status"],
            })
        except Exception as exc:
            sources_failed.append({
                "video_title": title,
                "error": translate_notebooklm_error(exc),
            })

    result["sources_added"] = sources_added
    result["sources_failed"] = sources_failed
    result["steps"].append({
        "step": "add_sources",
        "added": len(sources_added),
        "failed": len(sources_failed),
    })

    # Step 4: Optionally ask a question
    if question and sources_added:
        try:
            answer = await nlm_client.ask(notebook_id, question)
            result["answer"] = answer
            result["steps"].append({"step": "ask", "question": question})
        except Exception as exc:
            result["answer_error"] = translate_notebooklm_error(exc)

    return json.dumps(result, ensure_ascii=False)
