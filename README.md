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

### Step 1: Clone and install

```bash
git clone https://github.com/rubayatkhan/mcp-research-pipeline.git
cd mcp-research-pipeline
uv sync
```

### Step 2: Install Playwright browser

NotebookLM requires a Chromium browser for authentication. This is a one-time setup:

```bash
uv run python -m playwright install chromium
```

> **Note:** `playwright` is not a standalone CLI command — it's bundled inside the project's virtual environment. Always run it with `uv run python -m playwright`, not just `playwright`.

### Step 3: Authenticate with NotebookLM (optional)

```bash
uv run notebooklm login
```

This opens a browser window for Google sign-in. Your credentials are saved at `~/.notebooklm/storage_state.json` and persist across server restarts.

> **Skip this step** if you only want YouTube transcript/search tools. NotebookLM tools will return a helpful error message telling you to authenticate.

### Step 4: Get a TranscriptAPI key (optional)

Sign up at [transcriptapi.com](https://transcriptapi.com) to get an API key. You get **100 free credits**.

> **Skip this step** if you only need `get_transcript` (which is free and keyless). The search, channel, and playlist tools require this key.

### Step 5: Configure Claude Desktop

Add to your Claude Desktop config:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**Option A — Direct venv script (recommended, avoids path issues):**

```json
{
  "mcpServers": {
    "research-pipeline": {
      "command": "/absolute/path/to/mcp-research-pipeline/.venv/bin/mcp-research-pipeline",
      "env": {
        "TRANSCRIPT_API_KEY": "your-key-here"
      }
    }
  }
}
```

Replace `/absolute/path/to/mcp-research-pipeline` with your actual clone location. Leave `TRANSCRIPT_API_KEY` empty or omit the `env` block if you don't have a key yet.

**Option B — Using uv run (only if your path has no spaces):**

```json
{
  "mcpServers": {
    "research-pipeline": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/absolute/path/to/mcp-research-pipeline",
        "python", "-m", "mcp_research_pipeline"
      ],
      "env": {
        "TRANSCRIPT_API_KEY": "your-key-here"
      }
    }
  }
}
```

> **Warning:** Option B fails if your path contains spaces (e.g., iCloud Drive, OneDrive, Google Drive). Use Option A instead.

### Step 6: Restart Claude Desktop

Fully quit Claude Desktop (Cmd+Q / Ctrl+Q) and reopen it. The research-pipeline server should appear in your MCP tools.

## Troubleshooting

### "Server disconnected" in Claude Desktop

Check the server log at `~/Library/Logs/Claude/mcp-server-research-pipeline.log` (macOS). Common causes:

| Error | Fix |
|-------|-----|
| `No module named mcp_research_pipeline` | Your path has spaces. Switch to Option A (direct venv script). |
| `No module named playwright` | Run `uv run python -m playwright install chromium` in the project directory. |
| `command not found: playwright` | Don't use `playwright` directly. Use `uv run python -m playwright install chromium`. |
| Server starts then immediately disconnects | NotebookLM auth may have expired. Run `uv run notebooklm login` again. |

### "NotebookLM is not connected"

Run `uv run notebooklm login` in the project directory. This opens a browser for Google authentication.

### "TRANSCRIPT_API_KEY" errors

The `get_transcript` tool works without any API key. Only `search_youtube`, `get_channel_latest`, `get_channel_videos`, and `get_playlist_videos` need a TranscriptAPI.com key.

### Paths with spaces (iCloud, OneDrive, Google Drive)

If your project lives in a path with spaces (like `~/Library/Mobile Documents/com~apple~CloudDocs/`), the `uv run --directory` approach will fail. Two options:

1. **Use Option A** (direct venv script path) — this always works.
2. **Create a symlink** to a path without spaces:
   ```bash
   ln -sf "/path/with spaces/mcp-research-pipeline" ~/mcp-research-pipeline
   ```
   Then point Claude Desktop at `~/mcp-research-pipeline/.venv/bin/mcp-research-pipeline`.

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

# Run server locally (stdio mode)
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
