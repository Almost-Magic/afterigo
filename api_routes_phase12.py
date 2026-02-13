"""
Elaine v4 — Phase 12 API Routes
Orchestrator: Cross-module intelligence wiring
Almost Magic Tech Lab
"""

from flask import Blueprint, jsonify, request

orchestrator_bp = Blueprint("orchestrator", __name__, url_prefix="/api/orchestrator")


def create_orchestrator_routes(orchestrator):

    @orchestrator_bp.route("/cascade/post-meeting/<meeting_id>", methods=["POST"])
    def post_meeting_cascade(meeting_id):
        """Full cascade after a meeting ends."""
        result = orchestrator.post_meeting_cascade(meeting_id)
        return jsonify(result)

    @orchestrator_bp.route("/cascade/discovery", methods=["POST"])
    def discovery_cascade():
        """Cascade a new discovery across modules."""
        data = request.get_json() or {}
        result = orchestrator.discovery_cascade(
            data.get("title", ""),
            data.get("so_what", ""),
            data.get("territory", ""),
            data.get("actionability", "act"),
        )
        return jsonify(result)

    @orchestrator_bp.route("/cascade/content-review", methods=["POST"])
    def content_review():
        """Send content through Sentinel before publishing."""
        data = request.get_json() or {}
        result = orchestrator.content_to_sentinel_review(
            data.get("content", ""),
            data.get("title", ""),
            data.get("is_public", True),
        )
        return jsonify(result)

    @orchestrator_bp.route("/cascade/analyse", methods=["POST"])
    def analyse():
        """Run Thinking Frameworks on any topic."""
        data = request.get_json() or {}
        result = orchestrator.analyse_decision(
            data.get("topic", ""),
            data.get("domain", "strategy"),
            data.get("stakes", "high"),
        )
        return jsonify(result)

    @orchestrator_bp.route("/log", methods=["GET"])
    def cascade_log():
        limit = request.args.get("limit", 50, type=int)
        return jsonify(orchestrator.get_cascade_log(limit))

    @orchestrator_bp.route("/wiring", methods=["GET"])
    def wiring():
        return jsonify(orchestrator.get_wiring_diagram())

    @orchestrator_bp.route("/status", methods=["GET"])
    def orchestrator_status():
        return jsonify(orchestrator.status())

    # ── External App Delegation ──────────────────────────────────

    @orchestrator_bp.route("/delegate", methods=["POST"])
    def delegate():
        """Delegate a task to an external AMTL app.
        Body: {"app": "writer", "task_type": "write_draft", "payload": {...}, "priority": "normal"}
        """
        data = request.get_json() or {}
        app_id = data.get("app", "")
        task_type = data.get("task_type", "")
        payload = data.get("payload", {})
        priority = data.get("priority", "normal")
        if not app_id or not task_type:
            return jsonify({"error": "app and task_type are required"}), 400
        result = orchestrator.delegate_task(app_id, task_type, payload, priority)
        if "error" in result and "known_apps" in result:
            return jsonify(result), 400
        return jsonify(result)

    @orchestrator_bp.route("/delegate/write", methods=["POST"])
    def delegate_write():
        """Shortcut: delegate writing to CK Writer.
        Body: {"content_type": "blog", "topic": "...", "notes": "", "tone": "professional"}
        """
        data = request.get_json() or {}
        return jsonify(orchestrator.delegate_writing(
            data.get("content_type", "blog"),
            data.get("topic", ""),
            data.get("notes", ""),
            data.get("tone", "professional"),
        ))

    @orchestrator_bp.route("/delegate/learn", methods=["POST"])
    def delegate_learn():
        """Shortcut: delegate learning session.
        Body: {"skill": "...", "context": ""}
        """
        data = request.get_json() or {}
        return jsonify(orchestrator.delegate_learning(
            data.get("skill", ""),
            data.get("context", ""),
        ))

    @orchestrator_bp.route("/delegate/brand", methods=["POST"])
    def delegate_brand():
        """Shortcut: delegate brand audit to Peterman.
        Body: {"url": "", "topic": ""}
        """
        data = request.get_json() or {}
        return jsonify(orchestrator.delegate_brand_check(
            data.get("url", ""),
            data.get("topic", ""),
        ))

    @orchestrator_bp.route("/delegate/model", methods=["POST"])
    def delegate_model():
        """Shortcut: delegate mental model analysis to Costanza.
        Body: {"situation": "...", "model": "auto"}
        """
        data = request.get_json() or {}
        return jsonify(orchestrator.delegate_mental_model(
            data.get("situation", ""),
            data.get("model", "auto"),
        ))

    @orchestrator_bp.route("/delegate/financial", methods=["POST"])
    def delegate_financial():
        """Shortcut: delegate financial query to Genie.
        Body: {"query_type": "summary", "period": "this_month"}
        """
        data = request.get_json() or {}
        return jsonify(orchestrator.delegate_financial(
            data.get("query_type", "summary"),
            data.get("period", "this_month"),
        ))

    @orchestrator_bp.route("/delegate/tasks", methods=["GET"])
    def delegated_tasks():
        """List recent delegated tasks."""
        limit = request.args.get("limit", 20, type=int)
        app_id = request.args.get("app", None)
        return jsonify({"tasks": orchestrator.get_delegated_tasks(limit, app_id)})

    @orchestrator_bp.route("/apps", methods=["GET"])
    def external_apps():
        """Check which external AMTL apps are reachable."""
        return jsonify(orchestrator.get_app_status())

    return orchestrator_bp
