"""Tests for artifact tool functions (mocked clients)."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from mcp_research_pipeline.tools import artifacts


@pytest.mark.asyncio
async def test_generate_artifact_not_connected():
    with patch("mcp_research_pipeline.server.nlm_client", None):
        result = await artifacts.generate_artifact("nb-1", "audio")

    data = json.loads(result)
    assert "error" in data
    assert "notebooklm login" in data["error"]


@pytest.mark.asyncio
async def test_generate_artifact_success():
    mock_client = AsyncMock()
    mock_client.generate_artifact.return_value = {
        "task_id": "task-abc",
        "artifact_type": "audio",
        "status": "in_progress",
    }

    with patch("mcp_research_pipeline.server.nlm_client", mock_client):
        result = await artifacts.generate_artifact("nb-1", "audio")

    data = json.loads(result)
    assert data["task_id"] == "task-abc"
    assert data["status"] == "in_progress"


@pytest.mark.asyncio
async def test_list_artifacts_success():
    mock_client = AsyncMock()
    mock_client.list_artifacts.return_value = [
        {
            "artifact_id": "a-1",
            "title": "Audio Overview",
            "type": "audio",
            "status": "completed",
            "created_at": "2024-01-01T00:00:00",
        }
    ]

    with patch("mcp_research_pipeline.server.nlm_client", mock_client):
        result = await artifacts.list_artifacts("nb-1")

    data = json.loads(result)
    assert len(data) == 1
    assert data[0]["type"] == "audio"


@pytest.mark.asyncio
async def test_check_artifact_status_success():
    mock_client = AsyncMock()
    mock_client.check_artifact_status.return_value = {
        "task_id": "task-abc",
        "status": "completed",
        "is_complete": True,
    }

    with patch("mcp_research_pipeline.server.nlm_client", mock_client):
        result = await artifacts.check_artifact_status("nb-1", "task-abc")

    data = json.loads(result)
    assert data["is_complete"] is True


@pytest.mark.asyncio
async def test_download_artifact_success():
    mock_client = AsyncMock()
    mock_client.download_artifact.return_value = {
        "file_path": "/tmp/output.mp3",
        "artifact_type": "audio",
    }

    with patch("mcp_research_pipeline.server.nlm_client", mock_client):
        result = await artifacts.download_artifact("nb-1", "audio", "/tmp/output.mp3")

    data = json.loads(result)
    assert data["file_path"] == "/tmp/output.mp3"
