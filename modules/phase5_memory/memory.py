"""
ELAINE Phase 5: Memory & Conversation Continuity
Persistent chat history, user preferences, and session state.
Elaine remembers across restarts.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


class MemoryEngine:
    """
    Persistent memory for Elaine.
    - Conversation history (survives restarts)
    - User preferences
    - Session state (last viewed panel, scroll position, etc.)
    - Context awareness (Elaine remembers what you asked before)
    """

    def __init__(self):
        self.home = Path.home() / ".elaine"
        self.home.mkdir(exist_ok=True)
        self.db_path = str(self.home / "memory.db")
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Conversation history
        c.execute("""CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            intent TEXT,
            entities TEXT,
            panel TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        # User preferences — persisted settings
        c.execute("""CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        # Session state — UI state that survives restarts
        c.execute("""CREATE TABLE IF NOT EXISTS session_state (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        # Command history — for autocomplete and frequency analysis
        c.execute("""CREATE TABLE IF NOT EXISTS command_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT,
            intent TEXT,
            success INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        # Context tags — Elaine tracks conversation topics
        c.execute("""CREATE TABLE IF NOT EXISTS context_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag TEXT,
            conversation_id INTEGER,
            weight REAL DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )""")

        conn.commit()
        conn.close()

    # ═══════════════════════════════════════════
    #  CONVERSATION HISTORY
    # ═══════════════════════════════════════════

    def add_message(self, role, content, intent=None, entities=None, panel=None):
        """Store a conversation message."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT INTO conversations
            (role, content, intent, entities, panel)
            VALUES (?, ?, ?, ?, ?)""",
            (role, content, intent,
             json.dumps(entities) if entities else None, panel))
        msg_id = c.lastrowid

        # Auto-extract context tags
        if content:
            tags = self._extract_tags(content)
            for tag in tags:
                c.execute("""INSERT INTO context_tags (tag, conversation_id)
                    VALUES (?, ?)""", (tag, msg_id))

        conn.commit()
        conn.close()
        return msg_id

    def get_history(self, limit=50, since=None):
        """Get conversation history."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        if since:
            c.execute("""SELECT * FROM conversations
                WHERE created_at >= ? ORDER BY created_at DESC LIMIT ?""",
                (since, limit))
        else:
            c.execute("SELECT * FROM conversations ORDER BY created_at DESC LIMIT ?",
                (limit,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return list(reversed(rows))  # Chronological order

    def get_recent_context(self, n=10):
        """Get the last N messages as context for Elaine's responses."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT role, content, intent, panel FROM conversations ORDER BY id DESC LIMIT ?", (n,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return list(reversed(rows))

    def search_history(self, query, limit=20):
        """Search conversation history."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT * FROM conversations
            WHERE content LIKE ? ORDER BY created_at DESC LIMIT ?""",
            (f"%{query}%", limit))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def get_conversation_stats(self):
        """Get conversation statistics."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM conversations")
        total = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM conversations WHERE role = 'user'")
        user_msgs = c.fetchone()[0]

        c.execute("SELECT MIN(created_at), MAX(created_at) FROM conversations")
        row = c.fetchone()
        first = row[0]
        last = row[1]

        # Most common intents
        c.execute("""SELECT intent, COUNT(*) as cnt FROM conversations
            WHERE intent IS NOT NULL GROUP BY intent ORDER BY cnt DESC LIMIT 10""")
        top_intents = dict(c.fetchall())

        # Most active topics
        c.execute("""SELECT tag, COUNT(*) as cnt FROM context_tags
            GROUP BY tag ORDER BY cnt DESC LIMIT 15""")
        top_tags = dict(c.fetchall())

        conn.close()
        return {
            "total_messages": total,
            "user_messages": user_msgs,
            "assistant_messages": total - user_msgs,
            "first_message": first,
            "last_message": last,
            "top_intents": top_intents,
            "top_topics": top_tags
        }

    def clear_history(self, before=None):
        """Clear conversation history, optionally before a date."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if before:
            c.execute("DELETE FROM context_tags WHERE conversation_id IN (SELECT id FROM conversations WHERE created_at < ?)", (before,))
            c.execute("DELETE FROM conversations WHERE created_at < ?", (before,))
        else:
            c.execute("DELETE FROM context_tags")
            c.execute("DELETE FROM conversations")
        conn.commit()
        conn.close()

    # ═══════════════════════════════════════════
    #  USER PREFERENCES
    # ═══════════════════════════════════════════

    def set_preference(self, key, value):
        """Set a user preference."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT OR REPLACE INTO preferences (key, value, updated_at)
            VALUES (?, ?, ?)""",
            (key, json.dumps(value) if not isinstance(value, str) else value,
             datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def get_preference(self, key, default=None):
        """Get a user preference."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT value FROM preferences WHERE key = ?", (key,))
        row = c.fetchone()
        conn.close()
        if row is None:
            return default
        try:
            return json.loads(row[0])
        except (json.JSONDecodeError, TypeError):
            return row[0]

    def get_all_preferences(self):
        """Get all preferences."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT key, value, updated_at FROM preferences ORDER BY key")
        prefs = {}
        for r in c.fetchall():
            try:
                prefs[r["key"]] = json.loads(r["value"])
            except (json.JSONDecodeError, TypeError):
                prefs[r["key"]] = r["value"]
        conn.close()
        return prefs

    def delete_preference(self, key):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM preferences WHERE key = ?", (key,))
        conn.commit()
        conn.close()

    # ═══════════════════════════════════════════
    #  SESSION STATE
    # ═══════════════════════════════════════════

    def set_state(self, key, value):
        """Set session state (UI state that persists across restarts)."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT OR REPLACE INTO session_state (key, value, updated_at)
            VALUES (?, ?, ?)""",
            (key, json.dumps(value) if not isinstance(value, str) else value,
             datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def get_state(self, key, default=None):
        """Get session state."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT value FROM session_state WHERE key = ?", (key,))
        row = c.fetchone()
        conn.close()
        if row is None:
            return default
        try:
            return json.loads(row[0])
        except (json.JSONDecodeError, TypeError):
            return row[0]

    def get_all_state(self):
        """Get all session state."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT key, value FROM session_state")
        state = {}
        for k, v in c.fetchall():
            try:
                state[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                state[k] = v
        conn.close()
        return state

    # ═══════════════════════════════════════════
    #  COMMAND HISTORY
    # ═══════════════════════════════════════════

    def log_command(self, command, intent=None, success=True):
        """Log a command for history and autocomplete."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT INTO command_history (command, intent, success)
            VALUES (?, ?, ?)""", (command, intent, 1 if success else 0))
        conn.commit()
        conn.close()

    def get_command_suggestions(self, prefix="", limit=10):
        """Get command suggestions based on history."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if prefix:
            c.execute("""SELECT command, COUNT(*) as freq FROM command_history
                WHERE command LIKE ? AND success = 1
                GROUP BY command ORDER BY freq DESC LIMIT ?""",
                (f"{prefix}%", limit))
        else:
            c.execute("""SELECT command, COUNT(*) as freq FROM command_history
                WHERE success = 1
                GROUP BY command ORDER BY freq DESC LIMIT ?""", (limit,))
        results = [{"command": r[0], "frequency": r[1]} for r in c.fetchall()]
        conn.close()
        return results

    def get_frequent_commands(self, limit=10):
        """Get most frequently used commands."""
        return self.get_command_suggestions(limit=limit)

    # ═══════════════════════════════════════════
    #  CONTEXT AWARENESS
    # ═══════════════════════════════════════════

    def get_active_topics(self, hours=24):
        """Get topics discussed in recent conversations."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        c.execute("""SELECT tag, SUM(weight) as total FROM context_tags
            WHERE created_at >= ?
            GROUP BY tag ORDER BY total DESC LIMIT 20""", (since,))
        topics = [{"topic": r[0], "weight": r[1]} for r in c.fetchall()]
        conn.close()
        return topics

    def is_followup(self, content):
        """Detect if a message is a follow-up to a previous conversation."""
        followup_markers = [
            "also", "and", "another thing", "what about",
            "one more", "additionally", "by the way",
            "regarding", "about that", "going back to",
            "following up", "as I said", "like I mentioned",
            "the same", "that one", "it", "that", "this"
        ]
        content_lower = content.lower().strip()

        # Short messages starting with these are likely follow-ups
        if len(content_lower.split()) <= 5:
            for marker in followup_markers:
                if content_lower.startswith(marker):
                    return True

        # Pronouns without context suggest follow-up
        if content_lower.startswith(("it ", "that ", "this ", "they ", "he ", "she ")):
            return True

        return False

    def get_last_topic_context(self):
        """Get the context of the last conversation topic."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT * FROM conversations
            ORDER BY id DESC LIMIT 5""")
        recent = [dict(r) for r in c.fetchall()]
        conn.close()

        if not recent:
            return None

        return {
            "last_intent": recent[0].get("intent") if recent else None,
            "last_panel": recent[0].get("panel") if recent else None,
            "recent_messages": list(reversed(recent)),
            "topics": self.get_active_topics(hours=1)
        }

    def _extract_tags(self, content):
        """Extract topic tags from message content."""
        tags = []
        content_lower = content.lower()

        # Domain-specific tags
        domain_tags = {
            "client": ["client", "prospect", "customer", "lead"],
            "meeting": ["meeting", "call", "session", "appointment"],
            "pipeline": ["pipeline", "opportunity", "deal", "proposal"],
            "content": ["linkedin", "blog", "article", "post", "content"],
            "security": ["cyber", "security", "iso 27001", "essential eight"],
            "governance": ["governance", "iso 42001", "ai ethics", "responsible ai"],
            "scan": ["scan", "discover", "search", "monitor"],
            "briefing": ["briefing", "morning", "summary", "overview"],
            "project": ["project", "milestone", "deliverable", "deadline"],
            "email": ["email", "inbox", "message"],
            "people": ["person", "contact", "who", "people"],
        }

        for tag, keywords in domain_tags.items():
            if any(kw in content_lower for kw in keywords):
                tags.append(tag)

        return tags[:5]  # Max 5 tags per message

    # ═══════════════════════════════════════════
    #  DATA MANAGEMENT
    # ═══════════════════════════════════════════

    def export_all(self):
        """Export all memory data for backup."""
        return {
            "conversations": self.get_history(limit=10000),
            "preferences": self.get_all_preferences(),
            "session_state": self.get_all_state(),
            "stats": self.get_conversation_stats(),
            "exported_at": datetime.now().isoformat()
        }

    def get_memory_size(self):
        """Get the size of memory databases."""
        total = 0
        for db_name in ["memory.db", "briefing.db", "health.db",
                         "business.db", "the_current.db", "chronicle.db"]:
            db_path = self.home / db_name
            if db_path.exists():
                total += db_path.stat().st_size
        return {
            "total_bytes": total,
            "total_mb": round(total / (1024 * 1024), 2)
        }
