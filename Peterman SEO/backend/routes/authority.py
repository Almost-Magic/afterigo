"""
Peterman V4.1 — Chamber 4: Authority Engine
SERP analysis, topical authority scoring via SearXNG.
"""
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from ..models import db, Brand, Keyword, Scan, AuthorityResult
from ..services import searxng

authority_bp = Blueprint("authority", __name__)


@authority_bp.route("/api/authority/<int:brand_id>/scan", methods=["POST"])
def run_authority_scan(brand_id):
    """Run SERP authority scan for all approved keywords."""
    brand = Brand.query.get_or_404(brand_id)
    keywords = Keyword.query.filter_by(brand_id=brand_id, status="approved").all()

    if not keywords:
        return jsonify({"error": "No approved keywords. Add and approve keywords first."}), 400

    scan = Scan(brand_id=brand_id, scan_type="authority", status="running",
                chambers_run=["authority"], started_at=datetime.now(timezone.utc))
    db.session.add(scan)
    db.session.commit()

    try:
        results = []
        total_score = 0
        for kw in keywords[:20]:  # Max 20 keywords per scan
            serp = searxng.serp_check(kw.keyword, brand.name)
            positions = serp.get("brand_positions", [])
            best_pos = min(positions) if positions else None

            # Score: top 3 = 100, top 10 = 60, top 20 = 30, absent = 0
            if best_pos and best_pos <= 3:
                kw_score = 100
            elif best_pos and best_pos <= 10:
                kw_score = 60
            elif best_pos and best_pos <= 20:
                kw_score = 30
            else:
                kw_score = 0

            ar = AuthorityResult(
                brand_id=brand_id, scan_id=scan.id, keyword=kw.keyword,
                brand_position=best_pos, in_top_3=serp.get("brand_in_top_3", False),
                in_top_10=serp.get("brand_in_top_10", False),
                competitors_above=serp.get("competitors_above", []),
                total_results=serp.get("total_results", 0),
                authority_score=kw_score,
            )
            db.session.add(ar)
            results.append(ar)
            total_score += kw_score

        avg_score = round(total_score / max(len(results), 1), 1)
        in_top_3_count = sum(1 for r in results if r.in_top_3)
        in_top_10_count = sum(1 for r in results if r.in_top_10)

        scan.status = "completed"
        scan.completed_at = datetime.now(timezone.utc)
        scan.summary = {"keywords_scanned": len(results), "avg_authority_score": avg_score,
                        "in_top_3": in_top_3_count, "in_top_10": in_top_10_count}
        scan.scores = {"authority_score": avg_score}
        db.session.commit()

        return jsonify({
            "scan": scan.to_dict(),
            "results": [r.to_dict() for r in results],
            "message": f"Authority scan complete. Avg score: {avg_score}",
        })

    except Exception as e:
        scan.status = "failed"
        scan.summary = {"error": str(e)}
        db.session.commit()
        return jsonify({"error": str(e)}), 500


@authority_bp.route("/api/authority/<int:brand_id>", methods=["GET"])
def get_authority(brand_id):
    """Get latest authority results."""
    Brand.query.get_or_404(brand_id)
    results = AuthorityResult.query.filter_by(brand_id=brand_id).order_by(
        AuthorityResult.created_at.desc()
    ).limit(50).all()
    return jsonify({"results": [r.to_dict() for r in results], "total": len(results)})


@authority_bp.route("/api/authority/<int:brand_id>/gaps", methods=["GET"])
def authority_gaps(brand_id):
    """Find keywords where brand is missing from top results."""
    Brand.query.get_or_404(brand_id)
    results = AuthorityResult.query.filter_by(brand_id=brand_id).order_by(
        AuthorityResult.created_at.desc()
    ).all()

    # Deduplicate by keyword, keep latest
    seen = {}
    for r in results:
        if r.keyword not in seen:
            seen[r.keyword] = r

    gaps = [r.to_dict() for r in seen.values() if not r.in_top_10]
    strong = [r.to_dict() for r in seen.values() if r.in_top_3]

    return jsonify({"gaps": gaps, "strong": strong,
                    "gap_count": len(gaps), "strong_count": len(strong)})
