"""
Peterman V4.1 — The Authority & Presence Engine
Almost Magic Tech Lab Pty Ltd

Backend API server (Flask + PostgreSQL + pgvector)
Port: 5008
"""

import os
import sys
from pathlib import Path
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

# Import routes - PETERMAN routes only (Genie accounting routes disabled)
from backend.routes.health import health_bp
# dashboard_bp - Genie accounting - DISABLED
# machine_bp - Genie accounting - DISABLED
# settings_bp - Genie accounting - DISABLED
# audit_bp - Genie accounting - DISABLED
from backend.routes.brands import brands_bp
from backend.routes.perception import perception_bp
from backend.routes.semantic import semantic_bp
from backend.routes.vectormap import vectormap_bp
from backend.routes.authority import authority_bp
from backend.routes.survivability import survivability_bp
from backend.routes.amplifier import amplifier_bp
from backend.routes.proof import proof_bp
from backend.routes.oracle import oracle_bp
from backend.routes.forge import forge_bp
from backend.routes.seo_ask import seo_ask_bp
from backend.routes.browser import browser_bp
# settings, audit, dashboard, machine - all Genie accounting - DISABLED
from backend.models.database import db, get_db_path

# ── App Setup ──────────────────────────────────────────────
app = Flask(__name__, static_folder="static")
app.config["APP_NAME"] = "Peterman"
app.config["APP_VERSION"] = "4.1.0"
app.config["APP_PORT"] = 5008

# Database config
database_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/peterman")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# CORS
CORS(app, origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5008", "file://"])

# Register Blueprints - PETERMAN routes only
app.register_blueprint(health_bp)
app.register_blueprint(brands_bp)
app.register_blueprint(perception_bp)
app.register_blueprint(semantic_bp)
app.register_blueprint(vectormap_bp)
app.register_blueprint(authority_bp)
app.register_blueprint(survivability_bp)
app.register_blueprint(amplifier_bp)
app.register_blueprint(proof_bp)
app.register_blueprint(oracle_bp)
app.register_blueprint(forge_bp)
app.register_blueprint(seo_ask_bp)
app.register_blueprint(browser_bp)
# settings_bp, audit_bp, dashboard_bp, machine_bp - Genie accounting - DISABLED


# ── Serve Static Files (Frontend) ─────────────────────────
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)


# ── Error Handlers ─────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "message": str(e)}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error", "message": str(e)}), 500


# ── CLI Commands ───────────────────────────────────────────
@app.cli.command("init-db")
def init_db_command():
    """Initialize the database."""
    from backend.models import db
    db.create_all()
    print(f"✓ Database initialized: {get_db_path()}")


# ── Startup ────────────────────────────────────────────────
if __name__ == "__main__":
    # Database initialization
    with app.app_context():
        try:
            from backend.models import db
            db.create_all()
            print("[OK] Database ready")
        except Exception as e:
            print(f"[WARN] Database not available: {e}")
            print("       Run PostgreSQL or use SQLite for testing")
    
    print("\n=== Peterman V4.1 - The Authority & Presence Engine ===")
    print(f"   Dashboard: http://localhost:5008")
    
    app.run(host="0.0.0.0", port=5008, debug=True)
