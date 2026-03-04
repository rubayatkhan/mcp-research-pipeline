"""Tests for YouTube URL parsing and video ID extraction."""

import pytest

from mcp_research_pipeline.utils.youtube_url import extract_video_id


class TestExtractVideoId:
    """Tests for extract_video_id()."""

    def test_bare_id(self):
        assert extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_bare_id_with_whitespace(self):
        assert extract_video_id("  dQw4w9WgXcQ  ") == "dQw4w9WgXcQ"

    def test_standard_url(self):
        assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_standard_url_with_params(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s&list=PLtest"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_short_url(self):
        assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_short_url_with_timestamp(self):
        assert extract_video_id("https://youtu.be/dQw4w9WgXcQ?t=42") == "dQw4w9WgXcQ"

    def test_embed_url(self):
        assert extract_video_id("https://youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_v_url(self):
        assert extract_video_id("https://youtube.com/v/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_shorts_url(self):
        assert extract_video_id("https://youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_no_protocol(self):
        assert extract_video_id("youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_http_url(self):
        assert extract_video_id("http://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_id_with_dashes(self):
        assert extract_video_id("usTeU4Uh0iM") == "usTeU4Uh0iM"

    def test_id_with_underscores(self):
        assert extract_video_id("abc_def_123") == "abc_def_123"

    def test_invalid_empty_string(self):
        with pytest.raises(ValueError, match="Could not extract"):
            extract_video_id("")

    def test_invalid_short_string(self):
        with pytest.raises(ValueError, match="Could not extract"):
            extract_video_id("abc")

    def test_invalid_long_string(self):
        with pytest.raises(ValueError, match="Could not extract"):
            extract_video_id("this_is_way_too_long_to_be_a_video_id")

    def test_invalid_url(self):
        with pytest.raises(ValueError, match="Could not extract"):
            extract_video_id("https://example.com/watch?v=dQw4w9WgXcQ")
