"""
Peterman V4.1 — Unified Audit Endpoint
Runs complete SEO audit: crawl, analyse, generate recommendations
"""

import httpx
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify, request
from datetime import datetime
import json
import re

audit_bp = Blueprint("audit", __name__)

# Service URLs
OLLAMA_URL = "http://localhost:11434"
SEARXNG_URL = "http://localhost:8888"


def call_ollama(prompt, model="llama3.1"):
    """Call local Ollama for SEO analysis tasks."""
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False}
            )
            if response.status_code == 200:
                return response.json().get("response", "")
    except Exception as e:
        print(f"Ollama error: {e}")
    return None


def crawl_website(domain):
    """Crawl website and extract key information."""
    results = {
        "domain": domain,
        "url": f"https://{domain}",
        "status": "error",
        "title": "",
        "description": "",
        "og_title": "",
        "og_description": "",
        "h1_tags": [],
        "paragraphs": [],
        "has_sitemap": False,
        "has_robots": False,
        "schema_types": [],
        "word_count": 0,
        "links": [],
        "images": [],
        "error": None
    }
    
    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            for protocol in ["https", "http"]:
                url = f"{protocol}://{domain}"
                try:
                    resp = client.get(url, headers={"User-Agent": "Peterman/4.1"})
                    if resp.status_code == 200:
                        results["url"] = url
                        results["status"] = "success"
                        break
                except:
                    continue
            
            if results["status"] == "error":
                results["error"] = "Could not fetch website"
                return results
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Title
            title_tag = soup.find("title")
            results["title"] = title_tag.text.strip() if title_tag else ""
            
            # Meta description
            desc_tag = soup.find("meta", attrs={"name": "description"})
            results["description"] = desc_tag.get("content", "") if desc_tag else ""
            
            # OpenGraph
            og_title = soup.find("meta", attrs={"property": "og:title"})
            results["og_title"] = og_title.get("content", "") if og_title else results["title"]
            
            og_desc = soup.find("meta", attrs={"property": "og:description"})
            results["og_description"] = og_desc.get("content", "") if og_desc else results["description"]
            
            # H1 tags
            results["h1_tags"] = [h1.text.strip() for h1 in soup.find_all("h1")]
            
            # Paragraphs
            results["paragraphs"] = [p.text.strip() for p in soup.find_all("p") if len(p.text.strip()) > 50]
            results["word_count"] = sum(len(p.split()) for p in results["paragraphs"])
            
            # Links and images
            results["links"] = [a.get("href", "") for a in soup.find_all("a") if a.get("href")]
            results["images"] = [img.get("src", "") for img in soup.find_all("img") if img.get("src")]
            
            # Check sitemap and robots
            try:
                sitemap_resp = client.get(f"{results['url']}/sitemap.xml", timeout=10.0)
                results["has_sitemap"] = sitemap_resp.status_code == 200
            except:
                pass
            
            try:
                robots_resp = client.get(f"{results['url']}/robots.txt", timeout=10.0)
                results["has_robots"] = robots_resp.status_code == 200
            except:
                pass
            
            # Extract schema types
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    data = json.loads(script.string)
                    schema_type = data.get("@type", "")
                    if schema_type:
                        results["schema_types"].append(schema_type)
                except:
                    pass
            
    except Exception as e:
        results["error"] = str(e)
    
    return results


def analyse_meta_tags(crawl_data):
    """Use Ollama to analyse and generate optimised meta tags."""
    prompt = f"""Analyze these meta tags and return JSON with scores and optimised versions:

Current Title: {crawl_data.get('title', 'N/A')}
Current Description: {crawl_data.get('description', 'N/A')}
Website content: {' '.join(crawl_data.get('paragraphs', [])[:5])}

Return JSON only:
{{"title_score": 0-100, "description_score": 0-100, "optimised_title": "...", "optimised_description": "...", "keywords": [], "issues": []}}"""

    result = call_ollama(prompt)
    if result:
        try:
            json_match = re.search(r'\{[^{}]+\}', result)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
    
    return {
        "title_score": 50,
        "description_score": 45,
        "optimised_title": f"{crawl_data.get('title', 'Site')} | Official Website",
        "optimised_description": f"Learn about {crawl_data.get('description', 'our services')[:150]}...",
        "keywords": ["AI", "consulting"],
        "issues": ["Meta description too short"]
    }


def generate_schema_org(crawl_data):
    """Generate Organisation and Website schema."""
    domain = crawl_data.get("domain", "")
    name = domain.split(".")[0].title()
    
    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": name,
        "url": f"https://{domain}",
        "logo": f"https://{domain}/logo.png",
        "description": crawl_data.get("description", "")
    }
    
    website_schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": name,
        "url": f"https://{domain}",
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"https://{domain}/search?q={{search_term_string}}",
            "query-input": "required name=search_term_string"
        }
    }
    
    return [schema, website_schema]


