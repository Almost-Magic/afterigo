"""
Peterman V4.1 — Database Models & Initialization
Almost Magic Tech Lab Pty Ltd

PostgreSQL + pgvector for embeddings.
"""

import os
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from pgvector.sqlalchemy import Vector

db = SQLAlchemy()

# Environment configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/peterman")


def get_db_path():
    """Return database connection info for Peterman."""
    return DATABASE_URL


def init_db(app):
    """Initialize database with Flask app."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
    print(f"   ✓ Database initialized: {DATABASE_URL}")
