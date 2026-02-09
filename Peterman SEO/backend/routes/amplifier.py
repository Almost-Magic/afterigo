"""
Peterman V4.1 — Chamber 7: Amplifier
Citation probability, competitor shadow analysis, content atomisation.
"""
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from ..models import db, Brand, Competitor, Scan, CitationResult
from ..services import ollama, searxng

amplifier_bp = Blueprint("amplifier", __name__)


@amplifier_bp.route("/api/amplifier/<int:brand_id>/scan", methods=["POST"])
def run_amplifier_scan(brand_id):
    """Analyse citation probability and competitor shadow."""
    brand = Brand.query.get_or_404(brand_id)
    competitors = Competitor.query.filter_by(brand_id=brand_id).all()

    scan = Scan(brand_id=brand_id, scan_type="amplifier", status="running",
                chambers_run=["amplifier"], started_at=datetime.now(timezone.utc))
    db.session.add(scan)
    db.session.commit()

    try:
        queries = [
            f"Who are the best companies for {brand.industry or 'consulting'}?",
            f"Can you recommend a {brand.industry or 'technology'} provider?",
            f"What companies should I know about in {brand.industry or 'this space'}?",
        ]

        results = []
        for query in queries:
            llm_result = ollama.generate(query)
            response = llm_result.get("text", "")

            # Analyse citation
            brand_cited = brand.name.lower() in response.lower()
            comps_cited = [c.name for c in competitors if c.name.lower() in response.lower()]

            analysis = ollama.generate_json(
                f'Analyse this LLM response for brand citation patterns.\n'
                f'Query: "{query}"\nResponse: "{response[:1000]}"\n'
                f'Brand: "{brand.name}"\n'
                f'Return JSON: {{"citation_score": 0-100, "citation_context": "how the brand appears", '
                f'"shadow_brands": ["brands that appear instead"], '
                f'"recommendations": ["how to improve citation probability"]}}'
            )
            parsed = analysis.get("parsed") or {}

            cr = CitationResult(
                brand_id=brand_id, scan_id=scan.id, model="ollama",
                query=query, brand_cited=brand_cited,
                citation_context=parsed.get("citation_context", ""),
                competitors_cited=comps_cited,
                citation_score=parsed.get("citation_score", 0),
                shadow_brands=parsed.get("shadow_brands", []),
                recommendations=parsed.get("recommendations", []),
            )
            db.session.add(cr)
            results.append(cr)

        cited_count = sum(1 for r in results if r.brand_cited)
        avg_score = round(sum(r.citation_score or 0 for r in results) / max(len(results), 1), 1)

        scan.status = "completed"
        scan.completed_at = datetime.now(timezone.utc)
        scan.summary = {"queries": len(results), "brand_cited": cited_count,
                        "avg_citation_score": avg_score}
        scan.scores = {"amplifier_score": avg_score}
        db.session.commit()

        return jsonify({
            "scan": scan.to_dict(),
            "results": [r.to_dict() for r in results],
            "message": f"Amplifier scan complete. Cited in {cited_count}/{len(results)} queries.",
        })

    except Exception as e:
        scan.status = "failed"
        scan.summary = {"error": str(e)}
        db.session.commit()
        return jsonify({"error": str(e)}), 500


@amplifier_bp.route("/api/amplifier/<int:brand_id>", methods=["GET"])
def get_amplifier(brand_id):
    """Get latest citation results."""
    Brand.query.get_or_404(brand_id)
    results = CitationResult.query.filter_by(brand_id=brand_id).order_by(
        CitationResult.created_at.desc()
    ).limit(50).all()
    return jsonify({"results": [r.to_dict() for r in results], "total": len(results)})


@amplifier_bp.route("/api/amplifier/<int:brand_id>/shadow", methods=["GET"])
def competitor_shadow(brand_id):
    """Get competitor shadow analysis — who appears instead of you?"""
    Brand.query.get_or_404(brand_id)
    results = CitationResult.query.filter_by(brand_id=brand_id).order_by(
        CitationResult.created_at.desc()
    ).limit(20).all()

    shadow_counts = {}
    for r in results:
        for s in (r.shadow_brands or []):
            shadow_counts[s] = shadow_counts.get(s, 0) + 1

    shadows = [{"brand": k, "appearances": v} for k, v in
               sorted(shadow_counts.items(), key=lambda x: x[1], reverse=True)]

    return jsonify({"shadows": shadows, "total_queries": len(results)})
