"""NotebookLM artifact generation, listing, status, and download tools."""

from __future__ import annotations

import json
import logging

from ..server import mcp
from ..utils.errors import translate_notebooklm_error

logger = logging.getLogger(__name__)

VALID_ARTIFACT_TYPES = [
    "audio", "video", "quiz", "flashcards", "report",
    "mind_map", "infographic", "slide_deck", "data_table",
]


def _require_nlm() -> str | None:
    from ..server import nlm_client

    if nlm_client is None:
        return json.dumps({
            "error": "NotebookLM is not connected. "
            "Run 'notebooklm login' in a terminal to authenticate, "
            "then restart the MCP server."
        })
    return None


@mcp.tool()
async def generate_artifact(
    notebook_id: str,
    artifact_type: str,
    instructions: str = "",
    source_ids: list[str] | None = None,
    wait: bool = False,
) -> str:
    """Generate a NotebookLM artifact from notebook sources.

    Supported artifact types: audio, video, quiz, flashcards, report,
    mind_map, infographic, slide_deck, data_table.

    Args:
        notebook_id: ID of the notebook with sources.
        artifact_type: Type of artifact to generate.
        instructions: Optional instructions to guide generation.
        source_ids: Optional list of source IDs to use (default: all sources).
        wait: If true, wait for generation to complete (can take minutes).

    Returns:
        JSON with task_id, artifact_type, and status.
    """
    from ..server import nlm_client

    err = _require_nlm()
    if err:
        return err

    try:
        result = await nlm_client.generate_artifact(
            notebook_id,
            artifact_type,
            instructions=instructions,
            source_ids=source_ids,
            wait=wait,
        )
        return json.dumps(result, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": translate_notebooklm_error(exc)})


@mcp.tool()
async def list_artifacts(notebook_id: str) -> str:
    """List all artifacts in a NotebookLM notebook.

    Args:
        notebook_id: ID of the notebook.

    Returns:
        JSON array of artifacts with artifact_id, title, type, status, created_at.
    """
    from ..server import nlm_client

    err = _require_nlm()
    if err:
        return err

    try:
        result = await nlm_client.list_artifacts(notebook_id)
        return json.dumps(result, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": translate_notebooklm_error(exc)})


@mcp.tool()
async def check_artifact_status(notebook_id: str, task_id: str) -> str:
    """Check the generation status of a NotebookLM artifact.

    Args:
        notebook_id: ID of the notebook.
        task_id: Task ID returned by generate_artifact.

    Returns:
        JSON with task_id, status, and is_complete.
    """
    from ..server import nlm_client

    err = _require_nlm()
    if err:
        return err

    try:
        result = await nlm_client.check_artifact_status(notebook_id, task_id)
        return json.dumps(result, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": translate_notebooklm_error(exc)})


@mcp.tool()
async def download_artifact(
    notebook_id: str,
    artifact_type: str,
    output_path: str,
    artifact_id: str | None = None,
) -> str:
    """Download a completed NotebookLM artifact to a local file.

    Args:
        notebook_id: ID of the notebook.
        artifact_type: Type of artifact (audio, video, quiz, etc.).
        output_path: Local file path to save the artifact.
        artifact_id: Optional specific artifact ID (default: latest).

    Returns:
        JSON with file_path and artifact_type.
    """
    from ..server import nlm_client

    err = _require_nlm()
    if err:
        return err

    try:
        result = await nlm_client.download_artifact(
            notebook_id, artifact_type, output_path, artifact_id=artifact_id
        )
        return json.dumps(result, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": translate_notebooklm_error(exc)})
