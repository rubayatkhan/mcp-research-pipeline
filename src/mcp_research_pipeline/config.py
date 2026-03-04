"""Environment variable configuration via pydantic-settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Server configuration read from environment variables.

    Required:
        TRANSCRIPT_API_KEY: Bearer token for TranscriptAPI.com (optional —
            only needed for search/channel/playlist tools).

    Optional:
        NOTEBOOKLM_STORAGE_PATH: Override path to notebooklm storage state
            (default: ~/.notebooklm/storage_state.json).
    """

    transcript_api_key: str = ""
    notebooklm_storage_path: str = "~/.notebooklm/storage_state.json"

    model_config = {"env_prefix": "", "case_sensitive": False}

    @property
    def has_transcript_api(self) -> bool:
        return bool(self.transcript_api_key)
