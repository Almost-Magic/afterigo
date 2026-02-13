"""
ELAINE Phase 5: Morning Briefing v2 — Chief of Staff Briefing
Aggregates emails, LinkedIn, news, deadlines, meetings, prep questions,
and People of Interest tracking into a unified morning briefing.

"Good morning, Mani. Here's what needs your attention."
"""

import json
import sqlite3
import imaplib
import email
import re
import os
from datetime import datetime, timedelta
from pathlib import Path
from email.header import decode_header

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False


class MorningBriefingEngine:
    """
    Generates the Chief of Staff morning briefing.
    Pulls from: Email, LinkedIn, News, Calendar, Pipeline, Action Items.
    Tracks People of Interest and learns who matters over time.
    """

    def __init__(self, config_path=None):
        self.home = Path.home() / ".elaine"
        self.home.mkdir(exist_ok=True)
        self.config_path = config_path or str(self.home / "briefing_config.json")
        self.db_path = str(self.home / "briefing.db")
        self.config = self._load_config()
        self._init_db()

    def _load_config(self):
        defaults = {
            "email": {
                "enabled": False,
                "imap_server": "",
                "imap_port": 993,
                "username": "",
                "password": "",
                "folders": ["INBOX"],
                "hours_lookback": 12,
                "priority_senders": [],
                "priority_keywords": [
                    "urgent", "deadline", "action required", "overdue",
                    "invoice", "proposal", "contract", "meeting",
                    "ISO 42001", "ISO 27001", "audit", "compliance"
                ],
                "max_emails": 15
            },
            "linkedin": {
                "enabled": True,
                "rss_feeds": [
                    "https://news.google.com/rss/search?q=AI+governance+consulting",
                    "https://news.google.com/rss/search?q=cybersecurity+SMB+Australia",
                    "https://news.google.com/rss/search?q=AI+agents+enterprise",
                    "https://news.google.com/rss/search?q=ISO+42001+certification",
                ],
                "keywords": [
                    "AI governance", "cybersecurity", "ISO 42001", "ISO 27001",
                    "SMB digital transformation", "AI agents", "agentic AI",
                    "consulting", "fractional CTO"
                ],
                "max_items": 8
            },
            "news": {
                "enabled": True,
                "feeds": [
                    "https://news.google.com/rss/search?q=artificial+intelligence+Australia",
                    "https://news.google.com/rss/search?q=cybersecurity+Australia+2026",
                    "https://news.google.com/rss/search?q=AI+regulation+policy",
                    "https://news.google.com/rss/search?q=SMB+technology+Australia",
                    "https://news.google.com/rss/search?q=ISO+42001+AI+management",
                ],
                "max_items": 10,
                "hours_lookback": 24
            },
            "calendar": {
                "enabled": True,
                "ics_path": "",
                "outlook_ics_paths": [
                    str(Path.home() / "Documents" / "calendar.ics"),
                    str(Path.home() / "Downloads" / "calendar.ics"),
                    str(Path.home() / "Desktop" / "calendar.ics"),
                ],
                "days_ahead": 1
            },
            "briefing_time": "07:00",
            "timezone": "Australia/Sydney",
            "prep_questions_per_meeting": 4,
        }
        if Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    saved = json.load(f)
                for key in defaults:
                    if key in saved:
                        if isinstance(defaults[key], dict):
                            defaults[key].update(saved[key])
                        else:
                            defaults[key] = saved[key]
            except Exception:
                pass
        return defaults

    def save_config(self, config=None):
        if config:
            self.config = config
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS briefings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            briefing_data TEXT,
            sections_count INTEGER,
            total_items INTEGER
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS email_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT UNIQUE,
            sender TEXT,
            subject TEXT,
            snippet TEXT,
            received_at TIMESTAMP,
            priority_score REAL DEFAULT 0,
            is_read INTEGER DEFAULT 0,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        # People of Interest — Elaine learns who matters
        c.execute("""CREATE TABLE IF NOT EXISTS people_of_interest (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT,
            company TEXT,
            linkedin_url TEXT,
            twitter_handle TEXT,
            website TEXT,
            email TEXT,
            why_important TEXT,
            category TEXT DEFAULT 'general',
            interest_level INTEGER DEFAULT 5,
            auto_discovered INTEGER DEFAULT 0,
            search_queries TEXT,
            last_activity TEXT,
            last_checked TIMESTAMP,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS poi_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER,
            activity_type TEXT,
            title TEXT,
            url TEXT,
            summary TEXT,
            source TEXT,
            relevance_score REAL DEFAULT 0,
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            included_in_briefing INTEGER DEFAULT 0,
            FOREIGN KEY (person_id) REFERENCES people_of_interest(id)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS poi_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER,
            interaction_type TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (person_id) REFERENCES people_of_interest(id)
        )""")
        conn.commit()
        conn.close()

    # ═══════════════════════════════════════════
    #  PEOPLE OF INTEREST
    # ═══════════════════════════════════════════

    def add_person_of_interest(self, name, role=None, company=None,
                                linkedin_url=None, twitter_handle=None,
                                website=None, email_addr=None,
                                why_important=None, category='general',
                                interest_level=5):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        search_queries = self._build_poi_search_queries(name, company, role)
        c.execute("""INSERT INTO people_of_interest
            (name, role, company, linkedin_url, twitter_handle, website,
             email, why_important, category, interest_level, search_queries)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, role, company, linkedin_url, twitter_handle, website,
             email_addr, why_important, category, interest_level,
             json.dumps(search_queries)))
        pid = c.lastrowid
        conn.commit()
        conn.close()
        return pid

    def get_people_of_interest(self, category=None, min_level=0):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        if category:
            c.execute("""SELECT * FROM people_of_interest
                WHERE category = ? AND interest_level >= ?
                ORDER BY interest_level DESC""", (category, min_level))
        else:
            c.execute("""SELECT * FROM people_of_interest
                WHERE interest_level >= ?
                ORDER BY interest_level DESC""", (min_level,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def update_person(self, person_id, **kwargs):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        allowed = ['name', 'role', 'company', 'linkedin_url', 'twitter_handle',
                    'website', 'email', 'why_important', 'category',
                    'interest_level', 'search_queries']
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if updates:
            updates['updated_at'] = datetime.now().isoformat()
            set_clause = ", ".join(f"{k} = ?" for k in updates)
            c.execute(f"UPDATE people_of_interest SET {set_clause} WHERE id = ?",
                      list(updates.values()) + [person_id])
            conn.commit()
        conn.close()

    def remove_person(self, person_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM poi_activity WHERE person_id = ?", (person_id,))
        c.execute("DELETE FROM poi_interactions WHERE person_id = ?", (person_id,))
        c.execute("DELETE FROM people_of_interest WHERE id = ?", (person_id,))
        conn.commit()
        conn.close()

    def log_poi_interaction(self, person_id, interaction_type, notes=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT INTO poi_interactions
            (person_id, interaction_type, notes) VALUES (?, ?, ?)""",
            (person_id, interaction_type, notes))
        # Auto-boost interest when Mani keeps interacting
        c.execute("""SELECT COUNT(*) FROM poi_interactions
            WHERE person_id = ? AND created_at >= ?""",
            (person_id, (datetime.now() - timedelta(days=30)).isoformat()))
        recent = c.fetchone()[0]
        if recent >= 5:
            c.execute("""UPDATE people_of_interest
                SET interest_level = MIN(interest_level + 1, 10)
                WHERE id = ? AND interest_level < 10""", (person_id,))
        conn.commit()
        conn.close()

    def discover_people_from_clients(self):
        try:
            from modules.phase4_business.business_context import BusinessContextEngine
            biz = BusinessContextEngine()
            clients = biz.get_all_clients()
        except Exception:
            return []
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        discovered = []
        for client in clients:
            name = client.get("name", "")
            if not name or len(name) < 3:
                continue
            c.execute("SELECT id FROM people_of_interest WHERE name = ?", (name,))
            if c.fetchone():
                continue
            queries = self._build_poi_search_queries(name, client.get("company"), None)
            level = 6 if client.get("status") == "active" else 4
            c.execute("""INSERT OR IGNORE INTO people_of_interest
                (name, email, company, linkedin_url, category, interest_level,
                 auto_discovered, why_important, search_queries)
                VALUES (?, ?, ?, ?, 'client', ?, 1, ?, ?)""",
                (name, client.get("email"), client.get("company"),
                 client.get("linkedin_url"), level,
                 f"Client ({client.get('status', 'prospect')})",
                 json.dumps(queries)))
            if c.rowcount > 0:
                discovered.append({"name": name, "company": client.get("company")})
        conn.commit()
        conn.close()
        return discovered

    def discover_people_from_meetings(self):
        try:
            from modules.phase4_chronicle.chronicle import ChronicleEngine
            chron = ChronicleEngine()
        except Exception:
            return []
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        discovered = []
        try:
            chron_conn = sqlite3.connect(chron.db_path)
            chron_conn.row_factory = sqlite3.Row
            cc = chron_conn.cursor()
            cc.execute("SELECT * FROM meetings WHERE created_at >= ?",
                ((datetime.now() - timedelta(days=90)).isoformat(),))
            meetings = [dict(r) for r in cc.fetchall()]
            chron_conn.close()
        except Exception:
            return []
        for m in meetings:
            attendees = json.loads(m.get("attendees", "[]")) if m.get("attendees") else []
            for att in attendees:
                att_name = att if isinstance(att, str) else att.get("name", "")
                att_email = att.get("email", "") if isinstance(att, dict) else ""
                if not att_name or len(att_name) < 3:
                    continue
                c.execute("SELECT id FROM people_of_interest WHERE name = ?", (att_name,))
                if c.fetchone():
                    continue
                queries = self._build_poi_search_queries(att_name, None, None)
                c.execute("""INSERT OR IGNORE INTO people_of_interest
                    (name, email, category, interest_level,
                     auto_discovered, why_important, search_queries)
                    VALUES (?, ?, 'meeting_contact', 3, 1, 'Met in meetings', ?)""",
                    (att_name, att_email, json.dumps(queries)))
                if c.rowcount > 0:
                    discovered.append({"name": att_name})
        conn.commit()
        conn.close()
        return discovered

    def discover_people_from_emails(self, emails_data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        discovered = []
        for em in emails_data:
            sender = em.get("sender_email", "")
            name = em.get("sender", "")
            if not sender or "@" not in sender:
                continue
            skip = ["noreply", "no-reply", "newsletter", "notifications",
                    "support@", "info@", "admin@", "mailer-daemon",
                    "donotreply", "updates@", "team@", "hello@"]
            if any(p in sender.lower() for p in skip):
                continue
            c.execute("SELECT id FROM people_of_interest WHERE email = ?", (sender,))
            if c.fetchone():
                continue
            c.execute("""SELECT COUNT(*) FROM email_cache
                WHERE sender LIKE ? AND cached_at >= ?""",
                (f"%{sender}%", (datetime.now() - timedelta(days=30)).isoformat()))
            count = c.fetchone()[0]
            if count >= 3:
                domain = sender.split("@")[1] if "@" in sender else ""
                company = domain.split(".")[0].title() if domain else None
                queries = self._build_poi_search_queries(name, company, None)
                c.execute("""INSERT OR IGNORE INTO people_of_interest
                    (name, email, company, category, interest_level,
                     auto_discovered, why_important, search_queries)
                    VALUES (?, ?, ?, 'email_contact', 3, 1, 'Frequently emails you', ?)""",
                    (name, sender, company, json.dumps(queries)))
                if c.rowcount > 0:
                    discovered.append({"name": name, "email": sender})
        conn.commit()
        conn.close()
        return discovered

    def _build_poi_search_queries(self, name, company=None, role=None):
        queries = []
        if name:
            queries.append(f'"{name}"')
            if company:
                queries.append(f'"{name}" "{company}"')
                queries.append(f'"{name}" LinkedIn')
            if role:
                queries.append(f'"{name}" {role}')
        return queries

    def scan_poi_activity(self, max_people=10):
        if not HAS_REQUESTS or not HAS_FEEDPARSER:
            return {"error": "feedparser/requests not installed"}
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT * FROM people_of_interest WHERE interest_level >= 3
            ORDER BY CASE WHEN last_checked IS NULL THEN 0 ELSE 1 END,
            interest_level DESC, last_checked ASC LIMIT ?""", (max_people,))
        people = [dict(r) for r in c.fetchall()]
        results = []
        for person in people:
            pid = person["id"]
            name = person["name"]
            search_queries = json.loads(person.get("search_queries", "[]"))
            if not search_queries:
                search_queries = [f'"{name}"']
            person_results = []
            for query in search_queries[:2]:
                try:
                    encoded = query.replace('"', '%22').replace(' ', '+')
                    feed_url = f"https://news.google.com/rss/search?q={encoded}"
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:3]:
                        title = entry.get("title", "")
                        link = entry.get("link", "")
                        summary = entry.get("summary", "")
                        c.execute("SELECT id FROM poi_activity WHERE url = ?", (link,))
                        if c.fetchone():
                            continue
                        name_parts = name.lower().split()
                        text_lower = f"{title} {summary}".lower()
                        relevance = sum(1 for p in name_parts if p in text_lower)
                        score = min(relevance / max(len(name_parts), 1), 1.0)
                        if score >= 0.5:
                            c.execute("""INSERT INTO poi_activity
                                (person_id, activity_type, title, url, summary, source, relevance_score)
                                VALUES (?, 'news_mention', ?, ?, ?, 'google_news', ?)""",
                                (pid, title, link, summary[:300], score))
                            person_results.append({"title": title, "url": link, "relevance": score})
                except Exception:
                    continue
            c.execute("UPDATE people_of_interest SET last_checked = ?, last_activity = ? WHERE id = ?",
                (datetime.now().isoformat(),
                 json.dumps(person_results[:3]) if person_results else None, pid))
            if person_results:
                results.append({"person": name, "company": person.get("company"),
                    "interest_level": person["interest_level"], "new_activity": person_results})
        conn.commit()
        conn.close()
        return {"scanned": len(people), "with_activity": len(results), "results": results}

    def get_poi_recent_activity(self, hours=24, min_interest=3):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        c.execute("""SELECT a.*, p.name as person_name, p.company as person_company,
                p.interest_level, p.category, p.why_important
            FROM poi_activity a JOIN people_of_interest p ON a.person_id = p.id
            WHERE a.discovered_at >= ? AND p.interest_level >= ?
            ORDER BY p.interest_level DESC, a.relevance_score DESC LIMIT 15""",
            (since, min_interest))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def get_poi_stats(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM people_of_interest")
        total = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM people_of_interest WHERE auto_discovered = 1")
        auto = c.fetchone()[0]
        c.execute("SELECT category, COUNT(*) FROM people_of_interest GROUP BY category")
        by_cat = dict(c.fetchall())
        c.execute("SELECT COUNT(*) FROM poi_activity WHERE discovered_at >= ?",
            ((datetime.now() - timedelta(days=1)).isoformat(),))
        recent = c.fetchone()[0]
        conn.close()
        return {"total": total, "auto_discovered": auto, "manual": total - auto,
                "by_category": by_cat, "recent_activity_24h": recent}

    # ═══════════════════════════════════════════
    #  MAIN BRIEFING GENERATOR
    # ═══════════════════════════════════════════

    def generate_briefing(self):
        now = datetime.now()
        hour = now.hour
        greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"

        briefing = {
            "greeting": f"{greeting}, Mani.",
            "generated_at": now.isoformat(),
            "date": now.strftime("%A, %d %B %Y"),
            "time": now.strftime("%I:%M %p"),
            "sections": {},
            "summary": "",
            "health": {}
        }

        meetings = self._get_meetings()
        briefing["sections"]["meetings"] = meetings
        briefing["health"]["calendar"] = "ok" if meetings.get("items") else "no_meetings"

        emails = self._get_important_emails()
        briefing["sections"]["emails"] = emails
        briefing["health"]["email"] = emails.get("source", "disabled")

        prep = self._generate_prep_questions(meetings.get("items", []))
        briefing["sections"]["prep_questions"] = prep

        poi = self._get_poi_briefing()
        briefing["sections"]["people"] = poi
        briefing["health"]["people"] = "ok" if poi.get("items") else "no_activity"

        linkedin = self._get_linkedin_relevant()
        briefing["sections"]["linkedin"] = linkedin
        briefing["health"]["linkedin"] = "ok" if linkedin.get("items") else "no_data"

        news = self._get_relevant_news()
        briefing["sections"]["news"] = news
        briefing["health"]["news"] = "ok" if news.get("items") else "no_data"

        deadlines = self._get_deadlines()
        briefing["sections"]["deadlines"] = deadlines

        actions = self._get_pending_actions()
        briefing["sections"]["action_items"] = actions

        total = sum(len(s.get("items", [])) for s in briefing["sections"].values())
        briefing["total_items"] = total
        briefing["summary"] = self._build_summary(briefing)

        self._run_auto_discovery(emails.get("items", []))
        self._store_briefing(briefing)
        return briefing

    # ═══════════════════════════════════════════
    #  SECTION GENERATORS
    # ═══════════════════════════════════════════

    def _get_meetings(self):
        result = {"title": "Today's Meetings", "items": [], "source": "none"}
        ics = self._parse_ics_calendar()
        if ics:
            result["items"].extend(ics)
            result["source"] = "ics"
        try:
            from modules.phase4_chronicle.chronicle import ChronicleEngine
            chron = ChronicleEngine()
            upcoming = chron.get_upcoming_meetings(days=1)
            for m in upcoming:
                result["items"].append({
                    "title": m.get("title", "Untitled"),
                    "time": m.get("scheduled_at", "TBD"),
                    "type": m.get("meeting_type", "general"),
                    "attendees": json.loads(m["attendees"]) if m.get("attendees") else [],
                    "location": m.get("location", ""),
                    "source": "chronicle", "meeting_id": m.get("id")
                })
            if upcoming:
                result["source"] = "chronicle" if not ics else "ics+chronicle"
        except Exception as e:
            result["chronicle_error"] = str(e)
        result["items"].sort(key=lambda x: x.get("time", "99:99"))
        return result

    def _parse_ics_calendar(self):
        meetings = []
        today = datetime.now().date()
        paths = []
        if self.config["calendar"].get("ics_path"):
            paths.append(self.config["calendar"]["ics_path"])
        paths.extend(self.config["calendar"].get("outlook_ics_paths", []))
        for ics_path in paths:
            if not Path(ics_path).exists():
                continue
            try:
                with open(ics_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                events = content.split("BEGIN:VEVENT")
                for block in events[1:]:
                    ev = {}
                    for line in block.split("\n"):
                        line = line.strip()
                        if line.startswith("SUMMARY:"): ev["title"] = line[8:]
                        elif line.startswith("DTSTART"):
                            ev["start"] = self._parse_ics_dt(line.split(":", 1)[-1].strip())
                        elif line.startswith("DTEND"):
                            ev["end"] = self._parse_ics_dt(line.split(":", 1)[-1].strip())
                        elif line.startswith("LOCATION:"): ev["location"] = line[9:]
                        elif line.startswith("ATTENDEE"):
                            m = line.split("mailto:", 1)
                            if len(m) > 1:
                                ev.setdefault("attendees", []).append(m[1].strip())
                    if ev.get("start") and isinstance(ev["start"], datetime) and ev["start"].date() == today:
                        meetings.append({
                            "title": ev.get("title", "Untitled"),
                            "time": ev["start"].strftime("%I:%M %p"),
                            "end_time": ev["end"].strftime("%I:%M %p") if isinstance(ev.get("end"), datetime) else "",
                            "location": ev.get("location", ""),
                            "attendees": ev.get("attendees", []),
                            "source": "ics"
                        })
            except Exception:
                continue
        return meetings

    def _parse_ics_dt(self, s):
        s = s.replace("Z", "").strip()
        for fmt in ["%Y%m%dT%H%M%S", "%Y%m%d", "%Y%m%dT%H%M"]:
            try: return datetime.strptime(s, fmt)
            except ValueError: continue
        return None

    def _get_important_emails(self):
        result = {"title": "Important Emails", "items": [], "source": "disabled"}
        if not self.config["email"]["enabled"]:
            result["message"] = "Email not configured. Go to Settings to connect."
            return result
        try:
            srv = self.config["email"]["imap_server"]
            usr = self.config["email"]["username"]
            pwd = self.config["email"]["password"]
            if not all([srv, usr, pwd]):
                result["source"] = "not_configured"
                result["message"] = "Email credentials incomplete."
                return result
            mail = imaplib.IMAP4_SSL(srv, self.config["email"]["imap_port"])
            mail.login(usr, pwd)
            hours = self.config["email"]["hours_lookback"]
            since = (datetime.now() - timedelta(hours=hours)).strftime("%d-%b-%Y")
            pri_senders = [s.lower() for s in self.config["email"].get("priority_senders", [])]
            pri_kw = [k.lower() for k in self.config["email"].get("priority_keywords", [])]
            poi_emails = self._get_poi_emails()
            pri_senders.extend(poi_emails)
            for folder in self.config["email"]["folders"]:
                try:
                    mail.select(folder)
                    _, msgs = mail.search(None, f'(SINCE "{since}")')
                    for mid in msgs[0].split()[-50:]:
                        _, data = mail.fetch(mid, "(RFC822)")
                        msg = email.message_from_bytes(data[0][1])
                        sender_raw = msg.get("From", "")
                        sender = self._decode_hdr(sender_raw)
                        sender_email = self._extract_email(sender_raw)
                        subject = self._decode_hdr(msg.get("Subject", "(no subject)"))
                        snippet = self._get_snippet(msg)
                        recv = self._parse_email_date(msg.get("Date", ""))
                        score = self._score_priority(sender_email, subject, snippet, pri_senders, pri_kw)
                        self._cache_email(sender, sender_email, subject, snippet, recv)
                        result["items"].append({
                            "sender": sender, "sender_email": sender_email,
                            "subject": subject, "snippet": snippet[:200],
                            "received_at": recv, "priority_score": score,
                            "is_poi": sender_email.lower() in [e.lower() for e in poi_emails]
                        })
                except Exception:
                    continue
            mail.logout()
            result["source"] = "imap"
            result["items"].sort(key=lambda x: x.get("priority_score", 0), reverse=True)
            result["items"] = result["items"][:self.config["email"]["max_emails"]]
        except Exception as e:
            result["source"] = "error"
            result["message"] = str(e)
        return result

    def _get_poi_emails(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT email FROM people_of_interest WHERE email IS NOT NULL AND email != ''")
        emails = [r[0] for r in c.fetchall()]
        conn.close()
        return emails

    def _cache_email(self, sender, sender_email, subject, snippet, recv):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute("INSERT OR IGNORE INTO email_cache (message_id, sender, subject, snippet, received_at) VALUES (?, ?, ?, ?, ?)",
                (f"{sender_email}:{subject}:{recv}", f"{sender} <{sender_email}>", subject, snippet[:200], recv))
            conn.commit()
        except Exception: pass
        conn.close()

    def _decode_hdr(self, h):
        if not h: return ""
        parts = decode_header(h)
        out = []
        for c, ch in parts:
            out.append(c.decode(ch or 'utf-8', errors='replace') if isinstance(c, bytes) else c)
        return " ".join(out)

    def _extract_email(self, h):
        m = re.search(r'<([^>]+)>', h)
        return m.group(1).lower() if m else h.strip().lower()

    def _get_snippet(self, msg):
        if msg.is_multipart():
            for p in msg.walk():
                if p.get_content_type() == 'text/plain':
                    try: return p.get_payload(decode=True).decode('utf-8', errors='replace')[:300]
                    except: continue
        else:
            try:
                b = msg.get_payload(decode=True)
                return b.decode('utf-8', errors='replace')[:300] if b else ""
            except: pass
        return ""

    def _parse_email_date(self, s):
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(s).isoformat()
        except: return s

    def _score_priority(self, sender, subject, snippet, pri_senders, pri_kw):
        score = 0
        text = f"{subject} {snippet}".lower()
        if any(ps in sender.lower() for ps in pri_senders if ps): score += 40
        for k in pri_kw:
            if k in text: score += 15
        for u in ["urgent", "asap", "immediately", "deadline today", "action required"]:
            if u in text: score += 20
        if subject.lower().startswith("re:"): score += 10
        return min(score, 100)

    def _generate_prep_questions(self, meetings):
        result = {"title": "Preparation Questions", "items": []}
        if not meetings:
            result["message"] = "No meetings today — deep work time available."
            return result
        try:
            from modules.phase4_business.business_context import BusinessContextEngine
            biz = BusinessContextEngine()
            clients = biz.get_all_clients()
            pipeline = biz.get_pipeline()
        except Exception:
            clients, pipeline = [], []
        max_q = self.config.get("prep_questions_per_meeting", 4)
        for meeting in meetings:
            title = meeting.get("title", "Meeting")
            tl = title.lower()
            attendees = meeting.get("attendees", [])
            # Match to clients
            matched = []
            for a in attendees:
                al = a.lower() if isinstance(a, str) else ""
                for cl in clients:
                    if (cl.get("email") and al == cl["email"].lower()) or \
                       (cl.get("name") and cl["name"].lower() in al):
                        matched.append(cl)
            # Match to POI
            poi_match = self._match_poi(attendees)
            # Build questions
            if "discovery" in tl or "intro" in tl:
                qs = ["What is their primary business challenge?",
                      "What AI governance or cybersecurity pain points might they have?",
                      "What's the ideal first engagement?",
                      "What do you want them to feel after this meeting?"]
            elif "governance" in tl or "42001" in tl or "iso" in tl:
                qs = ["Where are they in AI governance maturity?",
                      "Regulatory pressures driving this?",
                      "Which ISO 42001 clauses matter most here?",
                      "What quick wins can you show?"]
            elif "cyber" in tl or "security" in tl or "27001" in tl:
                qs = ["Current Essential Eight maturity?",
                      "Recent security incidents?",
                      "Compliance requirements they're targeting?",
                      "Biggest security gap you can address?"]
            elif "board" in tl or "advisory" in tl:
                qs = ["Strategic decisions pending?",
                      "Data or trends to bring?",
                      "Risks to raise proactively?",
                      "One thing they should walk away knowing?"]
            else:
                qs = [f"Primary objective for '{title}'?",
                      "What decision or outcome do you want?",
                      "What context should you review?",
                      "How will you set the tone?"]
            # Context enrichment
            for cl in matched[:2]:
                if cl.get("status") == "prospect":
                    qs.append(f"Review {cl['name']}'s profile — conversion blocker?")
            for p in poi_match[:2]:
                qs.append(f"Check recent activity from {p['name']} — anything to reference?")
            closing = [p for p in pipeline if p.get("expected_close") and
                       p["expected_close"] <= (datetime.now() + timedelta(days=7)).isoformat()]
            if closing:
                qs.append(f"Pipeline: {len(closing)} opportunity(ies) closing this week.")
            result["items"].append({
                "meeting": title, "time": meeting.get("time", ""),
                "matched_clients": [c.get("name") for c in matched],
                "poi_present": [p.get("name") for p in poi_match],
                "questions": qs[:max_q + 2]
            })
        return result

    def _match_poi(self, attendees):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        matched = []
        for a in attendees:
            a_str = a if isinstance(a, str) else str(a)
            c.execute("SELECT * FROM people_of_interest WHERE email = ? OR name LIKE ?",
                (a_str.lower(), f"%{a_str}%"))
            matched.extend(dict(r) for r in c.fetchall())
        conn.close()
        return matched

    def _get_poi_briefing(self):
        result = {"title": "People of Interest", "items": []}
        activity = self.get_poi_recent_activity(hours=24, min_interest=3)
        if not activity:
            result["message"] = "No new activity from your people. Run a POI scan to check."
            return result
        by_person = {}
        for a in activity:
            name = a["person_name"]
            if name not in by_person:
                by_person[name] = {"name": name, "company": a.get("person_company"),
                    "interest_level": a.get("interest_level"),
                    "category": a.get("category"), "activities": []}
            by_person[name]["activities"].append({
                "type": a.get("activity_type"), "title": a.get("title"),
                "url": a.get("url"), "source": a.get("source")})
        result["items"] = list(by_person.values())
        return result

    def _get_linkedin_relevant(self):
        result = {"title": "LinkedIn & Industry", "items": []}
        if not self.config["linkedin"]["enabled"] or not HAS_FEEDPARSER:
            return result
        kws = [k.lower() for k in self.config["linkedin"]["keywords"]]
        poi_names = []
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT name, company FROM people_of_interest WHERE interest_level >= 5")
        for r in c.fetchall():
            poi_names.append(r[0].lower())
            if r[1]: poi_names.append(r[1].lower())
        conn.close()
        seen = set()
        for url in self.config["linkedin"]["rss_feeds"]:
            try:
                feed = feedparser.parse(url)
                for e in feed.entries[:5]:
                    link = e.get("link", "")
                    if link in seen: continue
                    seen.add(link)
                    text = f"{e.get('title', '')} {e.get('summary', '')}".lower()
                    kw_score = sum(1 for k in kws if k in text)
                    poi_score = sum(2 for p in poi_names if p in text)
                    if kw_score + poi_score >= 1:
                        result["items"].append({
                            "title": e.get("title", ""), "url": link,
                            "source": e.get("source", {}).get("title", ""),
                            "summary": e.get("summary", "")[:200],
                            "relevance_score": kw_score + poi_score,
                            "matched_keywords": [k for k in kws if k in text],
                            "matched_people": [p for p in poi_names if p in text],
                            "published": e.get("published", "")
                        })
            except Exception: continue
        result["items"].sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        result["items"] = result["items"][:self.config["linkedin"]["max_items"]]
        return result

    def _get_relevant_news(self):
        result = {"title": "News & Intelligence", "items": []}
        if not self.config["news"]["enabled"] or not HAS_FEEDPARSER:
            return result
        seen = set()
        # Pull from The Current first
        try:
            from modules.phase4_current.the_current import TheCurrentEngine
            current = TheCurrentEngine()
            br = current.get_morning_briefing()
            for d in br.get("top_discoveries", [])[:5]:
                url = d.get("url", "")
                if url and url not in seen:
                    seen.add(url)
                    result["items"].append({
                        "title": d.get("title", ""), "url": url,
                        "source": d.get("source", "The Current"),
                        "area": d.get("interest_area", ""),
                        "summary": d.get("snippet", "")[:200],
                        "published": d.get("discovered_at", ""),
                        "from_current": True
                    })
        except Exception: pass
        for url in self.config["news"]["feeds"]:
            try:
                feed = feedparser.parse(url)
                for e in feed.entries[:4]:
                    link = e.get("link", "")
                    if link in seen: continue
                    seen.add(link)
                    result["items"].append({
                        "title": e.get("title", ""), "url": link,
                        "source": e.get("source", {}).get("title", "Google News"),
                        "summary": e.get("summary", "")[:200],
                        "published": e.get("published", ""),
                        "from_current": False
                    })
            except Exception: continue
        result["items"] = result["items"][:self.config["news"]["max_items"]]
        return result

    def _get_deadlines(self):
        result = {"title": "Deadlines & Due Dates", "items": []}
        today = datetime.now().date()
        week = today + timedelta(days=7)
        try:
            from modules.phase4_business.business_context import BusinessContextEngine
            biz = BusinessContextEngine()
            for p in biz.get_pipeline():
                close = p.get("expected_close")
                if close:
                    try:
                        cd = datetime.fromisoformat(close).date()
                        if cd <= week:
                            urg = "overdue" if cd < today else "today" if cd == today else "this_week"
                            result["items"].append({"title": f"Pipeline: {p.get('opportunity', '')}",
                                "due": close, "urgency": urg, "type": "pipeline",
                                "value": p.get("estimated_value"), "client": p.get("client_name")})
                    except Exception: pass
            for proj in biz.get_active_projects():
                dl = proj.get("deadline")
                if dl:
                    try:
                        dd = datetime.fromisoformat(dl).date()
                        if dd <= week:
                            urg = "overdue" if dd < today else "today" if dd == today else "this_week"
                            result["items"].append({"title": f"Project: {proj.get('name', '')}",
                                "due": dl, "urgency": urg, "type": "project"})
                    except Exception: pass
            conn = sqlite3.connect(biz.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT name, company, next_followup FROM clients WHERE next_followup IS NOT NULL AND next_followup <= ?",
                (week.isoformat(),))
            for r in c.fetchall():
                try:
                    fd = datetime.fromisoformat(r["next_followup"]).date()
                    urg = "overdue" if fd < today else "today" if fd == today else "this_week"
                    result["items"].append({"title": f"Follow up: {r['name']}" +
                        (f" ({r['company']})" if r['company'] else ""),
                        "due": r["next_followup"], "urgency": urg, "type": "followup"})
                except Exception: pass
            conn.close()
            for d in biz.get_decisions_for_review():
                result["items"].append({"title": f"Decision review: {d.get('title', '')}",
                    "due": d.get("review_date"), "urgency": "overdue", "type": "decision"})
        except Exception: pass
        urg_order = {"overdue": 0, "today": 1, "this_week": 2}
        result["items"].sort(key=lambda x: urg_order.get(x.get("urgency"), 3))
        return result

    def _get_pending_actions(self):
        result = {"title": "Pending Action Items", "items": []}
        try:
            from modules.phase4_chronicle.chronicle import ChronicleEngine
            for a in ChronicleEngine().get_pending_action_items():
                result["items"].append({"action": a.get("action", ""),
                    "meeting": a.get("meeting_title", ""),
                    "assigned_to": a.get("assigned_to", ""),
                    "follow_up_date": a.get("follow_up_date", "")})
        except Exception as e:
            result["error"] = str(e)
        return result

    def _run_auto_discovery(self, email_items):
        try: self.discover_people_from_clients()
        except Exception: pass
        try: self.discover_people_from_meetings()
        except Exception: pass
        if email_items:
            try: self.discover_people_from_emails(email_items)
            except Exception: pass

    def _build_summary(self, briefing):
        parts = []
        s = briefing.get("sections", {})
        mtgs = s.get("meetings", {}).get("items", [])
        if mtgs: parts.append(f"{len(mtgs)} meeting{'s' if len(mtgs) != 1 else ''}")
        emails = s.get("emails", {}).get("items", [])
        hi = len([e for e in emails if e.get("priority_score", 0) >= 40])
        if hi: parts.append(f"{hi} important email{'s' if hi != 1 else ''}")
        dls = s.get("deadlines", {}).get("items", [])
        od = [d for d in dls if d.get("urgency") == "overdue"]
        td = [d for d in dls if d.get("urgency") == "today"]
        if od: parts.append(f"\u26a0\ufe0f {len(od)} overdue")
        if td: parts.append(f"{len(td)} due today")
        poi = s.get("people", {}).get("items", [])
        if poi: parts.append(f"activity from {len(poi)} people you follow")
        news = s.get("news", {}).get("items", [])
        if news: parts.append(f"{len(news)} news items")
        acts = s.get("action_items", {}).get("items", [])
        if acts: parts.append(f"{len(acts)} pending actions")
        return " \u00b7 ".join(parts) if parts else "Clear schedule. Good time for deep work."

    def _store_briefing(self, briefing):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO briefings (briefing_data, sections_count, total_items) VALUES (?, ?, ?)",
            (json.dumps(briefing, default=str), len(briefing.get("sections", {})), briefing.get("total_items", 0)))
        conn.commit()
        conn.close()

    def get_briefing_history(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT id, generated_at, sections_count, total_items FROM briefings ORDER BY generated_at DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows
