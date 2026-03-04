"""Adapter wrapping the notebooklm-py async client for MCP server lifecycle."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


class NotebookLMClientWrapper:
    """Manages NotebookLMClient lifecycle for use inside a FastMCP lifespan.

    Usage:
        wrapper = await NotebookLMClientWrapper.create()
        try:
            notebooks = await wrapper.list_notebooks()
        finally:
            await wrapper.close()
    """

    def __init__(self, client: Any) -> None:
        self._client = client

    @classmethod
    async def create(cls, storage_path: str | None = None) -> NotebookLMClientWrapper:
        """Create and connect a NotebookLMClient from stored auth."""
        from notebooklm import NotebookLMClient

        if storage_path:
            client = await NotebookLMClient.from_storage(path=storage_path)
        else:
            client = await NotebookLMClient.from_storage()
        await client.__aenter__()
        return cls(client)

    async def close(self) -> None:
        await self._client.__aexit__(None, None, None)

    # -- Notebooks --

    async def list_notebooks(self) -> list[dict]:
        notebooks = await self._client.notebooks.list()
        return [
            {
                "notebook_id": nb.id,
                "name": nb.title,
                "created_at": _fmt_dt(nb.created_at),
                "source_count": nb.source_count,
            }
            for nb in notebooks
        ]

    async def create_notebook(self, name: str) -> dict:
        nb = await self._client.notebooks.create(name)
        return {"notebook_id": nb.id, "name": nb.title}

    async def delete_notebook(self, notebook_id: str) -> dict:
        result = await self._client.notebooks.delete(notebook_id)
        return {"deleted": result, "notebook_id": notebook_id}

    # -- Sources --

    async def add_source(
        self,
        notebook_id: str,
        source_type: str,
        value: str,
        wait: bool = True,
    ) -> dict:
        """Add a source to a notebook.

        source_type: 'url', 'youtube', or 'text'
        """
        if source_type == "youtube":
            source = await self._client.sources.add_youtube(
                notebook_id, value, wait=wait
            )
        elif source_type == "text":
            source = await self._client.sources.add_text(
                notebook_id, value, wait=wait
            )
        else:
            source = await self._client.sources.add_url(
                notebook_id, value, wait=wait
            )

        return {
            "source_id": source.id,
            "title": source.title,
            "status": "ready" if source.is_ready else "processing",
        }

    async def list_sources(self, notebook_id: str) -> list[dict]:
        sources = await self._client.sources.list(notebook_id)
        return [
            {
                "source_id": s.id,
                "title": s.title,
                "url": s.url,
                "status": "ready" if s.is_ready else ("error" if s.is_error else "processing"),
            }
            for s in sources
        ]

    # -- Chat --

    async def ask(
        self,
        notebook_id: str,
        question: str,
        source_ids: list[str] | None = None,
    ) -> dict:
        result = await self._client.chat.ask(
            notebook_id, question, source_ids=source_ids
        )
        return {
            "answer": result.answer,
            "conversation_id": result.conversation_id,
            "references": [
                {
                    "source_id": ref.source_id,
                    "source_title": ref.source_title,
                    "excerpt": ref.excerpt,
                }
                for ref in result.references
            ],
        }

    # -- Artifacts --

    async def generate_artifact(
        self,
        notebook_id: str,
        artifact_type: str,
        instructions: str = "",
        source_ids: list[str] | None = None,
        wait: bool = False,
    ) -> dict:
        """Generate an artifact. Returns task_id and status."""
        generate_methods = {
            "audio": self._client.artifacts.generate_audio,
            "video": self._client.artifacts.generate_video,
            "quiz": self._client.artifacts.generate_quiz,
            "flashcards": self._client.artifacts.generate_flashcards,
            "report": self._client.artifacts.generate_report,
            "mind_map": self._client.artifacts.generate_mind_map,
            "infographic": self._client.artifacts.generate_infographic,
            "slide_deck": self._client.artifacts.generate_slide_deck,
            "data_table": self._client.artifacts.generate_data_table,
        }

        method = generate_methods.get(artifact_type)
        if not method:
            return {"error": f"Unknown artifact type: {artifact_type!r}. "
                    f"Valid types: {', '.join(generate_methods)}"}

        kwargs: dict[str, Any] = {"notebook_id": notebook_id}
        if source_ids:
            kwargs["source_ids"] = source_ids

        # mind_map is synchronous (returns dict, not GenerationStatus)
        if artifact_type == "mind_map":
            result = await method(**kwargs)
            return {
                "artifact_type": "mind_map",
                "status": "completed",
                "data": result,
            }

        # Instructions param name varies by method
        if instructions:
            kwargs["instructions"] = instructions

        status = await method(**kwargs)

        if wait and hasattr(status, "task_id"):
            status = await self._client.artifacts.wait_for_completion(
                notebook_id, status.task_id, timeout=600.0
            )

        return {
            "task_id": getattr(status, "task_id", None),
            "artifact_type": artifact_type,
            "status": getattr(status, "status", "unknown"),
        }

    async def list_artifacts(self, notebook_id: str) -> list[dict]:
        artifacts = await self._client.artifacts.list(notebook_id)
        return [
            {
                "artifact_id": a.id,
                "title": a.title,
                "type": a.kind.name if hasattr(a.kind, "name") else str(a.kind),
                "status": a.status,
                "created_at": _fmt_dt(a.created_at),
            }
            for a in artifacts
        ]

    async def check_artifact_status(self, notebook_id: str, task_id: str) -> dict:
        status = await self._client.artifacts.poll_status(notebook_id, task_id)
        return {
            "task_id": task_id,
            "status": status.status,
            "is_complete": status.is_complete,
        }

    async def download_artifact(
        self,
        notebook_id: str,
        artifact_type: str,
        output_path: str,
        artifact_id: str | None = None,
    ) -> dict:
        """Download a completed artifact to a local file."""
        download_methods = {
            "audio": self._client.artifacts.download_audio,
            "video": self._client.artifacts.download_video,
            "quiz": self._client.artifacts.download_quiz,
            "flashcards": self._client.artifacts.download_flashcards,
            "report": self._client.artifacts.download_report,
            "mind_map": self._client.artifacts.download_mind_map,
            "infographic": self._client.artifacts.download_infographic,
            "slide_deck": self._client.artifacts.download_slide_deck,
            "data_table": self._client.artifacts.download_data_table,
        }

        method = download_methods.get(artifact_type)
        if not method:
            return {"error": f"Unknown artifact type for download: {artifact_type!r}"}

        kwargs: dict[str, Any] = {
            "notebook_id": notebook_id,
            "output_path": output_path,
        }
        if artifact_id:
            kwargs["artifact_id"] = artifact_id

        path = await method(**kwargs)
        return {
            "file_path": str(path),
            "artifact_type": artifact_type,
        }


def _fmt_dt(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.isoformat()
