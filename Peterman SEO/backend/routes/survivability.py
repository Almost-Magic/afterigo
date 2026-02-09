"""
Peterman V4.1 — Chamber 5: Survivability Lab
Content preservation testing — does the LLM remember your brand accurately?
"""
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from ..models import db, Brand, Scan, SurvivabilityResult
from ..services import ollama

survivability_bp = Blueprint("survivability", __name__)


@survivability_bp.route("/api/survivability/<int:brand_id>/test", methods=["POST"])
def run_survivability_test(brand_id):
    """Test how well LLMs preserve brand content."""
    brand = Brand.query.get_or_404(brand_id)

    scan = Scan(brand_id=brand_id, scan_type="survivability", status="running",
                chambers_run=["survivability"], started_at=datetime.now(timezone.utc))
    db.session.add(scan)
    db.session.commit()

    try:
        # Build content items to test preservation of
        test_items = []
        if brand.tagline:
            test_items.append(("tagline", brand.tagline))
        if brand.description:
            test_items.append(("description", brand.description[:200]))
        for vp in (brand.value_propositions or [])[:3]:
            test_items.append(("value_prop", vp))
        for diff in (brand.differentiators or [])[:2]:
            test_items.append(("differentiator", diff))
        if brand.industry:
            test_items.append(("fact", f"{brand.name} operates in {brand.industry}"))

        if not test_items:
            test_items = [("fact", f"{brand.name} is a company")]

        results = []
        total_accuracy = 0

        for content_type, original in test_items:
            # Ask the LLM to recall this information
            prompt = f'What do you know about {brand.name}? Specifically, what is their {content_type}? ' \
                     f'If you know their {content_type}, state it exactly.'
            llm_result = ollama.generate(prompt)
            recall_text = llm_result.get("text", "")

            # Use LLM to score accuracy
            score_result = ollama.generate_json(
                f'Compare the original brand content with what the LLM recalled.\n'
                f'Original: "{original}"\nLLM Recall: "{recall_text[:500]}"\n'
                f'Return JSON: {{"accuracy": 0-100, "preserved": true/false, '
                f'"distortion": "description of any distortion or null"}}'
            )
            parsed = score_result.get("parsed") or {}
            accuracy = parsed.get("accuracy", 0)
            total_accuracy += accuracy

            sr = SurvivabilityResult(
                brand_id=brand_id, scan_id=scan.id, model="ollama",
                content_type=content_type, original_content=original,
                llm_recall=recall_text[:2000], recall_accuracy=accuracy,
                preserved=parsed.get("preserved", False),
                distortion_notes=parsed.get("distortion"),
            )
            db.session.add(sr)
            results.append(sr)

        avg_accuracy = round(total_accuracy / max(len(results), 1), 1)
        preserved_count = sum(1 for r in results if r.preserved)

        scan.status = "completed"
        scan.completed_at = datetime.now(timezone.utc)
        scan.summary = {"items_tested": len(results), "avg_accuracy": avg_accuracy,
                        "preserved": preserved_count, "lost": len(results) - preserved_count}
        scan.scores = {"survivability_score": avg_accuracy}
        db.session.commit()

        return jsonify({
            "scan": scan.to_dict(),
            "results": [r.to_dict() for r in results],
            "message": f"Survivability test complete. {preserved_count}/{len(results)} items preserved.",
        })

    except Exception as e:
        scan.status = "failed"
        scan.summary = {"error": str(e)}
        db.session.commit()
        return jsonify({"error": str(e)}), 500


@survivability_bp.route("/api/survivability/<int:brand_id>", methods=["GET"])
def get_survivability(brand_id):
    """Get latest survivability results."""
    Brand.query.get_or_404(brand_id)
    results = SurvivabilityResult.query.filter_by(brand_id=brand_id).order_by(
        SurvivabilityResult.created_at.desc()
    ).limit(50).all()
    return jsonify({"results": [r.to_dict() for r in results], "total": len(results)})
