"""
ELAINE v3 — Phase 4: Business Intelligence Module
Business Context Engine, Relationship Intelligence, Decision Support, Project Orchestration.
All data stored in SQLite for local-first privacy.
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger("elaine.business_intelligence")

DB_PATH = Path.home() / "elaine-v3" / "data" / "business_intel.db"


def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all Business Intelligence tables."""
    conn = get_db()
    conn.executescript("""
        -- ═══════════════════════════════════════════
        -- BUSINESS CONTEXT ENGINE
        -- ═══════════════════════════════════════════

        CREATE TABLE IF NOT EXISTS business_context (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            key TEXT NOT NULL UNIQUE,
            value TEXT NOT NULL,
            metadata TEXT DEFAULT '{}',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Seed AMTL business context
        INSERT OR IGNORE INTO business_context (category, key, value) VALUES
            ('company', 'name', 'Almost Magic Tech Lab'),
            ('company', 'founder', 'Mani Padisetti'),
            ('company', 'role', 'Curator'),
            ('company', 'entity_type', 'AI-native consulting firm'),
            ('company', 'launch_date', '2026-02-01'),
            ('company', 'market', 'Australia and New Zealand'),
            ('company', 'target_market', '250,000 SMBs in ANZ'),
            ('company', 'strategy', 'Building in public'),
            ('certifications', 'iso_42001', 'AI Management System'),
            ('certifications', 'iso_27001', 'Information Security'),
            ('certifications', 'cgeit', 'Governance of Enterprise IT'),
            ('services', 'ai_governance', 'AI governance consulting and implementation'),
            ('services', 'cybersecurity', 'Cybersecurity assessment and advisory'),
            ('services', 'business_intelligence', 'Business intelligence and analytics'),
            ('services', 'digital_transformation', 'Digital transformation consulting'),
            ('products', 'harvest', 'Project management platform with 12 Pillars of Intelligence'),
            ('products', 'energy_intel', 'Energy Intelligence Platform for Australian energy market'),
            ('products', 'identity_atlas', 'Intelligence gathering platform'),
            ('products', 'signal', 'LinkedIn intelligence and governance filter'),
            ('products', 'ck', 'Your Life OS — personal operating system'),
            ('products', 'secureflow', 'Cybersecurity applications suite'),
            ('products', 'opencyber', 'Cybersecurity research platform'),
            ('education', 'harvard', 'Executive education'),
            ('education', 'mit', 'Executive education'),
            ('education', 'wharton', 'Executive education'),
            ('education', 'imd', 'Executive education');

        -- ═══════════════════════════════════════════
        -- RELATIONSHIP INTELLIGENCE (CRM-lite)
        -- ═══════════════════════════════════════════

        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT DEFAULT '',
            role TEXT DEFAULT '',
            email TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            linkedin TEXT DEFAULT '',
            category TEXT DEFAULT 'prospect',
            warmth INTEGER DEFAULT 3,
            notes TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            first_contact DATE,
            last_contact DATE,
            next_followup DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            interaction_type TEXT NOT NULL,
            channel TEXT DEFAULT 'email',
            summary TEXT NOT NULL,
            sentiment TEXT DEFAULT 'neutral',
            action_items TEXT DEFAULT '[]',
            occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_interactions_contact
            ON interactions(contact_id);
        CREATE INDEX IF NOT EXISTS idx_contacts_category
            ON contacts(category);
        CREATE INDEX IF NOT EXISTS idx_contacts_next_followup
            ON contacts(next_followup);

        -- ═══════════════════════════════════════════
        -- DECISION SUPPORT (Decision Journal)
        -- ═══════════════════════════════════════════

        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            context TEXT NOT NULL,
            options TEXT DEFAULT '[]',
            chosen_option TEXT DEFAULT '',
            reasoning TEXT DEFAULT '',
            expected_outcome TEXT DEFAULT '',
            actual_outcome TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            category TEXT DEFAULT 'business',
            confidence INTEGER DEFAULT 5,
            reversibility TEXT DEFAULT 'medium',
            impact TEXT DEFAULT 'medium',
            review_date DATE,
            decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_decisions_status
            ON decisions(status);

        -- ═══════════════════════════════════════════
        -- PROJECT ORCHESTRATION
        -- ═══════════════════════════════════════════

        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE,
            description TEXT DEFAULT '',
            status TEXT DEFAULT 'active',
            priority INTEGER DEFAULT 3,
            category TEXT DEFAULT 'product',
            start_date DATE,
            target_date DATE,
            progress INTEGER DEFAULT 0,
            health TEXT DEFAULT 'green',
            notes TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            due_date DATE,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS project_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            update_text TEXT NOT NULL,
            update_type TEXT DEFAULT 'progress',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        -- Seed AMTL projects
        INSERT OR IGNORE INTO projects (name, code, description, status, category) VALUES
            ('Elaine', 'ELAINE', 'AI Chief of Staff — orchestration platform', 'active', 'product'),
            ('Harvest', 'HARVEST', 'Project management with 12 Pillars of Intelligence', 'planning', 'product'),
            ('Energy Intel', 'EIP', 'Energy Intelligence Platform for AU market', 'planning', 'product'),
            ('Identity Atlas', 'IDATLAS', 'Intelligence gathering platform', 'planning', 'product'),
            ('Signal', 'SIGNAL', 'LinkedIn intelligence and governance filter', 'planning', 'product'),
            ('CK Life OS', 'CK', 'Personal operating system — 90 tools, 28 modules', 'active', 'product'),
            ('SecureFlow', 'SECFLOW', 'Cybersecurity applications suite', 'planning', 'product'),
            ('OpenCyber', 'OCYBER', 'Cybersecurity research platform', 'planning', 'product'),
            ('AMTL Website', 'WEB', 'Company website and content', 'active', 'marketing'),
            ('LinkedIn Strategy', 'LINKEDIN', 'Building in public content strategy', 'active', 'marketing');
    """)
    conn.commit()
    conn.close()
    logger.info("Business Intelligence database initialised")


