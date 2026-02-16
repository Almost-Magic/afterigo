"""
Peterman V4.1 — Chamber 9: The Oracle
Predictive scanning, trend detection, industry framing analysis.
"""
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from ..models import db, Brand, Scan, TrendSignal
from ..services import ai_engine, searxng

oracle_bp = Blueprint("oracle", __name__)


@oracle_bp.route("/api/oracle/<int:brand_id>/scan", methods=["POST"])
def run_oracle_scan(brand_id):
    """Scan for industry trends, opportunities and threats."""
    brand = Brand.query.get_or_404(brand_id)
    industry = brand.industry or "technology"

    scan = Scan(brand_id=brand_id, scan_type="oracle", status="running",
                chambers_run=["oracle"], started_at=datetime.now(timezone.utc))
    db.session.add(scan)
    db.session.commit()

    try:
        # Search for trends via SearXNG
        trends_result = searxng.search_trends(industry)
        news_results = trends_result.get("results", [])

        signals = []
        for article in news_results[:10]:
            # Analyse each article for relevance to brand
            analysis = ai_engine.generate_json(
                f'Analyse this news article for relevance to "{brand.name}" ({industry}).\n'
                f'Title: "{article.get("title", "")}"\n'
                f'Content: "{article.get("content", "")[:500]}"\n'
                f'Return JSON: {{"signal_type": "trend|opportunity|threat|shift", '
                f'"relevance_score": 0-100, "urgency": "low|medium|high|critical", '
                f'"summary": "1-2 sentence summary", '
                f'"recommendation": "what the brand should do about this"}}'
            )
            parsed = analysis.get("parsed") or {}

            if parsed.get("relevance_score", 0) < 20:
                continue  # Skip low-relevance signals

            ts = TrendSignal(
                brand_id=brand_id, scan_id=scan.id,
                signal_type=parsed.get("signal_type", "trend"),
                title=article.get("title", "Untitled"),
                summary=parsed.get("summary", ""),
                source_url=article.get("url", ""),
                relevance_score=parsed.get("relevance_score", 0),
                urgency=parsed.get("urgency", "low"),
                recommendation=parsed.get("recommendation", ""),
            )
            db.session.add(ts)
            signals.append(ts)

        scan.status = "completed"
        scan.completed_at = datetime.now(timezone.utc)
        scan.summary = {"articles_scanned": len(news_results), "signals_found": len(signals),
                        "high_urgency": sum(1 for s in signals if s.urgency in ("high", "critical"))}
        scan.scores = {"oracle_score": round(sum(s.relevance_score or 0 for s in signals) / max(len(signals), 1), 1)}
        db.session.commit()

        return jsonify({
            "scan": scan.to_dict(),
            "signals": [s.to_dict() for s in signals],
            "message": f"Oracle scan complete. {len(signals)} signals detected.",
        })

    except Exception as e:
        scan.status = "failed"
        scan.summary = {"error": str(e)}
        db.session.commit()
        return jsonify({"error": str(e)}), 500


@oracle_bp.route("/api/oracle/<int:brand_id>/signals", methods=["GET"])
def list_signals(brand_id):
    """Get trend signals for a brand."""
    Brand.query.get_or_404(brand_id)
    signal_type = request.args.get("type")
    query = TrendSignal.query.filter_by(brand_id=brand_id)
    if signal_type:
        query = query.filter_by(signal_type=signal_type)
    signals = query.order_by(TrendSignal.relevance_score.desc()).limit(50).all()
    return jsonify({"signals": [s.to_dict() for s in signals], "total": len(signals)})


@oracle_bp.route("/api/oracle/<int:brand_id>/forecast", methods=["GET"])
def brand_forecast(brand_id):
    """Get predictive forecast based on accumulated signals."""
    Brand.query.get_or_404(brand_id)
    signals = TrendSignal.query.filter_by(brand_id=brand_id).order_by(
        TrendSignal.created_at.desc()
    ).limit(30).all()

    opportunities = [s for s in signals if s.signal_type == "opportunity"]
    threats = [s for s in signals if s.signal_type == "threat"]
    trends = [s for s in signals if s.signal_type == "trend"]

    outlook = "positive" if len(opportunities) > len(threats) else \
              "cautious" if len(threats) > len(opportunities) else "neutral"

    return jsonify({
        "outlook": outlook,
        "opportunities": len(opportunities),
        "threats": len(threats),
        "trends": len(trends),
        "top_opportunities": [s.to_dict() for s in sorted(opportunities, key=lambda x: x.relevance_score or 0, reverse=True)[:3]],
        "top_threats": [s.to_dict() for s in sorted(threats, key=lambda x: x.relevance_score or 0, reverse=True)[:3]],
    })
