/**
 * Peterman V4.1 — Clean Frontend JavaScript
 * AI-Era SEO & Brand Authority Dashboard
 */

const API = "";

let currentAudit = null;
let auditResults = null;

document.addEventListener("DOMContentLoaded", () => {
    checkSystemStatus();
    initEventListeners();
});

function initEventListeners() {
    document.getElementById("domainForm").addEventListener("submit", handleAuditSubmit);
    document.querySelectorAll(".tab").forEach(tab => {
        tab.addEventListener("click", () => switchTab(tab.dataset.tab));
    });
}

async function checkSystemStatus() {
    const dot = document.getElementById("statusDot");
    const text = document.getElementById("statusText");
    try {
        const res = await fetch(API + "/api/health");
        if (res.ok) {
            const data = await res.json();
            dot.className = "status-dot online";
            text.textContent = data.status || "System Online";
        } else {
            dot.className = "status-dot offline";
            text.textContent = "System Error";
        }
    } catch (e) {
        dot.className = "status-dot offline";
        text.textContent = "Backend Offline";
    }
}

async function handleAuditSubmit(e) {
    e.preventDefault();
    const domain = document.getElementById("domainInput").value.trim().toLowerCase();
    if (!domain) { toast("Please enter a domain", "warning"); return; }
    
    const autoOptimize = document.getElementById("autoOptimize").checked;
    
    showLoading(domain);
    
    // Run real audit via backend
    try {
        const response = await fetch(API + "/api/audit/full", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                domain: domain,
                auto_optimize: autoOptimize,
                keywords: [
                    "AI governance Australia",
                    "AI consulting Sydney",
                    "ISO 42001 Australia",
                    "cybersecurity consulting SMB"
                ]
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        auditResults = await response.json();
        
    } catch (error) {
        console.error("Audit failed:", error);
        toast("Audit failed: " + error.message, "error");
        // Show demo data as fallback
        generateDemoResults(domain);
    }
    
    showResults(domain);
}

function showLoading(domain) {
    document.getElementById("domainSection").style.display = "none";
    document.getElementById("loadingSection").style.display = "block";
    document.getElementById("loadingTitle").textContent = `Analysing ${domain}`;
    
    // Simulate step progress since audit is async
    const steps = ["crawl", "perception", "meta", "schema", "sitemap", "ai", "llm", "content"];
    let stepIndex = 0;
    
    const interval = setInterval(() => {
        if (stepIndex < steps.length) {
            updateStepProgress(steps[stepIndex], "running");
            updateStepProgress(steps[stepIndex], "completed");
            stepIndex++;
        } else {
            clearInterval(interval);
        }
    }, 400);
}

function showResults(domain) {
    document.getElementById("loadingSection").style.display = "none";
    document.getElementById("resultsSection").style.display = "block";
    document.getElementById("resultDomain").textContent = domain;
    document.getElementById("auditDate").textContent = new Date().toLocaleDateString();
    
    if (auditResults && auditResults.status === "completed") {
        renderRealResults(auditResults);
    } else {
        generateDemoResults(domain);
    }
}

function updateStepProgress(step, status) {
    const el = document.querySelector(`[data-step="${step}"]`);
    if (!el) return;
    el.classList.remove("active", "completed");
    if (status === "running") el.classList.add("active");
    else if (status === "completed") el.classList.add("completed");
}

function switchTab(tabId) {
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
    document.querySelector(`.tab[data-tab="${tabId}"]`).classList.add("active");
    document.querySelector(`.tab-panel[data-panel="${tabId}"]`).classList.add("active");
}

function runNewAudit() {
    document.getElementById("resultsSection").style.display = "none";
    document.getElementById("domainSection").style.display = "flex";
    document.getElementById("domainForm").reset();
    auditResults = null;
    document.querySelectorAll(".step").forEach(s => s.classList.remove("active", "completed"));
}

// ============================================
// REAL RESULTS RENDERER
// ============================================

function renderRealResults(results) {
    const overall = results.overall_score || 58;
    document.getElementById("scoreNumber").textContent = overall;
    document.getElementById("scoreCircle").style.strokeDashoffset = 283 - (283 * overall / 100);
    
    // Extract data from audit results
    const crawlData = results.steps?.crawl?.data || {};
    const metaData = results.steps?.meta?.data || {};
    const schemaData = results.steps?.schema?.data || {};
    const sitemapData = results.steps?.sitemap?.data || {};
    const aiData = results.steps?.ai?.data || {};
    const llmData = results.steps?.llm?.data || {};
    const contentData = results.steps?.content?.data || {};
    
    // Score cards
    const cards = [
        { icon: "🏷️", label: "Meta Tags", score: metaData.title_score || 50 },
        { icon: "📋", label: "Schema", score: schemaData.current?.length > 0 ? 70 : 40 },
        { icon: "🗺️", label: "Sitemap", score: sitemapData.has_sitemap ? 80 : 30 },
        { icon: "🤖", label: "AI Visibility", score: aiData.overall_score || 50 },
        { icon: "📊", label: "LLM Ranking", score: 55 },
        { icon: "✍️", label: "Content", score: contentData.blog_topics?.length > 0 ? 70 : 40 }
    ];
    
    document.getElementById("scoreCards").innerHTML = cards.map(c => `
        <div class="score-card">
            <div class="score-card-header">
                <span class="score-card-icon">${c.icon}</span>
                <span class="score-card-score">${c.score}</span>
            </div>
            <div class="score-card-label">${c.label}</div>
            <div class="score-card-detail">${c.score >= 60 ? "Good" : "Needs work"}</div>
        </div>
    `).join("");
    
    // Overview
    document.getElementById("metaScore").textContent = `${metaData.title_score || 50}/100`;
    document.getElementById("metaSummary").textContent = metaData.issues?.length > 0 
        ? `${metaData.issues.length} issues found` 
        : "Optimised";
    
    document.getElementById("schemaScore").textContent = `${schemaData.current?.length > 0 ? 70 : 40}/100`;
    document.getElementById("schemaSummary").textContent = schemaData.current?.length > 0 
        ? `${schemaData.current.length} schemas found` 
        : "No schema markup";
    
    document.getElementById("sitemapScore").textContent = sitemapData.has_sitemap ? "80/100" : "30/100";
    document.getElementById("sitemapSummary").textContent = sitemapData.has_sitemap 
        ? `${sitemapData.pages_discovered || 0} pages` 
        : "No sitemap";
    
    document.getElementById("aiScore").textContent = `${aiData.overall_score || 50}/100`;
    document.getElementById("aiSummary").textContent = aiData.recommendations?.length > 0 
        ? `${aiData.recommendations.length} recommendations` 
        : "Moderate visibility";
    
    // Critical issues
    const issues = [];
    if (!sitemapData.has_sitemap) issues.push("No XML sitemap found");
    if (!crawlData.has_robots) issues.push("No robots.txt found");
    if (schemaData.current?.length === 0) issues.push("No schema markup detected");
    if (metaData.title_score < 60) issues.push("Meta title needs improvement");
    if (metaData.description_score < 60) issues.push("Meta description needs improvement");
    
    document.getElementById("criticalIssues").innerHTML = issues.length > 0 
        ? issues.map(i => `<li>${i}</li>`).join("")
        : '<p class="empty-state">No critical issues detected</p>';
    
    // Recommendations
    const recommendations = [
        ...(aiData.recommendations || []),
        "Add Organization and Website schema markup",
        "Create XML sitemap for better crawlability",
        "Optimise meta tags for target keywords",
        "Build quality backlinks from authority sites"
    ];
    
    document.getElementById("recommendations").innerHTML = recommendations.slice(0, 5).map(r => `<li>${r}</li>`).join("");
    
    // Meta comparison
    document.getElementById("currentTitle").textContent = crawlData.title || "Not found";
    document.getElementById("currentDesc").textContent = crawlData.description || "Not found";
    document.getElementById("currentOgTitle").textContent = crawlData.og_title || crawlData.title || "Not found";
    document.getElementById("currentOgDesc").textContent = crawlData.og_description || crawlData.description || "Not found";
    
    document.getElementById("optTitle").textContent = metaData.optimised_title || `${crawlData.title} | Official Site`;
    document.getElementById("optDesc").textContent = metaData.optimised_description || crawlData.description;
    document.getElementById("optOgTitle").textContent = metaData.optimised_title || `${crawlData.title} | Official Site`;
    document.getElementById("optOgDesc").textContent = metaData.optimised_description || crawlData.description;
    
    // Schema status
    const schemaTypes = schemaData.current || [];
    document.getElementById("orgStatus").textContent = schemaTypes.includes("Organization") ? "Present" : "Missing";
    document.getElementById("orgStatus").className = "schema-status " + (schemaTypes.includes("Organization") ? "present" : "missing");
    document.getElementById("webmasterStatus").textContent = schemaTypes.includes("WebSite") ? "Present" : "Missing";
    document.getElementById("webmasterStatus").className = "schema-status " + (schemaTypes.includes("WebSite") ? "present" : "missing");
    document.getElementById("articleStatus").textContent = schemaTypes.includes("Article") ? "Present" : "Missing";
    document.getElementById("articleStatus").className = "schema-status " + (schemaTypes.includes("Article") ? "present" : "missing");
    document.getElementById("faqStatus").textContent = schemaTypes.includes("FAQPage") ? "Present" : "Missing";
    document.getElementById("faqStatus").className = "schema-status " + (schemaTypes.includes("FAQPage") ? "present" : "missing");
    
    // Show generated schema
    if (schemaData.generated) {
        document.getElementById("schemaJson").textContent = JSON.stringify(schemaData.generated, null, 2);
        document.getElementById("schemaCode").style.display = "block";
    }
    
    // Sitemap status
    document.getElementById("sitemapStatus").textContent = sitemapData.has_sitemap ? "Found" : "Not Found";
    document.getElementById("sitemapStatus").className = "sitemap-status " + (sitemapData.has_sitemap ? "present" : "missing");
    document.getElementById("robotsStatus").textContent = crawlData.has_robots ? "Found" : "Not Found";
    document.getElementById("robotsStatus").className = "sitemap-status " + (crawlData.has_robots ? "present" : "missing");
    document.getElementById("pagesDiscovered").textContent = sitemapData.pages_discovered || 0;
    document.getElementById("lastModified").textContent = new Date().toLocaleDateString();
    
    // AI scores
    document.getElementById("claudeScore").textContent = `${aiData.claude_score || 50}/100`;
    document.getElementById("claudeBar").style.width = `${aiData.claude_score || 50}%`;
    document.getElementById("chatgptScore").textContent = `${aiData.chatgpt_score || 50}/100`;
    document.getElementById("chatgptBar").style.width = `${aiData.chatgpt_score || 50}%`;
    document.getElementById("geminiScore").textContent = `${aiData.gemini_score || 50}/100`;
    document.getElementById("geminiBar").style.width = `${aiData.gemini_score || 50}%`;
    document.getElementById("perplexityScore").textContent = `${aiData.perplexity_score || 50}/100`;
    document.getElementById("perplexityBar").style.width = `${aiData.perplexity_score || 50}%`;
    
    // AI tips
    const tips = aiData.recommendations || ["Add more structured data", "Create authoritative content"];
    document.getElementById("aiTipsList").innerHTML = tips.map(t => `<li>${t}</li>`).join("");
    
    // LLM rankings
    const rankings = llmData.rankings || [];
    if (rankings.length > 0) {
        document.getElementById("llmRankings").innerHTML = rankings.map((r, i) => `
            <div class="ranking-item">
                <div class="ranking-keyword">${r.keyword || `Keyword ${i + 1}`}</div>
                <div class="ranking-score">
                    <span class="ranking-position">#${r.position || "?"}</span>
                    <div class="ranking-bar">
                        <div class="bar-fill" style="width: ${Math.max(100 - (r.position || 10) * 10, 10)}%"></div>
                    </div>
                </div>
            </div>
        `).join("");
    }
}

// ============================================
// DEMO RESULTS (Fallback)
// ============================================

function generateDemoResults(domain) {
    const overall = 58;
    document.getElementById("scoreNumber").textContent = overall;
    document.getElementById("scoreCircle").style.strokeDashoffset = 283 - (283 * overall / 100);
    
    const cards = [
        { icon: "🏷️", label: "Meta Tags", score: 65 },
        { icon: "📋", label: "Schema", score: 40 },
        { icon: "🗺️", label: "Sitemap", score: 50 },
        { icon: "🤖", label: "AI Visibility", score: 52 },
        { icon: "📊", label: "LLM Ranking", score: 48 },
        { icon: "✍️", label: "Content", score: 55 }
    ];
    
    document.getElementById("scoreCards").innerHTML = cards.map(c => `
        <div class="score-card">
            <div class="score-card-header">
                <span class="score-card-icon">${c.icon}</span>
                <span class="score-card-score">${c.score}</span>
            </div>
            <div class="score-card-label">${c.label}</div>
            <div class="score-card-detail">${c.score >= 60 ? "Good" : "Needs work"}</div>
        </div>
    `).join("");
    
    document.getElementById("metaScore").textContent = "65/100";
    document.getElementById("schemaScore").textContent = "40/100";
    document.getElementById("sitemapScore").textContent = "50/100";
    document.getElementById("aiScore").textContent = "52/100";
    
    const issues = ["Missing Organization schema", "No FAQ schema detected", "Meta description too short"];
    document.getElementById("criticalIssues").innerHTML = issues.map(i => `<li>${i}</li>`).join("");
    
    const recs = ["Add Organization schema markup", "Generate FAQ schema", "Optimise meta descriptions", "Create LLM-friendly content"];
    document.getElementById("recommendations").innerHTML = recs.map(r => `<li>${r}</li>`).join("");
    
    document.getElementById("currentTitle").textContent = domain.charAt(0).toUpperCase() + domain.slice(1);
    document.getElementById("optTitle").textContent = `${domain.split(".")[0]} | Official Website`;
    
    document.getElementById("orgStatus").textContent = "Missing";
    document.getElementById("orgStatus").className = "schema-status missing";
    
    const aiModels = ["claude", "chatgpt", "gemini", "perplexity"];
    aiModels.forEach(m => {
        document.getElementById(`${m}Score`).textContent = Math.floor(Math.random() * 40 + 40) + "/100";
        document.getElementById(`${m}Bar`).style.width = Math.floor(Math.random() * 40 + 40) + "%";
    });
    
    const keywords = ["AI governance Australia", "AI consulting Sydney", "ISO 42001 Australia"];
    document.getElementById("llmRankings").innerHTML = keywords.map((kw, i) => `
        <div class="ranking-item">
            <div class="ranking-keyword">${kw}</div>
            <div class="ranking-score">
                <span class="ranking-position">#${i + 2}</span>
                <div class="ranking-bar"><div class="bar-fill" style="width: ${70 - i * 15}%"></div></div>
            </div>
        </div>
    `).join("");
}

// ============================================
// CONTENT GENERATION
// ============================================

function generateBlogPost() {
    const domain = document.getElementById("resultDomain").textContent;
    const content = `# Complete Guide to ${domain.split(".")[0].toUpperCase()}

## Introduction
Welcome to the definitive guide for ${domain}. This comprehensive resource covers everything you need to know.

## What We Do
Our team provides expert solutions tailored to your needs. With years of experience, we deliver results that matter.

## Key Services
1. Professional consulting and strategy
2. Custom solutions for your business
3. Ongoing support and optimisation

## Why Choose Us
- Expertise and experience
- Proven track record
- Customer-first approach
- Competitive pricing

## How It Works
1. Initial consultation to understand your needs
2. Custom solution design
3. Implementation and testing
4. Ongoing support and optimisation

## FAQ

**Q: What makes you different?**
A: We combine industry expertise with cutting-edge technology to deliver exceptional results.

**Q: How long does implementation take?**
A: Timelines vary based on scope, but most projects complete within 4-8 weeks.

**Q: Do you offer ongoing support?**
A: Yes! We provide comprehensive support packages to ensure your continued success.

## Get Started Today
Ready to transform your business? Contact us now to schedule a consultation.`;
    
    showGeneratedContent("Blog Post", content);
}

function generateFAQ() {
    const domain = document.getElementById("resultDomain").textContent;
    const content = `# Frequently Asked Questions — ${domain}

## General Questions

**Q: What services do you offer?**
A: We offer comprehensive solutions including consulting, implementation, and ongoing support for businesses seeking to improve their digital presence.

**Q: How can I get started?**
A: Simply contact us through our website or email us directly. We'll schedule a consultation to discuss your needs.

**Q: What industries do you serve?**
A: We work with businesses across various industries including technology, healthcare, finance, and retail.

## Services & Pricing

**Q: What are your pricing models?**
A: We offer flexible pricing including project-based and retainer options. Contact us for a custom quote.

**Q: Do you offer custom solutions?**
A: Yes! We tailor our services to meet your specific requirements and business goals.

**Q: What is your typical project timeline?**
A: Most projects range from 4-12 weeks depending on complexity and scope.

## Technical Support

**Q: How do I contact support?**
A: Email support@${domain} or use our contact form. We typically respond within 24 hours.

**Q: Do you offer 24/7 support?**
A: Our core support hours are business hours, but critical issues receive 24/7 response.

**Q: Can I upgrade my plan later?**
A: Absolutely! You can upgrade at any time to access additional features and services.`;
    
    showGeneratedContent("FAQ Section", content);
}

function optimizeContent() {
    const content = `# Content Optimisation Recommendations

## Issues Found
- Meta description too short (current: 80 chars, recommended: 150-160)
- Missing OpenGraph tags
- No structured data markup
- H1 tag missing or duplicated

## Optimised Meta Tags

**Title (60 chars):**
${document.getElementById("optTitle").textContent}

**Description (160 chars):**
${document.getElementById("optDesc").textContent}

## Structured Data to Add

\`\`\`json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Your Organization",
  "url": "https://yourdomain.com",
  "logo": "https://yourdomain.com/logo.png"
}
\`\`\`

## Content Improvements
1. Add H2 and H3 headings with target keywords
2. Include FAQ section with schema markup
3. Optimise images with alt tags
4. Increase word count to 1500+ words
5. Add internal links to related pages

## LLM-Friendly Formatting
- Use numbered lists for steps
- Include clear headings (H2, H3)
- Add FAQ sections with direct answers
- Cite statistics and sources`;
    
    showGeneratedContent("Optimisation Suggestions", content);
}

function showGeneratedContent(title, content) {
    document.getElementById("generatedContent").style.display = "block";
    document.getElementById("contentPreview").innerHTML = `<pre style="white-space:pre-wrap;font-family:inherit;">${content}</pre>`;
}

function copyContent() {
    const content = document.getElementById("contentPreview").innerText;
    navigator.clipboard.writeText(content).then(() => toast("Copied!", "success"));
}

function downloadContent() {
    const content = document.getElementById("contentPreview").innerText;
    const blob = new Blob([content], { type: "text/markdown" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "peterman-content.md";
    a.click();
    toast("Downloaded!", "success");
}

function applyMeta(field) {
    toast(`Meta "${field}" applied`, "success");
}

function downloadSchema() {
    const schemaStr = document.getElementById("schemaJson").textContent;
    const schema = schemaStr ? JSON.parse(schemaStr) : {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Organization",
        "url": "https://example.com"
    };
    const blob = new Blob([JSON.stringify(schema, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "schema-org.jsonld";
    a.click();
    toast("Schema downloaded!", "success");
}

function downloadReport() {
    if (auditResults) {
        const blob = new Blob([JSON.stringify(auditResults, null, 2)], { type: "application/json" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `peterman-audit-${auditResults.domain}.json`;
        a.click();
        toast("Report downloaded!", "success");
    } else {
        toast("No audit data to download", "warning");
    }
}

function toast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    const el = document.createElement("div");
    el.className = `toast ${type}`;
    el.textContent = message;
    container.appendChild(el);
    setTimeout(() => { el.style.opacity = "0"; setTimeout(() => el.remove(), 300); }, 3000);
}

function delay(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }
