"""
Peterman V4.1 — Chamber 2: Semantic Core
Fingerprinting, drift detection, narrative analysis.
"""
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from ..models import db, Brand, Scan, SemanticFingerprint
from ..services import ollama

semantic_bp = Blueprint("semantic", __name__)


@semantic_bp.route("/api/scan/semantic/<int:brand_id>", methods=["POST"])
def run_semantic_scan(brand_id):
    """Generate a semantic fingerprint for a brand."""
    brand = Brand.query.get_or_404(brand_id)

    scan = Scan(brand_id=brand_id, scan_type="semantic", status="running",
                chambers_run=["semantic"], started_at=datetime.now(timezone.utc))
    db.session.add(scan)
    db.session.commit()

    try:
        # Build a comprehensive brand description for embedding
        brand_text = f"{brand.name}. {brand.description or ''} Industry: {brand.industry or 'N/A'}. " \
                     f"Tagline: {brand.tagline or 'N/A'}. " \
                     f"Value propositions: {', '.join(brand.value_propositions or [])}."

        # Generate embedding
        embed_result = ollama.embed(brand_text)
        embedding = embed_result.get("embedding") or None

        # Ask LLM for key themes and narrative
        analysis = ollama.generate_json(
            f'Analyse the brand "{brand.name}" ({brand.industry or "unknown industry"}). '
            f'Description: {brand.description or "N/A"}. '
            f'Return JSON: {{"key_themes": ["theme1","theme2","theme3","theme4","theme5"], '
            f'"narrative_summary": "2-3 sentence brand narrative", '
            f'"brand_positioning": "one-line positioning statement"}}'
        )
        parsed = analysis.get("parsed") or {}

        # Check for drift against previous fingerprint
        prev = SemanticFingerprint.query.filter_by(brand_id=brand_id).order_by(
            SemanticFingerprint.created_at.desc()
        ).first()

        drift_score = None
        drift_direction = "neutral"
        if prev and prev.key_themes and parsed.get("key_themes"):
            prev_set = set(t.lower() for t in prev.key_themes)
            new_set = set(t.lower() for t in parsed.get("key_themes", []))
            overlap = len(prev_set & new_set)
            total = max(len(prev_set | new_set), 1)
            drift_score = round((1 - overlap / total) * 100, 1)
            drift_direction = "stable" if drift_score < 20 else "shifting" if drift_score < 50 else "concerning"

        fp = SemanticFingerprint(
            brand_id=brand_id, scan_id=scan.id, model="ollama",
            embedding=embedding,
            key_themes=parsed.get("key_themes", []),
            narrative_summary=parsed.get("narrative_summary", ""),
            drift_score=drift_score, drift_direction=drift_direction,
        )
        db.session.add(fp)

        scan.status = "completed"
        scan.completed_at = datetime.now(timezone.utc)
        scan.summary = {"themes": len(parsed.get("key_themes", [])), "drift_score": drift_score,
                        "drift_direction": drift_direction}
        db.session.commit()

        return jsonify({"scan": scan.to_dict(), "fingerprint": fp.to_dict()})

    except Exception as e:
        scan.status = "failed"
        scan.summary = {"error": str(e)}
        db.session.commit()
        return jsonify({"error": str(e)}), 500


@semantic_bp.route("/api/fingerprint/<int:brand_id>", methods=["GET"])
def get_fingerprint(brand_id):
    """Get latest semantic fingerprint."""
    Brand.query.get_or_404(brand_id)
    fp = SemanticFingerprint.query.filter_by(brand_id=brand_id).order_by(
        SemanticFingerprint.created_at.desc()
    ).first()
    if not fp:
        return jsonify({"message": "No fingerprint yet", "fingerprint": None})
    return jsonify({"fingerprint": fp.to_dict()})


@semantic_bp.route("/api/drift/<int:brand_id>", methods=["GET"])
def get_drift(brand_id):
    """Get semantic drift history."""
    Brand.query.get_or_404(brand_id)
    fps = SemanticFingerprint.query.filter_by(brand_id=brand_id).order_by(
        SemanticFingerprint.created_at.desc()
    ).limit(20).all()
    return jsonify({
        "fingerprints": [f.to_dict() for f in fps],
        "total": len(fps),
        "latest_drift": fps[0].drift_score if fps and fps[0].drift_score is not None else None,
    })
