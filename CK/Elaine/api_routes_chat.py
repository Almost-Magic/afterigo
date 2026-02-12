"""
Elaine v4 — Chat + Tool Registry + Service Health Routes
Connects to Ollama via The Supervisor (:9000).
Ollama only — no cloud APIs.

Almost Magic Tech Lab
"""

from flask import Blueprint, jsonify, request
import json
import logging
import os
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

logger = logging.getLogger("elaine.chat")

SUPERVISOR_URL = os.environ.get("SUPERVISOR_URL", "http://localhost:9000")
LAN_IP = os.environ.get("ELAINE_LAN_IP", "192.168.4.55")

# ── AMTL Tool Registry ─────────────────────────────────────────

TOOLS = [
    {
        "id": "workshop",
        "name": "The Workshop",
        "desc": "Central launcher — App 0",
        "port": 5003,
        "url": f"http://{LAN_IP}:5003",
        "health": "/",
        "category": "core",
    },
    {
        "id": "supervisor",
        "name": "The Supervisor",
        "desc": "Runtime manager — GPU, models, health",
        "port": 9000,
        "url": f"http://{LAN_IP}:9000",
        "health": "/api/health",
        "category": "core",
    },
    {
        "id": "elaine",
        "name": "ELAINE",
        "desc": "Chief of Staff — 16 intelligence modules",
        "port": 5000,
        "url": f"http://{LAN_IP}:5000",
        "health": "/api/health",
        "category": "core",
    },
    {
        "id": "ripple",
        "name": "Ripple CRM",
        "desc": "Customer relationship management",
        "port": 3100,
        "url": f"http://{LAN_IP}:3100",
        "health": "/",
        "category": "business",
    },
    {
        "id": "ripple-api",
        "name": "Ripple CRM API",
        "desc": "CRM backend — contacts, deals, intelligence",
        "port": 8100,
        "url": f"http://{LAN_IP}:8100",
        "health": "/api/health",
        "category": "business",
    },
    {
        "id": "touchstone",
        "name": "Touchstone",
        "desc": "Marketing attribution engine",
        "port": 8200,
        "url": f"http://{LAN_IP}:8200",
        "health": "/api/v1/health",
        "category": "business",
    },
    {
        "id": "touchstone-dash",
        "name": "Touchstone Dashboard",
        "desc": "Attribution dashboard — 5 models, charts",
        "port": 3200,
        "url": f"http://{LAN_IP}:3200",
        "health": "/",
        "category": "business",
    },
    {
        "id": "writer",
        "name": "CK Writer",
        "desc": "8-mode writing studio",
        "port": 5004,
        "url": f"http://{LAN_IP}:5004",
        "health": "/",
        "category": "creative",
    },
    {
        "id": "author-studio",
        "name": "Author Studio",
        "desc": "Book authoring and publishing",
        "port": 5007,
        "url": f"http://{LAN_IP}:5007",
        "health": "/",
        "category": "creative",
    },
    {
        "id": "peterman",
        "name": "Peterman",
        "desc": "Brand intelligence — SEO, authority, presence",
        "port": 5008,
        "url": f"http://{LAN_IP}:5008",
        "health": "/api/health",
        "category": "business",
    },
    {
        "id": "genie",
        "name": "Genie",
        "desc": "AI bookkeeper — receipts, transactions, fraud guard",
        "port": 8000,
        "url": f"http://{LAN_IP}:8000",
        "health": "/api/health",
        "category": "finance",
    },
    {
        "id": "costanza",
        "name": "Costanza",
        "desc": "Mental models engine — 166 frameworks",
        "port": 5001,
        "url": f"http://{LAN_IP}:5001",
        "health": "/api/health",
        "category": "intelligence",
    },
    {
        "id": "learning",
        "name": "Learning Assistant",
        "desc": "Micro-skill training sessions",
        "port": 5002,
        "url": f"http://{LAN_IP}:5002",
        "health": "/api/health",
        "category": "learning",
    },
    {
        "id": "ollama",
        "name": "Ollama",
        "desc": "Local LLM inference engine",
        "port": 11434,
        "url": f"http://{LAN_IP}:11434",
        "health": "/api/tags",
        "category": "infra",
    },
    {
        "id": "n8n",
        "name": "n8n",
        "desc": "Workflow automation backbone",
        "port": 5678,
        "url": f"http://{LAN_IP}:5678",
        "health": "/",
        "category": "infra",
    },
]

