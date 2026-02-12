"""
Elaine v4 — Wisdom & Philosophy Routes
Proxies to Wisdom Quotes API (:3350) for daily quotes and philosophy search.

Almost Magic Tech Lab — Tool Integration
"""

import logging
import urllib.request
import urllib.parse
import json

from flask import Blueprint, jsonify, request

logger = logging.getLogger("elaine.wisdom")

WISDOM_API = "http://localhost:3350"

bp = Blueprint("wisdom", __name__)


@bp.route("/api/wisdom", methods=["GET"])
def daily_wisdom():
    """Get a random wisdom quote via the Wisdom Quotes API."""
    try:
        req = urllib.request.Request(f"{WISDOM_API}/api/quotes/random", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return jsonify(data)
    except Exception as e:
        logger.warning("Wisdom API unavailable: %s", e)
        return jsonify({
            "quote": "The only true wisdom is in knowing you know nothing.",
            "author": "Socrates",
            "source": "fallback",
        })


@bp.route("/api/philosophy-search", methods=["GET"])
def philosophy_search():
    """Search quotes by keyword via the Wisdom Quotes API."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "q parameter required"}), 400

    try:
        encoded = urllib.parse.quote(query)
        req = urllib.request.Request(
            f"{WISDOM_API}/api/quotes/search?q={encoded}", method="GET"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return jsonify(data)
    except Exception as e:
        logger.warning("Wisdom search failed: %s", e)
        return jsonify({"results": [], "query": query, "error": "Wisdom API unavailable"})
