"""
ELAINE Phase 4: Business Context Engine
Tracks clients, projects, relationships, and business intelligence
for Almost Magic Tech Lab.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


class BusinessContextEngine:
    """Core business intelligence and context management."""

    def __init__(self, db_path=None):
        self.db_path = db_path or str(Path.home() / ".elaine" / "business.db")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Clients
        c.execute("""CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT,
            email TEXT,
            phone TEXT,
            linkedin_url TEXT,
            industry TEXT,
            size TEXT,
            region TEXT DEFAULT 'AU',
            status TEXT DEFAULT 'prospect',
            tier TEXT DEFAULT 'standard',
            notes TEXT,
            tags TEXT,
            first_contact DATE,
            last_contact DATE,
            next_followup DATE,
            lifetime_value REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        # Interactions
        c.execute("""CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            type TEXT,
            channel TEXT,
            summary TEXT,
            sentiment TEXT,
            action_items TEXT,
            meeting_prep TEXT,
            meeting_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )""")
        # Projects
        c.execute("""CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            name TEXT NOT NULL,
            service_type TEXT,
            status TEXT DEFAULT 'planning',
            start_date DATE,
            end_date DATE,
            budget REAL,
            hours_estimated REAL,
            hours_actual REAL DEFAULT 0,
            deliverables TEXT,
            milestones TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )""")
        # Relationship Intelligence
        c.execute("""CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            contact_name TEXT,
            role TEXT,
            influence_level TEXT DEFAULT 'medium',
            relationship_strength TEXT DEFAULT 'new',
            notes TEXT,
            linkedin_url TEXT,
            last_interaction DATE,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )""")
        # Decision Log
        c.execute("""CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            context TEXT,
            options TEXT,
            decision TEXT,
            rationale TEXT,
            outcome TEXT,
            project_id INTEGER,
            client_id INTEGER,
            category TEXT,
            impact TEXT DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            review_date DATE,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )""")
        # Pipeline
        c.execute("""CREATE TABLE IF NOT EXISTS pipeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            opportunity TEXT NOT NULL,
            service_type TEXT,
            stage TEXT DEFAULT 'lead',
            probability REAL DEFAULT 0.1,
            estimated_value REAL,
            expected_close DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )""")
        conn.commit()
        conn.close()

    # --- Client Operations ---
    def add_client(self, name, company=None, email=None, phone=None,
                   linkedin_url=None, industry=None, size=None,
                   region='AU', status='prospect', tier='standard',
                   notes=None, tags=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT INTO clients
            (name, company, email, phone, linkedin_url, industry, size,
             region, status, tier, notes, tags, first_contact, last_contact)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, company, email, phone, linkedin_url, industry, size,
             region, status, tier, notes,
             json.dumps(tags) if tags else None,
             datetime.now().isoformat(), datetime.now().isoformat()))
        client_id = c.lastrowid
        conn.commit()
        conn.close()
        return client_id

    def get_client(self, client_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def search_clients(self, query):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT * FROM clients
            WHERE name LIKE ? OR company LIKE ? OR industry LIKE ? OR tags LIKE ?
            ORDER BY last_contact DESC""",
            (f"%{query}%",) * 4)
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_all_clients(self, status=None):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        if status:
            c.execute("SELECT * FROM clients WHERE status = ? ORDER BY last_contact DESC", (status,))
        else:
            c.execute("SELECT * FROM clients ORDER BY last_contact DESC")
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_client(self, client_id, **kwargs):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        kwargs['updated_at'] = datetime.now().isoformat()
        if 'tags' in kwargs and isinstance(kwargs['tags'], list):
            kwargs['tags'] = json.dumps(kwargs['tags'])
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [client_id]
        c.execute(f"UPDATE clients SET {sets} WHERE id = ?", vals)
        conn.commit()
        conn.close()

    # --- Interaction Operations ---
    def log_interaction(self, client_id, interaction_type, channel,
                        summary, sentiment=None, action_items=None,
                        meeting_prep=None, meeting_notes=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT INTO interactions
            (client_id, type, channel, summary, sentiment, action_items,
             meeting_prep, meeting_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (client_id, interaction_type, channel, summary, sentiment,
             json.dumps(action_items) if action_items else None,
             meeting_prep, meeting_notes))
        # Update last_contact on client
        c.execute("UPDATE clients SET last_contact = ? WHERE id = ?",
                  (datetime.now().isoformat(), client_id))
        conn.commit()
        conn.close()

    def get_interactions(self, client_id, limit=20):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT * FROM interactions
            WHERE client_id = ? ORDER BY created_at DESC LIMIT ?""",
            (client_id, limit))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # --- Project Operations ---
    def add_project(self, client_id, name, service_type=None, budget=None,
                    hours_estimated=None, start_date=None, deliverables=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT INTO projects
            (client_id, name, service_type, budget, hours_estimated,
             start_date, deliverables)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (client_id, name, service_type, budget, hours_estimated,
             start_date, json.dumps(deliverables) if deliverables else None))
        project_id = c.lastrowid
        conn.commit()
        conn.close()
        return project_id

    def get_active_projects(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT p.*, c.name as client_name, c.company
            FROM projects p LEFT JOIN clients c ON p.client_id = c.id
            WHERE p.status IN ('planning', 'active', 'review')
            ORDER BY p.start_date""")
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # --- Pipeline Operations ---
    def add_opportunity(self, client_id, opportunity, service_type=None,
                        estimated_value=None, expected_close=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT INTO pipeline
            (client_id, opportunity, service_type, estimated_value, expected_close)
            VALUES (?, ?, ?, ?, ?)""",
            (client_id, opportunity, service_type, estimated_value, expected_close))
        opp_id = c.lastrowid
        conn.commit()
        conn.close()
        return opp_id

    def get_pipeline(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT p.*, c.name as client_name, c.company
            FROM pipeline p LEFT JOIN clients c ON p.client_id = c.id
            WHERE p.stage NOT IN ('won', 'lost')
            ORDER BY p.expected_close""")
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_pipeline_value(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""SELECT
            SUM(estimated_value * probability) as weighted_value,
            SUM(estimated_value) as total_value,
            COUNT(*) as count
            FROM pipeline WHERE stage NOT IN ('won', 'lost')""")
        row = c.fetchone()
        conn.close()
        return {
            'weighted_value': row[0] or 0,
            'total_value': row[1] or 0,
            'count': row[2] or 0
        }

    # --- Decision Support ---
    def log_decision(self, title, context=None, options=None, decision=None,
                     rationale=None, project_id=None, client_id=None,
                     category=None, impact='medium'):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        review_date = (datetime.now() + timedelta(days=30)).isoformat()
        c.execute("""INSERT INTO decisions
            (title, context, options, decision, rationale, project_id,
             client_id, category, impact, review_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, context,
             json.dumps(options) if options else None,
             decision, rationale, project_id, client_id,
             category, impact, review_date))
        dec_id = c.lastrowid
        conn.commit()
        conn.close()
        return dec_id

    def get_decisions_for_review(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT * FROM decisions
            WHERE review_date <= ? AND outcome IS NULL
            ORDER BY impact DESC""",
            (datetime.now().isoformat(),))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # --- Dashboard Data ---
    def get_dashboard_summary(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Client counts by status
        c.execute("""SELECT status, COUNT(*) FROM clients GROUP BY status""")
        client_counts = dict(c.fetchall())

        # Active projects count
        c.execute("""SELECT COUNT(*) FROM projects
            WHERE status IN ('planning', 'active', 'review')""")
        active_projects = c.fetchone()[0]

        # Pipeline value
        pipeline = self.get_pipeline_value()

        # Overdue followups
        c.execute("""SELECT COUNT(*) FROM clients
            WHERE next_followup < ? AND next_followup IS NOT NULL""",
            (datetime.now().isoformat(),))
        overdue_followups = c.fetchone()[0]

        # Recent interactions (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        c.execute("""SELECT COUNT(*) FROM interactions
            WHERE created_at >= ?""", (week_ago,))
        recent_interactions = c.fetchone()[0]

        # Decisions pending review
        c.execute("""SELECT COUNT(*) FROM decisions
            WHERE review_date <= ? AND outcome IS NULL""",
            (datetime.now().isoformat(),))
        pending_decisions = c.fetchone()[0]

        conn.close()
        return {
            'clients': client_counts,
            'active_projects': active_projects,
            'pipeline': pipeline,
            'overdue_followups': overdue_followups,
            'recent_interactions': recent_interactions,
            'pending_decisions': pending_decisions
        }