# ── System Prompt for Ollama ────────────────────────────────────

TOOL_LIST_TEXT = "\n".join(
    f"- {t['name']} ({t['desc']}) — port {t['port']}, URL: {t['url']}"
    for t in TOOLS
)

SYSTEM_PROMPT = f"""You are Elaine, Chief of Staff for Mani Padisetti at Almost Magic Tech Lab.
Australian English. Direct, warm, no waffle. Under 150 words unless asked for detail.
You have 16 intelligence modules: Gravity (priorities), Constellation (people), Cartographer (markets), Amplifier (content), Sentinel (quality), Chronicle (meetings), Innovator (opportunities), Learning Radar, Gatekeeper, Compassion, plus Thinking/Communication/Strategic frameworks.
Key AMTL tools: Workshop (:5003), Genie (:8000), CK Writer (:5004), Ripple CRM (:3100/:8100), Supervisor (:9000), Ollama (:11434).
Reference Gravity for priorities, Constellation for people, Amplifier+Sentinel for content."""


def _ping_service(tool):
    """Ping a single tool's health endpoint. Returns (tool_id, status, latency_ms)."""
    url = f"http://localhost:{tool['port']}{tool['health']}"
    try:
        req = urllib.request.Request(url, method="GET")
        import time
        start = time.time()
        with urllib.request.urlopen(req, timeout=3) as resp:
            latency = int((time.time() - start) * 1000)
            if resp.status < 400:
                return (tool["id"], "running", latency)
    except Exception:
        pass
    return (tool["id"], "stopped", None)


def create_chat_routes():
    bp = Blueprint("chat", __name__)

    # ── POST /api/chat ────────────────────────────────────────────

    @bp.route("/api/chat", methods=["POST"])
    def chat():
        """
        Send a message to Ollama via The Supervisor.
        Body: {"message": "...", "model": "gemma2:27b"}
        """
        data = request.get_json(silent=True) or {}
        message = data.get("message", "").strip()
        if not message:
            return jsonify({"error": "message is required"}), 400

        model = data.get("model", "llama3.1:8b")
        history = data.get("history", [])

        # Build messages array for Ollama chat API
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for h in history[-10:]:  # Keep last 10 turns to fit context
            messages.append(h)
        messages.append({"role": "user", "content": message})

        # Build payload
        payload = json.dumps({
            "model": model,
            "messages": messages,
            "stream": False,
        }).encode("utf-8")

        # Route through Supervisor first (manages VRAM + model loading),
        # fall back to Ollama direct only if Supervisor is down.
        targets = [
            (f"{SUPERVISOR_URL}/api/chat", "supervisor"),
            ("http://localhost:11434/api/chat", "ollama-direct"),
        ]

        for url, via in targets:
            try:
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    result = json.loads(resp.read().decode("utf-8"))

                reply = ""
                if "message" in result:
                    reply = result["message"].get("content", "")
                elif "response" in result:
                    reply = result["response"]

                return jsonify({
                    "reply": reply,
                    "model": model,
                    "via": via,
                })
            except Exception as e:
                logger.warning(f"Chat via {via} failed: {e}")
                continue

        return jsonify({
            "error": "Cannot reach Ollama",
            "reply": "I can't reach Ollama right now. Check that Ollama (:11434) or The Supervisor (:9000) is running.",
            "via": "offline",
        }), 503

    # ── GET /api/tools ────────────────────────────────────────────

    @bp.route("/api/tools", methods=["GET"])
    def tools():
        """Return the AMTL tool registry."""
        return jsonify({
            "tools": TOOLS,
            "total": len(TOOLS),
            "lan_ip": LAN_IP,
        })

    # ── GET /api/tools/health ─────────────────────────────────────

    @bp.route("/api/tools/health", methods=["GET"])
    def tools_health():
        """Ping all tools and return health status."""
        results = {}
        running = 0

        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = {pool.submit(_ping_service, t): t for t in TOOLS}
            for future in as_completed(futures):
                tool_id, status, latency = future.result()
                results[tool_id] = {
                    "status": status,
                    "latency_ms": latency,
                }
                if status == "running":
                    running += 1

        return jsonify({
            "services": results,
            "running": running,
            "total": len(TOOLS),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    return bp
