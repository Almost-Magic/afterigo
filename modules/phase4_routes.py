"""
ELAINE Phase 4: Flask Routes
Business Intelligence, The Current, Chronicle

Add these routes to your existing app.py or import as a Blueprint.
"""

from flask import Blueprint, request, jsonify
import json

phase4_bp = Blueprint('phase4', __name__)

# ─── Lazy initialisation ───
_business = None
_current = None
_chronicle = None


def get_business():
    global _business
    if _business is None:
        from modules.phase4_business.business_context import BusinessContextEngine
        _business = BusinessContextEngine()
    return _business


def get_current():
    global _current
    if _current is None:
        from modules.phase4_current.the_current import TheCurrentEngine
        _current = TheCurrentEngine()
    return _current


def get_chronicle():
    global _chronicle
    if _chronicle is None:
        from modules.phase4_chronicle.chronicle import ChronicleEngine
        _chronicle = ChronicleEngine()
    return _chronicle


# ═══════════════════════════════════════════
#  BUSINESS CONTEXT ROUTES
# ═══════════════════════════════════════════

@phase4_bp.route('/api/business/dashboard')
def business_dashboard():
    return jsonify(get_business().get_dashboard_summary())


@phase4_bp.route('/api/business/clients', methods=['GET', 'POST'])
def clients():
    biz = get_business()
    if request.method == 'POST':
        data = request.json
        client_id = biz.add_client(**data)
        return jsonify({'id': client_id, 'status': 'created'})
    else:
        status = request.args.get('status')
        return jsonify(biz.get_all_clients(status))


@phase4_bp.route('/api/business/clients/<int:client_id>')
def get_client(client_id):
    client = get_business().get_client(client_id)
    return jsonify(client) if client else ('Not found', 404)


@phase4_bp.route('/api/business/clients/<int:client_id>/update', methods=['POST'])
def update_client(client_id):
    data = request.json
    get_business().update_client(client_id, **data)
    return jsonify({'status': 'updated'})


@phase4_bp.route('/api/business/clients/search')
def search_clients():
    q = request.args.get('q', '')
    return jsonify(get_business().search_clients(q))


@phase4_bp.route('/api/business/interactions', methods=['POST'])
def log_interaction():
    data = request.json
    get_business().log_interaction(**data)
    return jsonify({'status': 'logged'})


@phase4_bp.route('/api/business/interactions/<int:client_id>')
def get_interactions(client_id):
    return jsonify(get_business().get_interactions(client_id))


@phase4_bp.route('/api/business/projects')
def active_projects():
    return jsonify(get_business().get_active_projects())


@phase4_bp.route('/api/business/projects', methods=['POST'])
def add_project():
    data = request.json
    pid = get_business().add_project(**data)
    return jsonify({'id': pid, 'status': 'created'})


@phase4_bp.route('/api/business/pipeline')
def pipeline():
    return jsonify(get_business().get_pipeline())


@phase4_bp.route('/api/business/pipeline/value')
def pipeline_value():
    return jsonify(get_business().get_pipeline_value())


@phase4_bp.route('/api/business/pipeline', methods=['POST'])
def add_opportunity():
    data = request.json
    oid = get_business().add_opportunity(**data)
    return jsonify({'id': oid, 'status': 'created'})


@phase4_bp.route('/api/business/decisions', methods=['POST'])
def log_decision():
    data = request.json
    did = get_business().log_decision(**data)
    return jsonify({'id': did, 'status': 'logged'})


@phase4_bp.route('/api/business/decisions/review')
def decisions_for_review():
    return jsonify(get_business().get_decisions_for_review())


# ═══════════════════════════════════════════
#  THE CURRENT ROUTES
# ═══════════════════════════════════════════

@phase4_bp.route('/api/current/dashboard')
def current_dashboard():
    return jsonify(get_current().get_dashboard_data())


