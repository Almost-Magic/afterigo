"""
Peterman V4.1 — Chamber 8: The Proof
Visitor intelligence, lead identification, ROI tracking via Snitcher.
"""
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from ..models import db, Brand, VisitorLead
from ..services import snitcher

proof_bp = Blueprint("proof", __name__)


@proof_bp.route("/api/proof/<int:brand_id>/visitors", methods=["POST"])
def fetch_visitors(brand_id):
    """Fetch and score website visitors via Snitcher."""
    brand = Brand.query.get_or_404(brand_id)
    if not brand.domain:
        return jsonify({"error": "Brand has no domain set"}), 400

    data = request.get_json() or {}
    result = snitcher.get_visitors(
        brand.domain,
        date_from=data.get("date_from"),
        date_to=data.get("date_to"),
        limit=data.get("limit", 50),
    )

    if result.get("error"):
        return jsonify(result), 503

    leads = []
    for v in result.get("visitors", []):
        # Score each visitor
        score_data = snitcher.score_visitor(v, brand.target_audience)

        lead = VisitorLead(
            brand_id=brand_id,
            company_name=v.get("company"),
            company_domain=v.get("domain"),
            industry=v.get("industry"),
            employee_count=str(v.get("employee_count", "")),
            location=v.get("location"),
            pages_viewed=v.get("pages_viewed", []),
            visit_count=v.get("visit_count", 1),
            lead_score=score_data["score"],
            lead_tier=score_data["tier"],
            score_reasons=score_data["reasons"],
        )
        db.session.add(lead)
        leads.append(lead)

    db.session.commit()

    return jsonify({
        "leads": [l.to_dict() for l in leads],
        "total": len(leads),
        "hot": sum(1 for l in leads if l.lead_tier == "hot"),
        "warm": sum(1 for l in leads if l.lead_tier == "warm"),
        "cool": sum(1 for l in leads if l.lead_tier == "cool"),
    })


@proof_bp.route("/api/proof/<int:brand_id>/leads", methods=["GET"])
def list_leads(brand_id):
    """Get all leads for a brand, sorted by score."""
    Brand.query.get_or_404(brand_id)
    tier = request.args.get("tier")
    query = VisitorLead.query.filter_by(brand_id=brand_id)
    if tier:
        query = query.filter_by(lead_tier=tier)
    leads = query.order_by(VisitorLead.lead_score.desc()).limit(100).all()
    return jsonify({"leads": [l.to_dict() for l in leads], "total": len(leads)})


@proof_bp.route("/api/proof/<int:brand_id>/leads/hot", methods=["GET"])
def hot_leads(brand_id):
    """Get hot leads only."""
    Brand.query.get_or_404(brand_id)
    leads = VisitorLead.query.filter_by(brand_id=brand_id, lead_tier="hot").order_by(
        VisitorLead.lead_score.desc()
    ).limit(50).all()
    return jsonify({"leads": [l.to_dict() for l in leads], "total": len(leads)})


@proof_bp.route("/api/proof/<int:brand_id>/summary", methods=["GET"])
def proof_summary(brand_id):
    """Get proof-of-impact summary for a brand."""
    Brand.query.get_or_404(brand_id)
    all_leads = VisitorLead.query.filter_by(brand_id=brand_id).all()
    hot = [l for l in all_leads if l.lead_tier == "hot"]
    warm = [l for l in all_leads if l.lead_tier == "warm"]

    return jsonify({
        "total_leads": len(all_leads),
        "hot": len(hot), "warm": len(warm), "cool": len(all_leads) - len(hot) - len(warm),
        "avg_score": round(sum(l.lead_score for l in all_leads) / max(len(all_leads), 1), 1),
        "top_industries": _top_values([l.industry for l in all_leads if l.industry]),
        "top_companies": [{"name": l.company_name, "score": l.lead_score} for l in
                          sorted(all_leads, key=lambda x: x.lead_score, reverse=True)[:5]],
    })


def _top_values(items, limit=5):
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return [{"value": k, "count": v} for k, v in
            sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]]