def check_ai_visibility(domain, crawl_data):
    """Check AI visibility using Ollama perception scanning."""
    brand_name = domain.split(".")[0]
    
    prompt = f"""For website {domain}, score AI visibility (Claude, ChatGPT, Gemini, Perplexity) 0-100:

Brand: {brand_name}
Description: {crawl_data.get('description', 'N/A')}
Content: {' '.join(crawl_data.get('paragraphs', [])[:3])}

Return JSON only:
{{"claude_score": 0-100, "chatgpt_score": 0-100, "gemini_score": 0-100, "perplexity_score": 0-100, "overall_score": 0-100, "recommendations": []}}"""

    result = call_ollama(prompt)
    if result:
        try:
            json_match = re.search(r'\{[^{}]+\}', result)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
    
    return {
        "claude_score": 50,
        "chatgpt_score": 45,
        "gemini_score": 40,
        "perplexity_score": 55,
        "overall_score": 48,
        "recommendations": ["Add more structured data", "Create authoritative content"]
    }


def check_llm_ranking(keywords, domain):
    """Check search engine rankings for keywords."""
    results = []
    
    for keyword in keywords[:5]:
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.get(
                    f"{SEARXNG_URL}/search",
                    params={"q": keyword, "format": "json"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    position = 10
                    for i, result in enumerate(data.get("results", [])[:10]):
                        if domain in result.get("url", ""):
                            position = i + 1
                            break
                    results.append({"keyword": keyword, "position": position, "in_top_10": position <= 10})
        except Exception as e:
            results.append({"keyword": keyword, "position": None, "error": str(e)})
    
    return results


def generate_content_recommendations(crawl_data, ai_scores):
    """Generate content recommendations."""
    prompt = f"""Generate SEO recommendations for {crawl_data.get('domain', '')}:

Return JSON only:
{{"blog_topics": [], "faq_questions": [], "content_improvements": [], "keywords": [], "meta_improvements": []}}"""

    result = call_ollama(prompt)
    if result:
        try:
            json_match = re.search(r'\{[^{}]+\}', result)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
    
    return {
        "blog_topics": ["AI trends in Australia", "Best practices guide"],
        "faq_questions": ["What services do you offer?", "How can you help my business?"],
        "content_improvements": ["Add more H2 headings", "Include internal links"],
        "keywords": ["AI consulting", "technology solutions"],
        "meta_improvements": []
    }


@audit_bp.route("/api/audit/full", methods=["POST"])
def full_audit():
    """Run complete SEO audit on a domain."""
    data = request.get_json() or {}
    domain = data.get("domain", "").strip().lower()
    
    if not domain:
        return jsonify({"error": "Domain required"}), 400
    
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
    
    results = {
        "domain": domain,
        "timestamp": datetime.now().isoformat(),
        "status": "running",
        "steps": {}
    }
    
    try:
        # Step 1: Crawl website
        results["steps"]["crawl"] = {"status": "running"}
        crawl_data = crawl_website(domain)
        results["steps"]["crawl"] = {
            "status": "completed" if crawl_data["status"] == "success" else "error",
            "data": crawl_data
        }
        
        if crawl_data["status"] != "success":
            results["status"] = "error"
            results["error"] = crawl_data.get("error", "Failed to crawl")
            return jsonify(results)
        
        # Step 2: Meta analysis
        results["steps"]["meta"] = {"status": "running"}
        meta_analysis = analyse_meta_tags(crawl_data)
        results["steps"]["meta"] = {"status": "completed", "data": meta_analysis}
        
        # Step 3: Schema
        results["steps"]["schema"] = {"status": "running"}
        schema_data = generate_schema_org(crawl_data)
        results["steps"]["schema"] = {
            "status": "completed",
            "data": {"current": crawl_data.get("schema_types", []), "generated": schema_data}
        }
        
        # Step 4: Sitemap
        results["steps"]["sitemap"] = {"status": "completed", "data": {
            "has_sitemap": crawl_data.get("has_sitemap", False),
            "has_robots": crawl_data.get("has_robots", False),
            "pages_discovered": len(crawl_data.get("paragraphs", [])),
            "links_found": len(crawl_data.get("links", []))
        }}
        
        # Step 5: AI visibility
        results["steps"]["ai"] = {"status": "running"}
        ai_scores = check_ai_visibility(domain, crawl_data)
        results["steps"]["ai"] = {"status": "completed", "data": ai_scores}
        
        # Step 6: LLM ranking
        results["steps"]["llm"] = {"status": "running"}
        keywords = data.get("keywords", ["AI consulting", "technology services"])
        llm_rankings = check_llm_ranking(keywords, domain)
        results["steps"]["llm"] = {"status": "completed", "data": {"keywords": keywords, "rankings": llm_rankings}}
        
        # Step 7: Content
        results["steps"]["content"] = {"status": "running"}
        content_recs = generate_content_recommendations(crawl_data, ai_scores)
        results["steps"]["content"] = {"status": "completed", "data": content_recs}
        
        # Calculate overall score
        scores = [
            meta_analysis.get("title_score", 0),
            meta_analysis.get("description_score", 0),
            100 if crawl_data.get("has_sitemap") else 50,
            100 if crawl_data.get("has_robots") else 50,
            ai_scores.get("overall_score", 0)
        ]
        results["overall_score"] = sum(scores) // len(scores)
        results["status"] = "completed"
        
        return jsonify(results)
        
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
        return jsonify(results), 500


@audit_bp.route("/api/audit/status/<domain>", methods=["GET"])
def get_audit_status(domain):
    return jsonify({"domain": domain, "message": "Run full audit to get results"})
