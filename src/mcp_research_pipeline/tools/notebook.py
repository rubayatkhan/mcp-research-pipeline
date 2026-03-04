"""NotebookLM notebook, source, and chat tools."""

from __future__ import annotations

import json
import logging

from ..server import mcp
from ..utils.errors import translate_notebooklm_error

logger = logging.getLogger(__name__)


def _require_nlm() -> str | None:
    """Return an error JSON string if NotebookLM client is unavailable."""
    from ..server import nlm_client

    if nlm_client is None:
        return json.dumps({
            "error": "NotebookLM is not connected. "
            "Run 'notebooklm login' in a terminal to authenticate, "
            "then restart the MCP server."
        })
    return None


@mcp.tool()
async def create_notebook(name: str) -> str:
    """Create a new NotebookLM notebook.

    Args:
        name: Name for the new notebook.

    Returns:
        JSON with notebook_id and name.
    """
    from ..server import nlm_client

    err = _require_nlm()
    if err:
        return err

    try:
        result = await nlm_client.create_notebook(name)
        return json.dumps(result, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": translate_notebooklm_error(exc)})


@mcp.tool()
async def list_notebooks() -> str:
    """List all NotebookLM notebooks.

    Returns:
        JSON array of notebooks with notebook_id, name, created_at, source_count.
    """
    from ..server import nlm_client

    err = _require_nlm()
    if err:
        return err

    try:
        result = await nlm_client.list_notebooks()
        return json.dumps(result, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": translate_notebooklm_error(exc)})


@mcp.tool()
async def add_source(
    notebook_id: str,
    source_type: str,
    value: str,
    wait: bool = True,
) -> str:
    """Add a source to a NotebookLM notebook.

    Args:
        notebook_id: ID of the target notebook.
        source_type: One of "url", "youtube", or "text".
        value: The URL, YouTube URL, or raw text content to add.
        wait: If true, wait for the source to finish processing (default: true).

    Returns:
        JSON with source_id, title, and status.
    """
    from ..server import nlm_client

    err = _require_nlm()
    if err:
        return err

    if source_type not in ("url", "youtube", "text"):
        return json.dumps({
            "error": f"Invalid source_type: {source_type!r}. "
            "Must be 'url', 'youtube', or 'text'."
        })

    try:
        result = await nlm_client.add_source(
            notebook_id, source_type, value, wait=wait
        )
        return json.dumps(result, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": translate_notebooklm_error(exc)})


@mcp.tool()
async def list_sources(notebook_id: str) -> str:
    """List all sources in a NotebookLM notebook.

    Args:
        notebook_id: ID of the notebook.

    Returns:
        JSON array of sources with source_id, title, url, and status.
    """
    from ..server import nlm_client

    err = _require_nlm()
    if err:
        return err

    try:
        result = await nlm_client.list_sources(notebook_id)
        return json.dumps(result, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": translate_notebooklm_error(exc)})


@mcp.tool()
async def ask_notebook(
    notebook_id: str,
    question: str,
    source_ids: list[str] | None = None,
) -> str:
    """Ask a question against the sources in a NotebookLM notebook.

    NotebookLM uses your sources as context (RAG) and provides
    referenced answers. This is powered by Google's infrastructure.

    Args:
        notebook_id: ID of the notebook to query.
        question: Your question or prompt.
        source_ids: Optional list of source IDs to scope the query to.

    Returns:
        JSON with answer, conversation_id, and references array.
    """
    from ..server import nlm_client

    err = _require_nlm()
    if err:
        return err

    try:
        result = await nlm_client.ask(
            notebook_id, question, source_ids=source_ids
        )
        return json.dumps(result, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": translate_notebooklm_error(exc)})
