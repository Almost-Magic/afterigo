"""
Peterman V4.1 — Chamber 3: Neural Vector Map
Embedding-based brand positioning and competitive mapping.
"""
from flask import Blueprint, jsonify, request
from ..models import db, Brand, Competitor, SemanticFingerprint
from ..services import ollama

vectormap_bp = Blueprint("vectormap", __name__)


def _cosine_sim(a, b):
    """Cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x * x for x in a) ** 0.5
    mag_b = sum(x * x for x in b) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return round(dot / (mag_a * mag_b), 4)


@vectormap_bp.route("/api/vectormap/<int:brand_id>/generate", methods=["POST"])
def generate_vectormap(brand_id):
    """Generate vector embeddings for brand and its competitors."""
    brand = Brand.query.get_or_404(brand_id)
    competitors = Competitor.query.filter_by(brand_id=brand_id).all()

    # Embed brand
    brand_text = f"{brand.name}: {brand.description or brand.industry or ''}"
    brand_embed = ollama.embed(brand_text)
    brand_vec = brand_embed.get("embedding", [])

    # Embed competitors
    comp_results = []
    for c in competitors:
        comp_text = f"{c.name}: {c.notes or ''}"
        comp_embed = ollama.embed(comp_text)
        comp_vec = comp_embed.get("embedding", [])
        similarity = _cosine_sim(brand_vec, comp_vec)
        comp_results.append({
            "id": c.id, "name": c.name, "domain": c.domain,
            "similarity": similarity,
            "relationship": c.relationship,
            "distance": round(1 - similarity, 4) if similarity else 1.0,
        })

    comp_results.sort(key=lambda x: x["similarity"], reverse=True)

    return jsonify({
        "brand": {"id": brand.id, "name": brand.name, "has_embedding": bool(brand_vec)},
        "competitors": comp_results,
        "total": len(comp_results),
        "closest": comp_results[0]["name"] if comp_results else None,
        "farthest": comp_results[-1]["name"] if comp_results else None,
    })


@vectormap_bp.route("/api/vectormap/<int:brand_id>/trajectory", methods=["GET"])
def vector_trajectory(brand_id):
    """Track how brand's semantic position has shifted over time."""
    Brand.query.get_or_404(brand_id)
    fps = SemanticFingerprint.query.filter_by(brand_id=brand_id).order_by(
        SemanticFingerprint.created_at.asc()
    ).all()

    trajectory = []
    for i, fp in enumerate(fps):
        point = {"date": fp.created_at.isoformat() if fp.created_at else None,
                 "themes": fp.key_themes, "drift_score": fp.drift_score}
        if i > 0 and fps[i - 1].key_themes and fp.key_themes:
            prev_set = set(t.lower() for t in fps[i - 1].key_themes)
            curr_set = set(t.lower() for t in fp.key_themes)
            point["themes_added"] = list(curr_set - prev_set)
            point["themes_lost"] = list(prev_set - curr_set)
        trajectory.append(point)

    return jsonify({"trajectory": trajectory, "total_snapshots": len(trajectory)})


@vectormap_bp.route("/api/vectormap/<int:brand_id>/neighbours", methods=["GET"])
def nearest_neighbours(brand_id):
    """Find which competitors are closest in vector space."""
    brand = Brand.query.get_or_404(brand_id)
    competitors = Competitor.query.filter_by(brand_id=brand_id).all()

    brand_text = f"{brand.name}: {brand.description or brand.industry or ''}"
    brand_embed = ollama.embed(brand_text)
    brand_vec = brand_embed.get("embedding", [])

    neighbours = []
    for c in competitors:
        comp_embed = ollama.embed(f"{c.name}: {c.notes or ''}")
        comp_vec = comp_embed.get("embedding", [])
        sim = _cosine_sim(brand_vec, comp_vec)
        neighbours.append({"name": c.name, "similarity": sim, "relationship": c.relationship})

    neighbours.sort(key=lambda x: x["similarity"], reverse=True)
    return jsonify({"brand": brand.name, "neighbours": neighbours[:10]})
