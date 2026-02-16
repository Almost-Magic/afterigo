"""
ELAINE v4 — Beast Test Suite
25+ tests covering all critical features.

Run: python -m pytest tests/test_elaine.py -v
From: CK/Elaine/

Almost Magic Tech Lab
"""

import json
import os
import sys
from unittest.mock import patch, MagicMock

import pytest

# Ensure the app root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app


@pytest.fixture(scope="session")
def app():
    """Create test Flask app (session-scoped to avoid blueprint re-registration)."""
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


# ═══════════════════════════════════════════════════════════════════
# Health & Status (3)
# ═══════════════════════════════════════════════════════════════════

class TestHealth:

    def test_health(self, client):
        """GET /api/health returns 200 with healthy status."""
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "healthy"
        assert data["service"] == "ELAINE"
        assert "timestamp" in data

    def test_ai_status(self, client):
        """GET /api/ai/status returns engine info."""
        resp = client.get("/api/ai/status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "claude_cli" in data
        assert "active_engine" in data
        assert "status" in data
        # active_engine should be one of: claude-cli, ollama, none
        assert data["active_engine"] in ("claude-cli", "ollama", "none")

    def test_status(self, client):
        """GET /api/status returns full system status."""
        resp = client.get("/api/status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == "Maestro Elaine"
        assert "modules" in data
        assert data["voice_id"] == "XQanfahzbl1YiUlZi5NW"


# ═══════════════════════════════════════════════════════════════════
# Chat (4)
# ═══════════════════════════════════════════════════════════════════

class TestChat:

    @patch("utils.ai_engine.query_ai")
    def test_chat_responds(self, mock_ai, client):
        """POST /api/chat returns a response."""
        mock_ai.return_value = {"text": "Morning, Mani.", "engine": "claude-cli"}
        resp = client.post("/api/chat", json={"message": "Good morning"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "reply" in data
        assert data["reply"] == "Morning, Mani."
        assert data["via"] == "claude-cli"

    @patch("utils.ai_engine.query_ai")
    def test_chat_session(self, mock_ai, client):
        """Two messages should maintain conversation context."""
        mock_ai.return_value = {"text": "First reply.", "engine": "claude-cli"}
        resp1 = client.post("/api/chat", json={"message": "Hello", "history": []})
        assert resp1.status_code == 200

        mock_ai.return_value = {"text": "Second reply.", "engine": "claude-cli"}
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "First reply."},
        ]
        resp2 = client.post("/api/chat", json={"message": "Follow up", "history": history})
        assert resp2.status_code == 200
        data = resp2.get_json()
        assert data["reply"] == "Second reply."

    @patch("utils.ai_engine.query_ai")
    def test_chat_personality(self, mock_ai, client):
        """Chat should pass ELAINE personality system prompt."""
        mock_ai.return_value = {"text": "G'day Mani.", "engine": "claude-cli"}
        resp = client.post("/api/chat", json={"message": "Who are you?"})
        assert resp.status_code == 200
        # Verify the system prompt was passed to query_ai
        call_args = mock_ai.call_args
        system_prompt = call_args[0][0] if call_args[0] else call_args[1].get("system_prompt", "")
        assert "ELAINE" in system_prompt
        assert "Mani" in system_prompt

    @patch("utils.ai_engine.query_ai")
    def test_chat_no_ai(self, mock_ai, client):
        """Graceful 503 when no AI available — NEVER says 'open Claude'."""
        mock_ai.return_value = None
        resp = client.post("/api/chat", json={"message": "Hello"})
        assert resp.status_code == 503
        data = resp.get_json()
        assert "reply" in data
        # CRITICAL: Never tell user to open Claude
        reply_lower = data["reply"].lower()
        assert "open claude" not in reply_lower
        assert "open" not in reply_lower or "open" in reply_lower and "desktop" not in reply_lower

    def test_chat_empty_message(self, client):
        """POST /api/chat with empty message returns 400."""
        resp = client.post("/api/chat", json={"message": ""})
        assert resp.status_code == 400


# ═══════════════════════════════════════════════════════════════════
# Morning Brief (3)
# ═══════════════════════════════════════════════════════════════════

class TestMorningBrief:

    def test_briefing_generates(self, client):
        """GET /api/morning-briefing returns content."""
        resp = client.get("/api/morning-briefing")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "briefing" in data or "raw_data" in data
        assert "generated_at" in data

    def test_briefing_voice(self, client):
        """GET /api/morning-briefing/voice returns voice segments."""
        resp = client.get("/api/morning-briefing/voice")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "segments" in data
        assert "plain_text" in data
        assert len(data["segments"]) > 0
        # First segment should be greeting
        assert "Mani" in data["segments"][0]["text"] or "Morning" in data["segments"][0]["text"]

    def test_briefing_latest(self, client):
        """GET /api/morning-briefing/latest returns stored briefing or 404."""
        resp = client.get("/api/morning-briefing/latest")
        # Either 200 (briefing exists) or 404 (none stored yet)
        assert resp.status_code in (200, 404)


# ═══════════════════════════════════════════════════════════════════
# Thinking Frameworks (3)
# ═══════════════════════════════════════════════════════════════════

class TestThinking:

    def test_frameworks_matrix(self, client):
        """GET /api/thinking/matrix returns framework matrix."""
        resp = client.get("/api/thinking/matrix")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) >= 5  # Multiple domain/stakes combos

    def test_analyse(self, client):
        """POST /api/thinking/analyse returns analysis."""
        resp = client.post("/api/thinking/analyse", json={
            "topic": "Should I hire a new developer?",
            "domain": "strategy",
            "stakes": "medium",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "synthesis" in data or "frameworks_applied" in data

    def test_thinking_status(self, client):
        """GET /api/thinking/status returns status."""
        resp = client.get("/api/thinking/status")
        assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════
# Gatekeeper (3)
# ═══════════════════════════════════════════════════════════════════

class TestGatekeeper:

    def test_gatekeeper_check(self, client):
        """POST /api/gatekeeper/check returns a verdict."""
        resp = client.post("/api/gatekeeper/check", json={
            "content": "Hello, just following up on our meeting yesterday.",
            "title": "Follow-up email",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "verdict" in data
        assert data["verdict"] in ("clear", "review", "hold")
        assert "summary" in data

    def test_gatekeeper_status(self, client):
        """GET /api/gatekeeper/status returns status."""
        resp = client.get("/api/gatekeeper/status")
        assert resp.status_code == 200

    def test_gatekeeper_history(self, client):
        """GET /api/gatekeeper/history returns history list."""
        resp = client.get("/api/gatekeeper/history")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "history" in data


# ═══════════════════════════════════════════════════════════════════
# Ecosystem (3)
# ═══════════════════════════════════════════════════════════════════

class TestEcosystem:

    def test_ecosystem_checks(self, client):
        """GET /api/ecosystem returns status with checked_at."""
        resp = client.get("/api/ecosystem")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "apps" in data
        assert "checked_at" in data
        assert "healthy" in data
        assert "total" in data

    def test_ecosystem_counts(self, client):
        """Ecosystem returns correct total count."""
        resp = client.get("/api/ecosystem")
        data = resp.get_json()
        assert data["total"] >= 10  # At least 10 registered apps
        assert data["healthy"] >= 0
        assert data["healthy"] <= data["total"]

    def test_ecosystem_self(self, client):
        """ELAINE reports own status in ecosystem."""
        resp = client.get("/api/ecosystem")
        data = resp.get_json()
        app_names = [a["name"] for a in data["apps"]]
        assert "ELAINE" in app_names


# ═══════════════════════════════════════════════════════════════════
# Voice (3)
# ═══════════════════════════════════════════════════════════════════

class TestVoice:

    def test_voice_status_endpoint(self, client):
        """GET /api/tts/status returns config with voice_id."""
        resp = client.get("/api/tts/status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "voice_id" in data
        assert "primary" in data
        assert data["primary"] == "ElevenLabs"

    def test_voice_elevenlabs_configured(self, client):
        """Voice config has correct ElevenLabs voice_id."""
        resp = client.get("/api/voice/config")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["voice_id"] == "XQanfahzbl1YiUlZi5NW"

    def test_voice_speak_endpoint(self, client):
        """POST /api/voice/speak returns audio or graceful error."""
        resp = client.post("/api/voice/speak", json={"text": "Good morning Mani"})
        # Either 200 (audio returned) or 503 (no TTS engine available)
        assert resp.status_code in (200, 503)
        if resp.status_code == 200:
            assert resp.content_type == "audio/mpeg"
        else:
            data = resp.get_json()
            assert "error" in data

    def test_voice_speak_empty(self, client):
        """POST /api/voice/speak with empty text returns 400."""
        resp = client.post("/api/voice/speak", json={"text": ""})
        assert resp.status_code == 400


# ═══════════════════════════════════════════════════════════════════
# Dashboard (3)
# ═══════════════════════════════════════════════════════════════════

class TestDashboard:

    def test_dashboard_renders(self, client):
        """GET / returns HTML with 'ELAINE'."""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.data.decode("utf-8")
        assert "ELAINE" in html
        assert "Chief of Staff" in html

    def test_dashboard_dark_theme(self, client):
        """Default theme is dark (#0A0E14)."""
        resp = client.get("/")
        html = resp.data.decode("utf-8")
        assert 'data-theme="dark"' in html
        assert "#0A0E14" in html or "#0A0E14".lower() in html.lower()

    def test_dashboard_toggle(self, client):
        """Toggle button exists in header."""
        resp = client.get("/")
        html = resp.data.decode("utf-8")
        assert "theme-toggle" in html
        assert "toggleTheme" in html


# ═══════════════════════════════════════════════════════════════════
# Tools & Services (2)
# ═══════════════════════════════════════════════════════════════════

class TestTools:

    def test_tools_registry(self, client):
        """GET /api/tools returns tool registry."""
        resp = client.get("/api/tools")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "tools" in data
        assert data["total"] > 0
        # Should include core tools
        tool_ids = [t["id"] for t in data["tools"]]
        assert "elaine" in tool_ids
        assert "genie" in tool_ids

    def test_frustration_log(self, client):
        """POST /api/frustration logs an entry."""
        resp = client.post("/api/frustration", json={
            "text": "Test frustration entry",
            "source": "test",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["logged"] is True


# ═══════════════════════════════════════════════════════════════════
# AI Engine Unit Tests (2)
# ═══════════════════════════════════════════════════════════════════

class TestAIEngine:

    def test_ai_engine_no_open_claude(self):
        """AI engine should NEVER suggest opening Claude."""
        from utils.ai_engine import check_ai_status
        status = check_ai_status()
        # Status should not contain any "open" instructions
        status_str = json.dumps(status).lower()
        assert "open claude" not in status_str
        assert "launch claude" not in status_str
        assert "start claude" not in status_str

    def test_ai_engine_has_ollama_fallback(self):
        """AI engine should have Ollama as fallback."""
        from utils.ai_engine import check_ai_status
        status = check_ai_status()
        assert "ollama" in status


# ═══════════════════════════════════════════════════════════════════
# Voice Engine Unit Tests (2)
# ═══════════════════════════════════════════════════════════════════

class TestVoiceEngine:

    def test_voice_engine_correct_id(self):
        """Voice engine must use correct ElevenLabs voice_id."""
        from utils.voice_engine import ELAINE_VOICE_ID
        assert ELAINE_VOICE_ID == "XQanfahzbl1YiUlZi5NW"

    def test_voice_engine_status(self):
        """Voice engine status reports configuration."""
        from utils.voice_engine import get_voice_status
        status = get_voice_status()
        assert status["voice_id"] == "XQanfahzbl1YiUlZi5NW"
        assert status["primary"] == "ElevenLabs"
        assert "model" in status
