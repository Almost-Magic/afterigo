"""
Peterman V4.1 — Chamber 10: The Forge
Content production pipeline — generate briefs and content from perception gaps.
"""
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from ..models import db, Brand, Scan, ContentBrief, Hallucination, AuthorityResult
from ..services import ollama

forge_bp = Blueprint("forge", __name__)


@forge_bp.route("/api/forge/<int:brand_id>/generate", methods=["POST"])
def generate_briefs(brand_id):
    """Generate content briefs based on perception gaps and authority gaps."""
    brand = Brand.query.get_or_404(brand_id)

    scan = Scan(brand_id=brand_id, scan_type="forge", status="running",
                chambers_run=["forge"], started_at=datetime.now(timezone.utc))
    db.session.add(scan)
    db.session.commit()

    try:
        briefs = []

        # 1. Generate correction briefs from hallucinations
        hallucinations = Hallucination.query.filter_by(brand_id=brand_id).filter(
            Hallucination.status.in_(["detected", "confirmed"])
        ).limit(5).all()

        for h in hallucinations:
            result = ollama.generate_json(
                f'Create a content brief to correct this hallucination about "{brand.name}".\n'
                f'Hallucinated claim: "{h.hallucinated_claim}"\n'
                f'Actual truth: "{h.actual_truth or "needs research"}"\n'
                f'Return JSON: {{"title": "article title", "brief_type": "correction", '
                f'"outline": ["point 1", "point 2", "point 3"], '
                f'"target_keyword": "primary keyword to target"}}'
            )
            parsed = result.get("parsed") or {}
            if parsed.get("title"):
                brief = ContentBrief(
                    brand_id=brand_id, title=parsed["title"],
                    brief_type="correction", target_keyword=parsed.get("target_keyword", ""),
                    gap_source="perception", outline=parsed.get("outline", []),
                )
                db.session.add(brief)
                briefs.append(brief)

        # 2. Generate authority briefs from SERP gaps
        gaps = AuthorityResult.query.filter_by(brand_id=brand_id).filter(
            AuthorityResult.in_top_10 == False
        ).limit(5).all()

        for gap in gaps:
            result = ollama.generate_json(
                f'Create a content brief to improve SERP ranking for "{brand.name}" '
                f'on keyword "{gap.keyword}".\n'
                f'Return JSON: {{"title": "article title", "brief_type": "blog", '
                f'"outline": ["section 1", "section 2", "section 3"], '
                f'"target_keyword": "{gap.keyword}"}}'
            )
            parsed = result.get("parsed") or {}
            if parsed.get("title"):
                brief = ContentBrief(
                    brand_id=brand_id, title=parsed["title"],
                    brief_type=parsed.get("brief_type", "blog"),
                    target_keyword=gap.keyword, gap_source="authority",
                    outline=parsed.get("outline", []),
                )
                db.session.add(brief)
                briefs.append(brief)

        # 3. If no gaps found, generate general thought leadership
        if not briefs:
            result = ollama.generate_json(
                f'Create 3 thought leadership content briefs for "{brand.name}" '
                f'in {brand.industry or "their industry"}.\n'
                f'Return JSON: {{"briefs": [{{"title": "...", "brief_type": "blog", '
                f'"outline": ["..."], "target_keyword": "..."}}]}}'
            )
            parsed = result.get("parsed") or {}
            for b in parsed.get("briefs", [])[:3]:
                if b.get("title"):
                    brief = ContentBrief(
                        brand_id=brand_id, title=b["title"],
                        brief_type=b.get("brief_type", "blog"),
                        target_keyword=b.get("target_keyword", ""),
                        gap_source="oracle", outline=b.get("outline", []),
                    )
                    db.session.add(brief)
                    briefs.append(brief)

        scan.status = "completed"
        scan.completed_at = datetime.now(timezone.utc)
        scan.summary = {"briefs_generated": len(briefs),
                        "correction": sum(1 for b in briefs if b.brief_type == "correction"),
                        "authority": sum(1 for b in briefs if b.gap_source == "authority"),
                        "thought_leadership": sum(1 for b in briefs if b.gap_source == "oracle")}
        db.session.commit()

        return jsonify({
            "scan": scan.to_dict(),
            "briefs": [b.to_dict() for b in briefs],
            "message": f"Forge complete. {len(briefs)} content briefs generated.",
        })

    except Exception as e:
        scan.status = "failed"
        scan.summary = {"error": str(e)}
        db.session.commit()
        return jsonify({"error": str(e)}), 500


@forge_bp.route("/api/forge/<int:brand_id>/briefs", methods=["GET"])
def list_briefs(brand_id):
    """Get all content briefs for a brand."""
    Brand.query.get_or_404(brand_id)
    status = request.args.get("status")
    query = ContentBrief.query.filter_by(brand_id=brand_id)
    if status:
        query = query.filter_by(status=status)
    briefs = query.order_by(ContentBrief.created_at.desc()).limit(50).all()
    return jsonify({"briefs": [b.to_dict() for b in briefs], "total": len(briefs)})


@forge_bp.route("/api/forge/<int:brand_id>/briefs/<int:brief_id>/generate", methods=["POST"])
def generate_content(brand_id, brief_id):
    """Generate full content from a brief using LLM."""
    brand = Brand.query.get_or_404(brand_id)
    brief = ContentBrief.query.filter_by(id=brief_id, brand_id=brand_id).first_or_404()

    outline_text = "\n".join(f"- {o}" for o in (brief.outline or []))
    result = ollama.generate(
        f'Write a {brief.brief_type} article for {brand.name} ({brand.industry or ""}).\n'
        f'Title: {brief.title}\nTarget keyword: {brief.target_keyword}\n'
        f'Outline:\n{outline_text}\n\n'
        f'Write professional, SEO-optimised content. 500-800 words.',
        max_tokens=4096,
    )

    brief.generated_content = result.get("text", "")
    brief.status = "draft"
    db.session.commit()

    return jsonify({"brief": brief.to_dict(), "message": "Content generated"})


@forge_bp.route("/api/forge/<int:brand_id>/briefs/<int:brief_id>/approve", methods=["PUT"])
def approve_brief(brand_id, brief_id):
    """Approve a content brief or draft."""
    brief = ContentBrief.query.filter_by(id=brief_id, brand_id=brand_id).first_or_404()
    brief.status = "approved"
    db.session.commit()
    return jsonify({"brief": brief.to_dict(), "message": "Brief approved"})


@forge_bp.route("/api/forge/<int:brand_id>/pipeline", methods=["GET"])
def pipeline_status(brand_id):
    """Get content pipeline status."""
    Brand.query.get_or_404(brand_id)
    briefs = ContentBrief.query.filter_by(brand_id=brand_id).all()

    return jsonify({
        "total": len(briefs),
        "draft": sum(1 for b in briefs if b.status == "draft"),
        "approved": sum(1 for b in briefs if b.status == "approved"),
        "published": sum(1 for b in briefs if b.status == "published"),
        "rejected": sum(1 for b in briefs if b.status == "rejected"),
        "by_type": _count_by(briefs, "brief_type"),
        "by_source": _count_by(briefs, "gap_source"),
    })


def _count_by(items, attr):
    counts = {}
    for item in items:
        val = getattr(item, attr, "unknown") or "unknown"
        counts[val] = counts.get(val, 0) + 1
    return counts