@phase4_bp.route('/api/current/scan', methods=['POST'])
def run_scan():
    area = request.json.get('interest_area') if request.json else None
    source = request.json.get('source') if request.json else None
    current = get_current()
    if source == 'rss':
        results = current.scan_rss_feeds(area)
    elif source == 'reddit':
        results = current.scan_reddit(area)
    elif source == 'academic':
        results = current.scan_academic(area)
    elif source == 'books':
        results = current.scan_books(area)
    else:
        results = current.run_full_scan()
    return jsonify(results)


@phase4_bp.route('/api/current/scan/start', methods=['POST'])
def start_background_scan():
    interval = request.json.get('interval_hours', 6) if request.json else 6
    return jsonify(get_current().start_background_scan(interval))


@phase4_bp.route('/api/current/scan/stop', methods=['POST'])
def stop_background_scan():
    return jsonify(get_current().stop_background_scan())


@phase4_bp.route('/api/current/discoveries')
def discoveries():
    args = {
        'interest_area': request.args.get('area'),
        'source': request.args.get('source'),
        'unread_only': request.args.get('unread') == 'true',
        'starred_only': request.args.get('starred') == 'true',
        'limit': int(request.args.get('limit', 50))
    }
    return jsonify(get_current().get_discoveries(**args))


@phase4_bp.route('/api/current/opportunities')
def content_opportunities():
    fmt = request.args.get('format')
    status = request.args.get('status', 'idea')
    return jsonify(get_current().get_content_opportunities(fmt, status))


@phase4_bp.route('/api/current/trends')
def trends():
    status = request.args.get('status')
    return jsonify(get_current().get_trends(status))


@phase4_bp.route('/api/current/briefing')
def morning_briefing():
    return jsonify(get_current().get_morning_briefing())


@phase4_bp.route('/api/current/competitors', methods=['GET', 'POST'])
def competitors():
    current = get_current()
    if request.method == 'POST':
        data = request.json
        cid = current.add_competitor(**data)
        return jsonify({'id': cid, 'status': 'created'})
    return jsonify(current.get_competitors())


# ═══════════════════════════════════════════
#  CHRONICLE (MEETING INTELLIGENCE) ROUTES
# ═══════════════════════════════════════════

@phase4_bp.route('/api/chronicle/meetings', methods=['GET', 'POST'])
def meetings():
    chron = get_chronicle()
    if request.method == 'POST':
        data = request.json
        mid = chron.create_meeting(**data)
        return jsonify({'id': mid, 'status': 'created'})
    days = int(request.args.get('days', 7))
    return jsonify(chron.get_upcoming_meetings(days))


@phase4_bp.route('/api/chronicle/meetings/<int:meeting_id>')
def get_meeting(meeting_id):
    meeting = get_chronicle().get_meeting(meeting_id)
    return jsonify(meeting) if meeting else ('Not found', 404)


@phase4_bp.route('/api/chronicle/meetings/<int:meeting_id>/prep')
def meeting_prep(meeting_id):
    prep = get_chronicle().generate_prep(meeting_id, get_business())
    return jsonify(prep) if prep else ('Not found', 404)


@phase4_bp.route('/api/chronicle/meetings/<int:meeting_id>/post', methods=['POST'])
def post_meeting(meeting_id):
    data = request.json
    get_chronicle().capture_post_meeting(meeting_id, **data)
    return jsonify({'status': 'captured'})


@phase4_bp.route('/api/chronicle/meetings/<int:meeting_id>/attendees', methods=['POST'])
def add_attendee(meeting_id):
    data = request.json
    data['meeting_id'] = meeting_id
    aid = get_chronicle().add_attendee_intel(**data)
    return jsonify({'id': aid, 'status': 'added'})


@phase4_bp.route('/api/chronicle/templates')
def meeting_templates():
    return jsonify(get_chronicle().get_templates())


@phase4_bp.route('/api/chronicle/actions')
def pending_actions():
    return jsonify(get_chronicle().get_pending_action_items())
