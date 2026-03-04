# mcp-research-pipeline

MCP server that unifies YouTube transcripts, YouTube search, and Google NotebookLM into a research pipeline for Claude Desktop and any MCP client.

## What It Does

- **Extract YouTube transcripts** (free, no API key needed)
- **Search YouTube** for videos, channels, and playlists (via TranscriptAPI.com)
- **Create NotebookLM notebooks**, add sources, ask questions, and generate deliverables (podcasts, quizzes, reports, etc.)
- **One-shot research pipeline**: search → create notebook → add sources → ask — in a single tool call

NotebookLM acts as a free RAG system — Google pays for the analysis tokens. This MCP server lets Claude Desktop interact with it programmatically.

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Install

```bash
git clone https://github.com/rubayatkhan/mcp-research-pipeline.git
cd mcp-research-pipeline
uv sync
```

### Configure Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "research-pipeline": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/path/to/mcp-research-pipeline",
        "python", "-m", "mcp_research_pipeline"
      ],
      "env": {
        "TRANSCRIPT_API_KEY": "your-key-here"
      }
    }
  }
}
```

### Authentication

**YouTube Transcripts** — works immediately, no setup needed.

**YouTube Search** (optional) — sign up at [transcriptapi.com](https://transcriptapi.com), get an API key, set `TRANSCRIPT_API_KEY` in your env or Claude Desktop config. You get 100 free credits.

**NotebookLM** (optional) — run the login command once:

```bash
uv run notebooklm login
```

This opens a browser for Google authentication. Credentials are saved at `~/.notebooklm/storage_state.json`.

## Tools (15 total)

### YouTube (5 tools)

| Tool | Cost | Description |
|------|------|-------------|
| `get_transcript` | Free | Fetch transcript from a YouTube URL or video ID |
| `search_youtube` | 1 credit | Search YouTube for videos or channels |
| `get_channel_latest` | Free | Get 15 most recent videos from a channel |
| `get_channel_videos` | 1 credit/page | Paginated list of all channel videos |
| `get_playlist_videos` | 1 credit/page | Paginated list of playlist videos |

### NotebookLM — Notebooks (5 tools)

| Tool | Description |
|------|-------------|
| `create_notebook` | Create a new NotebookLM notebook |
| `list_notebooks` | List all notebooks |
| `add_source` | Add a URL, YouTube video, or text to a notebook |
| `list_sources` | List sources in a notebook |
| `ask_notebook` | Ask a question against notebook sources (RAG) |

### NotebookLM — Artifacts (4 tools)

| Tool | Description |
|------|-------------|
| `generate_artifact` | Generate audio, video, quiz, flashcards, report, mind_map, infographic, slide_deck, or data_table |
| `list_artifacts` | List all artifacts in a notebook |
| `check_artifact_status` | Poll generation status |
| `download_artifact` | Download a completed artifact |

### Pipeline (1 tool)

| Tool | Description |
|------|-------------|
| `research_topic` | End-to-end: search YouTube → create notebook → add sources → ask question |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TRANSCRIPT_API_KEY` | No | TranscriptAPI.com API key (enables YouTube search tools) |
| `NOTEBOOKLM_STORAGE_PATH` | No | Custom path to NotebookLM auth (default: `~/.notebooklm/storage_state.json`) |

## Development

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Lint
uv run ruff check src/ tests/

# Run server locally
uv run python -m mcp_research_pipeline
```

## Architecture

The server uses three design patterns:

- **Facade Pattern**: 15 MCP tools presenting a unified interface over three different APIs
- **Adapter Pattern**: `clients/` layer wraps each third-party library behind a common async interface
- **Lifespan Management**: FastMCP lifespan hook creates expensive clients once at startup, tears them down on shutdown

```
server.py (FastMCP + lifespan)
├── clients/
│   ├── youtube_transcript.py  → youtube-transcript-api (sync→async)
│   ├── transcript_api.py      → TranscriptAPI.com REST (httpx)
│   └── notebooklm.py          → notebooklm-py (async)
├── tools/
│   ├── youtube.py     (5 tools)
│   ├── notebook.py    (5 tools)
│   ├── artifacts.py   (4 tools)
│   └── pipeline.py    (1 tool)
└── utils/
    ├── youtube_url.py  (URL parsing)
    └── errors.py       (error translation)
```

## License

MIT
