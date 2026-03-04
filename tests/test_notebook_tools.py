"""Tests for NotebookLM tool functions (mocked clients)."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from mcp_research_pipeline.tools import notebook


@pytest.mark.asyncio
async def test_create_notebook_success():
    mock_client = AsyncMock()
    mock_client.create_notebook.return_value = {
        "notebook_id": "nb-123",
        "name": "Test Notebook",
    }

    with patch("mcp_research_pipeline.server.nlm_client", mock_client):
        result = await notebook.create_notebook("Test Notebook")

    data = json.loads(result)
    assert data["notebook_id"] == "nb-123"
    assert data["name"] == "Test Notebook"


@pytest.mark.asyncio
async def test_create_notebook_not_connected():
    with patch("mcp_research_pipeline.server.nlm_client", None):
        result = await notebook.create_notebook("Test")

    data = json.loads(result)
    assert "error" in data
    assert "notebooklm login" in data["error"]


@pytest.mark.asyncio
async def test_list_notebooks_success():
    mock_client = AsyncMock()
    mock_client.list_notebooks.return_value = [
        {"notebook_id": "nb-1", "name": "NB 1", "created_at": None, "source_count": 0},
    ]

    with patch("mcp_research_pipeline.server.nlm_client", mock_client):
        result = await notebook.list_notebooks()

    data = json.loads(result)
    assert len(data) == 1
    assert data[0]["notebook_id"] == "nb-1"


@pytest.mark.asyncio
async def test_add_source_invalid_type():
    mock_client = AsyncMock()

    with patch("mcp_research_pipeline.server.nlm_client", mock_client):
        result = await notebook.add_source("nb-1", "pdf", "test.pdf")

    data = json.loads(result)
    assert "error" in data
    assert "Invalid source_type" in data["error"]


@pytest.mark.asyncio
async def test_ask_notebook_success():
    mock_client = AsyncMock()
    mock_client.ask.return_value = {
        "answer": "The video discusses research pipelines.",
        "conversation_id": "conv-1",
        "references": [],
    }

    with patch("mcp_research_pipeline.server.nlm_client", mock_client):
        result = await notebook.ask_notebook("nb-1", "What is this about?")

    data = json.loads(result)
    assert "research pipelines" in data["answer"]