# ═══════════════════════════════════════════════════════════
# BUSINESS CONTEXT ENGINE
# ═══════════════════════════════════════════════════════════

class BusinessContext:
    """Knows everything about AMTL — services, products, certifications, strategy."""

    @staticmethod
    def get(category=None, key=None):
        conn = get_db()
        if key:
            row = conn.execute(
                "SELECT value, metadata FROM business_context WHERE key = ?", (key,)
            ).fetchone()
            conn.close()
            return dict(row) if row else None
        elif category:
            rows = conn.execute(
                "SELECT key, value FROM business_context WHERE category = ?", (category,)
            ).fetchall()
            conn.close()
            return {r["key"]: r["value"] for r in rows}
        else:
            rows = conn.execute(
                "SELECT category, key, value FROM business_context"
            ).fetchall()
            conn.close()
            result = {}
            for r in rows:
                result.setdefault(r["category"], {})[r["key"]] = r["value"]
            return result

    @staticmethod
    def set(category, key, value, metadata=None):
        conn = get_db()
        conn.execute(
            """INSERT INTO business_context (category, key, value, metadata, updated_at)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(key) DO UPDATE SET
                   value = excluded.value,
                   metadata = excluded.metadata,
                   updated_at = CURRENT_TIMESTAMP""",
            (category, key, value, json.dumps(metadata or {})),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_context_prompt():
        """Generate a context block for Ollama system prompts."""
        ctx = BusinessContext.get()
        lines = ["Business Context for Almost Magic Tech Lab:"]
        for cat, items in ctx.items():
            lines.append(f"\n{cat.upper()}:")
            for k, v in items.items():
                lines.append(f"  - {k}: {v}")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════
# RELATIONSHIP INTELLIGENCE
# ═══════════════════════════════════════════════════════════

class RelationshipIntelligence:
    """CRM-lite for tracking contacts, interactions, and follow-ups."""

    @staticmethod
    def add_contact(name, **kwargs):
        conn = get_db()
        fields = ["name"]
        values = [name]
        for k in ["company", "role", "email", "phone", "linkedin",
                   "category", "warmth", "notes", "first_contact"]:
            if k in kwargs:
                fields.append(k)
                values.append(kwargs[k])
        placeholders = ", ".join(["?"] * len(values))
        field_str = ", ".join(fields)
        conn.execute(f"INSERT INTO contacts ({field_str}) VALUES ({placeholders})", values)
        conn.commit()
        cid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        return cid

    @staticmethod
    def log_interaction(contact_id, interaction_type, summary, channel="email", sentiment="neutral"):
        conn = get_db()
        conn.execute(
            """INSERT INTO interactions (contact_id, interaction_type, channel, summary, sentiment)
               VALUES (?, ?, ?, ?, ?)""",
            (contact_id, interaction_type, channel, summary, sentiment),
        )
        conn.execute(
            "UPDATE contacts SET last_contact = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (contact_id,),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_contacts(category=None, limit=50):
        conn = get_db()
        if category:
            rows = conn.execute(
                "SELECT * FROM contacts WHERE category = ? ORDER BY updated_at DESC LIMIT ?",
                (category, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM contacts ORDER BY updated_at DESC LIMIT ?", (limit,)
            ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_followups_due(days_ahead=7):
        conn = get_db()
        cutoff = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        rows = conn.execute(
            """SELECT * FROM contacts
               WHERE next_followup IS NOT NULL AND next_followup <= ?
               ORDER BY next_followup ASC""",
            (cutoff,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def search_contacts(query):
        conn = get_db()
        pattern = f"%{query}%"
        rows = conn.execute(
            """SELECT * FROM contacts
               WHERE name LIKE ? OR company LIKE ? OR notes LIKE ? OR role LIKE ?
               ORDER BY updated_at DESC LIMIT 20""",
            (pattern, pattern, pattern, pattern),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_contact_history(contact_id, limit=20):
        conn = get_db()
        contact = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
        interactions = conn.execute(
            "SELECT * FROM interactions WHERE contact_id = ? ORDER BY occurred_at DESC LIMIT ?",
            (contact_id, limit),
        ).fetchall()
        conn.close()
        return {
            "contact": dict(contact) if contact else None,
            "interactions": [dict(i) for i in interactions],
        }


# ═══════════════════════════════════════════════════════════
# DECISION SUPPORT
# ═══════════════════════════════════════════════════════════

class DecisionSupport:
    """Structured decision journal with review cycle."""

    @staticmethod
    def log_decision(title, context, options=None, chosen=None, reasoning=None,
                     category="business", confidence=5, reversibility="medium", impact="medium"):
        conn = get_db()
        review_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        conn.execute(
            """INSERT INTO decisions
               (title, context, options, chosen_option, reasoning, category,
                confidence, reversibility, impact, review_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, context, json.dumps(options or []), chosen or "",
             reasoning or "", category, confidence, reversibility, impact, review_date),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_pending_reviews():
        conn = get_db()
        rows = conn.execute(
            """SELECT * FROM decisions
               WHERE status = 'pending' AND review_date <= date('now')
               ORDER BY review_date ASC""",
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def review_decision(decision_id, actual_outcome, status="reviewed"):
        conn = get_db()
        conn.execute(
            """UPDATE decisions SET actual_outcome = ?, status = ?, reviewed_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (actual_outcome, status, decision_id),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_decisions(category=None, status=None, limit=20):
        conn = get_db()
        query = "SELECT * FROM decisions WHERE 1=1"
        params = []
        if category:
            query += " AND category = ?"
            params.append(category)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]


# ═══════════════════════════════════════════════════════════
# PROJECT ORCHESTRATION
# ═══════════════════════════════════════════════════════════

class ProjectOrchestration:
    """Tracks all AMTL projects, milestones, and updates."""

    @staticmethod
    def get_projects(status=None, category=None):
        conn = get_db()
        query = "SELECT * FROM projects WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " ORDER BY priority ASC, name ASC"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_project(code):
        conn = get_db()
        row = conn.execute("SELECT * FROM projects WHERE code = ?", (code,)).fetchone()
        if not row:
            conn.close()
            return None
        project = dict(row)
        milestones = conn.execute(
            "SELECT * FROM milestones WHERE project_id = ? ORDER BY due_date ASC",
            (row["id"],),
        ).fetchall()
        updates = conn.execute(
            "SELECT * FROM project_updates WHERE project_id = ? ORDER BY created_at DESC LIMIT 10",
            (row["id"],),
        ).fetchall()
        conn.close()
        project["milestones"] = [dict(m) for m in milestones]
        project["recent_updates"] = [dict(u) for u in updates]
        return project

    @staticmethod
    def add_milestone(project_code, title, description="", due_date=None):
        conn = get_db()
        project = conn.execute("SELECT id FROM projects WHERE code = ?", (project_code,)).fetchone()
        if not project:
            conn.close()
            return None
        conn.execute(
            "INSERT INTO milestones (project_id, title, description, due_date) VALUES (?, ?, ?, ?)",
            (project["id"], title, description, due_date),
        )
        conn.commit()
        mid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        return mid

    @staticmethod
    def log_update(project_code, update_text, update_type="progress"):
        conn = get_db()
        project = conn.execute("SELECT id FROM projects WHERE code = ?", (project_code,)).fetchone()
        if not project:
            conn.close()
            return None
        conn.execute(
            "INSERT INTO project_updates (project_id, update_text, update_type) VALUES (?, ?, ?)",
            (project["id"], update_text, update_type),
        )
        conn.execute(
            "UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (project["id"],),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def update_progress(project_code, progress, health=None):
        conn = get_db()
        if health:
            conn.execute(
                "UPDATE projects SET progress = ?, health = ?, updated_at = CURRENT_TIMESTAMP WHERE code = ?",
                (progress, health, project_code),
            )
        else:
            conn.execute(
                "UPDATE projects SET progress = ?, updated_at = CURRENT_TIMESTAMP WHERE code = ?",
                (progress, project_code),
            )
        conn.commit()
        conn.close()

    @staticmethod
    def get_dashboard_summary():
        """Get a high-level summary for the morning briefing."""
        conn = get_db()
        active = conn.execute("SELECT COUNT(*) FROM projects WHERE status = 'active'").fetchone()[0]
        total = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
        overdue_milestones = conn.execute(
            """SELECT m.title, p.name, p.code, m.due_date
               FROM milestones m JOIN projects p ON m.project_id = p.id
               WHERE m.status = 'pending' AND m.due_date < date('now')
               ORDER BY m.due_date ASC LIMIT 10""",
        ).fetchall()
        upcoming_milestones = conn.execute(
            """SELECT m.title, p.name, p.code, m.due_date
               FROM milestones m JOIN projects p ON m.project_id = p.id
               WHERE m.status = 'pending' AND m.due_date >= date('now')
               ORDER BY m.due_date ASC LIMIT 10""",
        ).fetchall()
        red_projects = conn.execute(
            "SELECT name, code, health FROM projects WHERE health = 'red' AND status = 'active'"
        ).fetchall()
        conn.close()
        return {
            "active_projects": active,
            "total_projects": total,
            "overdue_milestones": [dict(m) for m in overdue_milestones],
            "upcoming_milestones": [dict(m) for m in upcoming_milestones],
            "at_risk_projects": [dict(p) for p in red_projects],
        }


# ═══════════════════════════════════════════════════════════
# NLU INTEGRATION — Route business commands
# ═══════════════════════════════════════════════════════════

def handle_business_command(text: str) -> dict | None:
    """
    Parse natural language business commands.
    Returns a response dict if handled, None if not a business command.
    """
    text_lower = text.lower().strip()

    # Project queries
    if any(kw in text_lower for kw in ["project status", "show projects", "my projects", "project dashboard"]):
        projects = ProjectOrchestration.get_projects(status="active")
        summary = ProjectOrchestration.get_dashboard_summary()
        lines = [f"📊 **Project Dashboard** — {summary['active_projects']} active of {summary['total_projects']} total\n"]
        for p in projects:
            health_icon = {"green": "🟢", "amber": "🟡", "red": "🔴"}.get(p["health"], "⚪")
            lines.append(f"{health_icon} **{p['name']}** [{p['code']}] — {p['progress']}% complete")
        if summary["overdue_milestones"]:
            lines.append(f"\n⚠️ **{len(summary['overdue_milestones'])} overdue milestones**")
            for m in summary["overdue_milestones"][:5]:
                lines.append(f"  • {m['title']} ({m['name']}) — due {m['due_date']}")
        return {"response": "\n".join(lines), "module": "project_orchestration"}

    # Contact queries
    if any(kw in text_lower for kw in ["show contacts", "my contacts", "who do i know", "crm"]):
        contacts = RelationshipIntelligence.get_contacts(limit=10)
        lines = [f"👥 **Contacts** — {len(contacts)} recent\n"]
        for c in contacts:
            warmth_bar = "🔥" * min(c["warmth"], 5)
            lines.append(f"• **{c['name']}** ({c['company']}) — {c['category']} {warmth_bar}")
        return {"response": "\n".join(lines), "module": "relationship_intelligence"}

    # Follow-up reminders
    if any(kw in text_lower for kw in ["follow up", "followup", "who should i follow up"]):
        followups = RelationshipIntelligence.get_followups_due(days_ahead=7)
        if not followups:
            return {"response": "✅ No follow-ups due in the next 7 days.", "module": "relationship_intelligence"}
        lines = ["📅 **Follow-ups Due:**\n"]
        for c in followups:
            lines.append(f"• **{c['name']}** ({c['company']}) — due {c['next_followup']}")
        return {"response": "\n".join(lines), "module": "relationship_intelligence"}

    # Decision journal
    if any(kw in text_lower for kw in ["decisions", "decision journal", "review decisions"]):
        pending = DecisionSupport.get_pending_reviews()
        recent = DecisionSupport.get_decisions(limit=5)
        lines = ["📓 **Decision Journal**\n"]
        if pending:
            lines.append(f"🔄 **{len(pending)} decisions due for review:**")
            for d in pending:
                lines.append(f"  • {d['title']} (decided {d['decided_at'][:10]})")
        lines.append(f"\n📝 **Recent decisions:**")
        for d in recent:
            status_icon = {"pending": "⏳", "reviewed": "✅", "revised": "🔄"}.get(d["status"], "•")
            lines.append(f"  {status_icon} {d['title']} — confidence: {d['confidence']}/10")
        return {"response": "\n".join(lines), "module": "decision_support"}

    # Business context / "about AMTL"
    if any(kw in text_lower for kw in ["about amtl", "about almost magic", "our services",
                                         "our products", "certifications", "what do we do"]):
        ctx = BusinessContext.get()
        lines = ["🏢 **Almost Magic Tech Lab**\n"]
        if "company" in ctx:
            for k, v in ctx["company"].items():
                lines.append(f"• {k.replace('_', ' ').title()}: {v}")
        if "certifications" in ctx:
            lines.append("\n🏅 **Certifications:**")
            for k, v in ctx["certifications"].items():
                lines.append(f"  • {k.upper()}: {v}")
        if "products" in ctx:
            lines.append("\n📦 **Products:**")
            for k, v in ctx["products"].items():
                lines.append(f"  • {k.replace('_', ' ').title()}: {v}")
        return {"response": "\n".join(lines), "module": "business_context"}

    return None


# Initialise on import
try:
    init_db()
except Exception as e:
    logger.error(f"Failed to initialise Business Intelligence DB: {e}")
