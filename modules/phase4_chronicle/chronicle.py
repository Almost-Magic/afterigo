"""
ELAINE Phase 4: Chronicle — Meeting Intelligence
Pre-meeting prep + post-meeting synthesis. NO recording.

Provides context before meetings and structured capture after.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


class ChronicleEngine:
    """Meeting intelligence without recording."""

    def __init__(self, db_path=None):
        self.db_path = db_path or str(Path.home() / ".elaine" / "chronicle.db")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            meeting_type TEXT DEFAULT 'client',
            attendees TEXT,
            client_id INTEGER,
            project_id INTEGER,
            scheduled_at TIMESTAMP,
            duration_minutes INTEGER DEFAULT 60,
            location TEXT,
            meeting_link TEXT,
            status TEXT DEFAULT 'scheduled',
            prep_notes TEXT,
            agenda TEXT,
            objectives TEXT,
            post_notes TEXT,
            action_items TEXT,
            decisions TEXT,
            key_takeaways TEXT,
            follow_up_date DATE,
            sentiment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        # Meeting templates
        c.execute("""CREATE TABLE IF NOT EXISTS meeting_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            meeting_type TEXT,
            default_agenda TEXT,
            default_objectives TEXT,
            default_duration INTEGER DEFAULT 60,
            prep_checklist TEXT,
            post_checklist TEXT
        )""")

        # Attendee intelligence
        c.execute("""CREATE TABLE IF NOT EXISTS attendee_intel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER,
            name TEXT NOT NULL,
            role TEXT,
            company TEXT,
            linkedin_url TEXT,
            background TEXT,
            talking_points TEXT,
            previous_interactions TEXT,
            notes TEXT,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        )""")

        conn.commit()
        conn.close()
        self._seed_templates()

    def _seed_templates(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM meeting_templates")
        if c.fetchone()[0] == 0:
            templates = [
                ("Discovery Call", "prospect",
                 json.dumps(["Introductions", "Understand their challenges",
                             "Present relevant services", "Q&A", "Next steps"]),
                 json.dumps(["Qualify the prospect", "Identify pain points",
                             "Determine budget/timeline"]),
                 45,
                 json.dumps(["Research company on LinkedIn", "Check for news",
                             "Review their website", "Prepare case studies"]),
                 json.dumps(["Send follow-up email", "Update CRM",
                             "Create proposal if qualified"])),
                ("AI Governance Assessment", "client",
                 json.dumps(["Review current AI usage", "Identify shadow AI",
                             "Risk assessment", "Gap analysis",
                             "Recommendations", "Implementation roadmap"]),
                 json.dumps(["Complete assessment", "Identify quick wins",
                             "Scope remediation project"]),
                 90,
                 json.dumps(["Review ISO 42001 requirements", "Prepare assessment template",
                             "Research industry-specific AI risks"]),
                 json.dumps(["Generate assessment report", "Send recommendations",
                             "Schedule follow-up", "Create project proposal"])),
                ("Cybersecurity Review", "client",
                 json.dumps(["Current posture review", "Threat landscape update",
                             "Incident review", "Policy updates",
                             "Training needs", "Budget planning"]),
                 json.dumps(["Review security posture", "Identify improvements",
                             "Plan next quarter"]),
                 60,
                 json.dumps(["Pull latest ACSC advisories", "Review client's sector threats",
                             "Check Essential Eight compliance status"]),
                 json.dumps(["Update security roadmap", "Send meeting summary",
                             "Schedule remediation tasks"])),
                ("Board Advisory", "advisory",
                 json.dumps(["Strategic update", "Risk register review",
                             "Technology roadmap", "Budget review",
                             "Governance matters", "Open discussion"]),
                 json.dumps(["Provide strategic guidance", "Review risks",
                             "Approve roadmap"]),
                 120,
                 json.dumps(["Prepare board pack", "Review financials",
                             "Update risk register", "Prepare strategic recommendations"]),
                 json.dumps(["Distribute minutes", "Update action register",
                             "File board papers"])),
                ("Content Strategy Session", "internal",
                 json.dumps(["Content calendar review", "Performance metrics",
                             "Topic brainstorm", "Platform strategy",
                             "Upcoming campaigns", "Resource planning"]),
                 json.dumps(["Plan next month's content", "Review what's working"]),
                 60,
                 json.dumps(["Pull analytics", "Review trending topics",
                             "Check competitor content"]),
                 json.dumps(["Update content calendar", "Create briefs",
                             "Schedule production"])),
            ]
            for t in templates:
                c.execute("""INSERT INTO meeting_templates
                    (name, meeting_type, default_agenda, default_objectives,
                     default_duration, prep_checklist, post_checklist)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""", t)
            conn.commit()
        conn.close()

    # ─── Meeting Operations ───
    def create_meeting(self, title, meeting_type='client',
                       attendees=None, client_id=None, project_id=None,
                       scheduled_at=None, duration_minutes=60,
                       location=None, meeting_link=None,
                       template_name=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        agenda = None
        objectives = None
        prep_notes = None

        # Apply template if specified
        if template_name:
            c.execute("SELECT * FROM meeting_templates WHERE name = ?",
                      (template_name,))
            tmpl = c.fetchone()
            if tmpl:
                agenda = tmpl[3]      # default_agenda
                objectives = tmpl[4]  # default_objectives
                if not duration_minutes:
                    duration_minutes = tmpl[5]

        c.execute("""INSERT INTO meetings
            (title, meeting_type, attendees, client_id, project_id,
             scheduled_at, duration_minutes, location, meeting_link,
             agenda, objectives)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, meeting_type,
             json.dumps(attendees) if attendees else None,
             client_id, project_id, scheduled_at, duration_minutes,
             location, meeting_link, agenda, objectives))
        meeting_id = c.lastrowid
        conn.commit()
        conn.close()
        return meeting_id

    def get_meeting(self, meeting_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_upcoming_meetings(self, days=7):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        future = (datetime.now() + timedelta(days=days)).isoformat()
        c.execute("""SELECT * FROM meetings
            WHERE scheduled_at >= ? AND scheduled_at <= ?
            AND status = 'scheduled'
            ORDER BY scheduled_at""",
            (datetime.now().isoformat(), future))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ─── Pre-Meeting Prep ───
    def generate_prep(self, meeting_id, business_context=None):
        """Generate pre-meeting preparation package."""
        meeting = self.get_meeting(meeting_id)
        if not meeting:
            return None

        prep = {
            'meeting': meeting,
            'agenda': json.loads(meeting['agenda']) if meeting.get('agenda') else [],
            'objectives': json.loads(meeting['objectives']) if meeting.get('objectives') else [],
            'attendee_intel': [],
            'client_context': None,
            'previous_interactions': [],
            'talking_points': [],
            'risks_to_discuss': [],
        }

        # Get attendee intelligence
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM attendee_intel WHERE meeting_id = ?",
                  (meeting_id,))
        prep['attendee_intel'] = [dict(r) for r in c.fetchall()]
        conn.close()

        # Pull client context if business_context engine available
        if business_context and meeting.get('client_id'):
            client = business_context.get_client(meeting['client_id'])
            if client:
                prep['client_context'] = client
                prep['previous_interactions'] = business_context.get_interactions(
                    meeting['client_id'], limit=5
                )

        return prep

    # ─── Post-Meeting Capture ───
    def capture_post_meeting(self, meeting_id, notes=None,
                              action_items=None, decisions=None,
                              key_takeaways=None, sentiment=None,
                              follow_up_date=None):
        """Capture post-meeting notes and intelligence."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""UPDATE meetings SET
            post_notes = ?,
            action_items = ?,
            decisions = ?,
            key_takeaways = ?,
            sentiment = ?,
            follow_up_date = ?,
            status = 'completed',
            updated_at = ?
            WHERE id = ?""",
            (notes,
             json.dumps(action_items) if action_items else None,
             json.dumps(decisions) if decisions else None,
             json.dumps(key_takeaways) if key_takeaways else None,
             sentiment, follow_up_date,
             datetime.now().isoformat(), meeting_id))
        conn.commit()
        conn.close()

    def add_attendee_intel(self, meeting_id, name, role=None,
                           company=None, linkedin_url=None,
                           background=None, talking_points=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT INTO attendee_intel
            (meeting_id, name, role, company, linkedin_url,
             background, talking_points)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (meeting_id, name, role, company, linkedin_url,
             background,
             json.dumps(talking_points) if talking_points else None))
        intel_id = c.lastrowid
        conn.commit()
        conn.close()
        return intel_id

    def get_templates(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM meeting_templates")
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_pending_action_items(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT id, title, action_items, follow_up_date
            FROM meetings
            WHERE action_items IS NOT NULL
            AND status = 'completed'
            ORDER BY follow_up_date""")
        rows = c.fetchall()
        conn.close()

        items = []
        for row in rows:
            try:
                actions = json.loads(row['action_items'])
                for action in actions:
                    items.append({
                        'meeting_id': row['id'],
                        'meeting_title': row['title'],
                        'action': action,
                        'follow_up_date': row['follow_up_date']
                    })
            except (json.JSONDecodeError, TypeError):
                pass
        return items
