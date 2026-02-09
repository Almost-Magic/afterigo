"""
Peterman V4.1 — Chamber 6: Machine Interface
Technical SEO audits — JSON-LD, schema, sitemap, robots.txt.
"""
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from ..models import db, Brand, Scan, TechnicalAudit
from ..services import searxng
import httpx
import re
import logging

logger = logging.getLogger(__name__)
machine_bp = Blueprint("machine", __name__)


def _check_url(url, timeout=10):
    """Check if a URL is accessible."""
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            r = client.get(url)
            return r.status_code, r.text
    except Exception:
        return None, ""


@machine_bp.route("/api/technical/<int:brand_id>/audit", methods=["POST"])
def run_technical_audit(brand_id):
    """Run technical SEO audit on brand's domain."""
    brand = Brand.query.get_or_404(brand_id)
    if not brand.domain:
        return jsonify({"error": "Brand has no domain set"}), 400

    domain = brand.domain.rstrip("/")
    if not domain.startswith("http"):
        domain = "https://" + domain

    scan = Scan(brand_id=brand_id, scan_type="technical", status="running",
                chambers_run=["machine"], started_at=datetime.now(timezone.utc))
    db.session.add(scan)
    db.session.commit()

    try:
        issues = []

        # Check homepage for JSON-LD and OpenGraph
        status, html = _check_url(domain)
        has_jsonld = bool(html and 'application/ld+json' in html)
        has_opengraph = bool(html and 'og:title' in html)

        if not has_jsonld:
            issues.append({"type": "missing_jsonld", "severity": "high",
                           "message": "No JSON-LD structured data found on homepage"})
        if not has_opengraph:
            issues.append({"type": "missing_opengraph", "severity": "medium",
                           "message": "No OpenGraph meta tags found"})

        # Extract schema types from JSON-LD
        schema_types = []
        if has_jsonld and html:
            for match in re.findall(r'"@type"\s*:\s*"([^"]+)"', html):
                if match not in schema_types:
                    schema_types.append(match)

        # Check sitemap
        sitemap_status, _ = _check_url(domain + "/sitemap.xml")
        has_sitemap = sitemap_status == 200
        if not has_sitemap:
            issues.append({"type": "missing_sitemap", "severity": "medium",
                           "message": "No sitemap.xml found"})

        # Check robots.txt
        robots_status, robots_text = _check_url(domain + "/robots.txt")
        has_robots = robots_status == 200 and bool(robots_text)
        if not has_robots:
            issues.append({"type": "missing_robots", "severity": "low",
                           "message": "No robots.txt found"})

        # Score
        score = 0
        if status and status < 400:
            score += 20
        if has_jsonld:
            score += 25
        if has_opengraph:
            score += 15
        if has_sitemap:
            score += 20
        if has_robots:
            score += 10
        if schema_types:
            score += 10

        audit = TechnicalAudit(
            brand_id=brand_id, scan_id=scan.id, domain=domain,
            has_jsonld=has_jsonld, has_opengraph=has_opengraph,
            has_sitemap=has_sitemap, has_robots=has_robots,
            schema_types=schema_types, issues=issues, score=score,
        )
        db.session.add(audit)

        scan.status = "completed"
        scan.completed_at = datetime.now(timezone.utc)
        scan.summary = {"score": score, "issues": len(issues), "schema_types": schema_types}
        scan.scores = {"technical_score": score}
        db.session.commit()

        return jsonify({"scan": scan.to_dict(), "audit": audit.to_dict()})

    except Exception as e:
        scan.status = "failed"
        scan.summary = {"error": str(e)}
        db.session.commit()
        return jsonify({"error": str(e)}), 500


@machine_bp.route("/api/technical/<int:brand_id>", methods=["GET"])
def get_technical(brand_id):
    """Get latest technical audit results."""
    Brand.query.get_or_404(brand_id)
    audits = TechnicalAudit.query.filter_by(brand_id=brand_id).order_by(
        TechnicalAudit.created_at.desc()
    ).limit(10).all()
    return jsonify({"audits": [a.to_dict() for a in audits], "total": len(audits)})


@machine_bp.route("/api/technical/<int:brand_id>/checklist", methods=["GET"])
def technical_checklist(brand_id):
    """Get technical SEO checklist with current status."""
    Brand.query.get_or_404(brand_id)
    latest = TechnicalAudit.query.filter_by(brand_id=brand_id).order_by(
        TechnicalAudit.created_at.desc()
    ).first()

    checklist = [
        {"item": "JSON-LD Structured Data", "status": latest.has_jsonld if latest else False, "priority": "high"},
        {"item": "OpenGraph Meta Tags", "status": latest.has_opengraph if latest else False, "priority": "medium"},
        {"item": "XML Sitemap", "status": latest.has_sitemap if latest else False, "priority": "medium"},
        {"item": "Robots.txt", "status": latest.has_robots if latest else False, "priority": "low"},
        {"item": "Schema.org Types", "status": bool(latest and latest.schema_types), "priority": "high"},
    ]
    return jsonify({"checklist": checklist, "last_audit": latest.to_dict() if latest else None})
