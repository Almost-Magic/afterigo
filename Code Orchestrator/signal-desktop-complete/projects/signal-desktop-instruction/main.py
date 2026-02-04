"""
Signal Desktop - Standalone LinkedIn Intelligence App
By Almost Magic Tech Lab

A desktop application for filtering LinkedIn posts by relevance.
No hosting required - everything runs locally!
"""

import webview
import json
import sys
from pathlib import Path


class SignalAPI:
    """Backend API for Signal Desktop."""
    
    def __init__(self):
        self.settings_file = Path.home() / ".signal_desktop_settings.json"
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from file."""
        default = {
            "topics": [
                "AI Governance",
                "Cybersecurity", 
                "Leadership",
                "Digital Transformation",
                "Startups",
                "SMB Technology"
            ],
            "minLikes": 10,
            "timeWindow": 14,
            "topPercent": 20
        }
        
        try:
            if self.settings_file.exists():
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    return {**default, **saved}
        except Exception as e:
            print(f"Could not load settings: {e}")
        
        return default
    
    def save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Could not save settings: {e}")
            return False
    
    def get_settings(self):
        """Return current settings."""
        return self.settings
    
    def add_topic(self, topic):
        """Add a topic."""
        topic = topic.strip()
        if topic and topic not in self.settings["topics"]:
            self.settings["topics"].append(topic)
            self.save_settings()
        return self.settings
    
    def remove_topic(self, topic):
        """Remove a topic."""
        if topic in self.settings["topics"]:
            self.settings["topics"].remove(topic)
            self.save_settings()
        return self.settings
    
    def update_setting(self, key, value):
        """Update a setting."""
        if key in ["minLikes", "timeWindow", "topPercent"]:
            self.settings[key] = int(value)
            self.save_settings()
        return self.settings
    
    def reset_settings(self):
        """Reset to defaults."""
        self.settings = {
            "topics": [
                "AI Governance",
                "Cybersecurity",
                "Leadership", 
                "Digital Transformation",
                "Startups",
                "SMB Technology"
            ],
            "minLikes": 10,
            "timeWindow": 14,
            "topPercent": 20
        }
        self.save_settings()
        return self.settings
    
    def get_bookmarklet(self):
        """Generate bookmarklet code."""
        settings_json = json.dumps(self.settings).replace('"', '\\"')
        
        bookmarklet = '''javascript:(function(){
if(window.SIGNAL_LOADED){if(window.SignalApp)window.SignalApp.reprocess();return}
window.SIGNAL_LOADED=true;
var S=''' + settings_json + ''';
var K={"AI Governance":["ai governance","responsible ai","ai ethics","ai regulation","ai compliance","iso 42001"],"Cybersecurity":["cybersecurity","infosec","data protection","zero trust","ransomware","iso 27001","ciso"],"Digital Transformation":["digital transformation","cloud migration","automation","agile"],"Leadership":["leadership","executive","management","ceo","cto"],"Startups":["startup","venture capital","founder","mvp","scaling"],"SMB Technology":["smb","small business","msp","saas"]};
var css=document.createElement("style");
css.textContent=".signal-badge{display:flex;align-items:center;gap:8px;padding:8px 12px;margin:8px 0;background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:8px;font-family:system-ui;font-size:13px;color:#fff;box-shadow:0 2px 8px rgba(0,0,0,.2)}.signal-score{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700}.signal-dimmed{opacity:.4}.signal-dimmed:hover{opacity:.8}.signal-toast{position:fixed;top:20px;right:20px;background:#8B5CF6;color:#fff;padding:16px 24px;border-radius:12px;font-family:system-ui;z-index:10000}";
document.head.appendChild(css);
var toast=document.createElement("div");toast.className="signal-toast";toast.id="signal-toast";toast.textContent="📡 Loading...";document.body.appendChild(toast);
var App={done:new Set(),n:0,hi:0,lo:0,
init:function(){this.run();new MutationObserver(function(){App.run()}).observe(document.body,{childList:true,subtree:true});this.msg()},
run:function(){var self=this;document.querySelectorAll("[data-urn*=activity],.feed-shared-update-v2").forEach(function(p){var id=p.getAttribute("data-urn")||Math.random();if(self.done.has(id))return;self.done.add(id);var r=self.calc(p);self.tag(p,r);self.n++;if(r.d=="hi")self.hi++;if(r.d=="lo")self.lo++});this.msg()},
calc:function(p){var t=(p.textContent||"").toLowerCase().slice(0,1500);var sc=0,tp=null;S.topics.forEach(function(x){var kw=K[x]||[x.toLowerCase()];var m=kw.filter(function(k){return t.includes(k)}).length;var v=Math.min(m*25,100);if(v>sc){sc=v;tp=x}});var lk=0;var b=p.querySelector("button[aria-label*=reaction]");if(b){var m=(b.getAttribute("aria-label")||"").match(/([0-9,]+)/);if(m)lk=parseInt(m[1].replace(/,/g,""))||0}var en=Math.min(lk*2,100);var f=Math.round(sc*.5+en*.35+50*.15);var d="ok";if(lk<S.minLikes)d="lo";else if(f>=70)d="hi";else if(f<30)d="lo";return{s:f,t:tp,l:lk,d:d}},
tag:function(p,r){var o=p.querySelector(".signal-badge");if(o)o.remove();var c=r.s>=70?"#22c55e":r.s>=50?"#eab308":r.s>=30?"#f97316":"#ef4444";var l=r.s>=70?"🔥 High":r.s>=50?"✅ OK":r.s>=30?"📊 Low":"⬇️ Skip";var b=document.createElement("div");b.className="signal-badge";b.innerHTML="<div class=signal-score style=background:"+c+">"+r.s+"</div><div style=font-weight:600>"+l+"</div><div style=margin-left:auto;font-size:11px;opacity:.7>"+(r.t||"")+(r.l?" 👍"+r.l:"")+"</div>";p.classList.remove("signal-dimmed");if(r.d=="lo")p.classList.add("signal-dimmed");var h=p.querySelector(".feed-shared-actor");if(h)h.after(b);else p.prepend(b)},
msg:function(){var t=document.getElementById("signal-toast");if(t){t.textContent="📡 "+this.n+" posts | "+this.hi+" 🔥 | "+this.lo+" dimmed";setTimeout(function(){if(t)t.remove()},5000)}},
reprocess:function(){this.done.clear();this.n=0;this.hi=0;this.lo=0;document.querySelectorAll(".signal-badge").forEach(function(x){x.remove()});document.querySelectorAll(".signal-dimmed").forEach(function(x){x.classList.remove("signal-dimmed")});var t=document.createElement("div");t.className="signal-toast";t.id="signal-toast";t.textContent="📡 Reloading...";document.body.appendChild(t);this.run()}};
App.init()})();'''
        
        # Remove newlines for bookmarklet
        bookmarklet = bookmarklet.replace('\n', '')
        
        return bookmarklet


def get_html():
    """Return the HTML for the app UI."""
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Signal Desktop</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 24px;
        }
        .container { max-width: 600px; margin: 0 auto; }
        
        h1 { font-size: 28px; margin-bottom: 8px; display: flex; align-items: center; gap: 12px; }
        .subtitle { color: #a0a0a0; margin-bottom: 32px; }
        
        .section { 
            background: rgba(255,255,255,0.05); 
            border-radius: 12px; 
            padding: 20px; 
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .section h2 { font-size: 16px; margin-bottom: 16px; color: #a0a0a0; }
        
        .topics { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; }
        .topic {
            background: rgba(139,92,246,0.2);
            border: 1px solid rgba(139,92,246,0.4);
            border-radius: 20px;
            padding: 6px 12px;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .topic .remove {
            cursor: pointer;
            opacity: 0.6;
            font-size: 16px;
        }
        .topic .remove:hover { opacity: 1; }
        
        .add-row { display: flex; gap: 8px; }
        .add-row input {
            flex: 1;
            padding: 10px 14px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            color: #fff;
            font-size: 14px;
        }
        .add-row input::placeholder { color: #666; }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-primary { background: #8B5CF6; color: #fff; }
        .btn-primary:hover { background: #7C3AED; }
        .btn-secondary { background: rgba(255,255,255,0.1); color: #fff; }
        .btn-secondary:hover { background: rgba(255,255,255,0.2); }
        .btn-large { padding: 16px 32px; font-size: 16px; width: 100%; }
        .btn-success { background: #22c55e; }
        .btn-success:hover { background: #16a34a; }
        
        .setting-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .setting-row select {
            padding: 8px 12px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 6px;
            color: #fff;
            font-size: 14px;
        }
        
        .bookmarklet-box {
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            padding: 12px;
            font-family: monospace;
            font-size: 11px;
            color: #a0a0a0;
            word-break: break-all;
            max-height: 80px;
            overflow: auto;
            margin-bottom: 12px;
        }
        
        .instructions {
            background: rgba(34,197,94,0.1);
            border: 1px solid rgba(34,197,94,0.3);
            border-radius: 8px;
            padding: 16px;
            margin-top: 20px;
        }
        .instructions h3 { color: #22c55e; margin-bottom: 12px; }
        .instructions ol { padding-left: 20px; }
        .instructions li { margin-bottom: 8px; color: #a0a0a0; font-size: 14px; }
        
        .footer { text-align: center; margin-top: 32px; color: #666; font-size: 12px; }
        
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #22c55e;
            color: #fff;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 14px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .toast.show { opacity: 1; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📡 Signal Desktop</h1>
        <p class="subtitle">Smart LinkedIn Post Filtering - No Extension Required</p>
        
        <div class="section">
            <h2>YOUR TOPICS</h2>
            <div class="topics" id="topicsList"></div>
            <div class="add-row">
                <input type="text" id="newTopic" placeholder="Add a topic (e.g., Machine Learning)">
                <button class="btn btn-primary" onclick="addTopic()">Add</button>
            </div>
        </div>
        
        <div class="section">
            <h2>FILTERS</h2>
            <div class="setting-row">
                <span>Minimum Likes</span>
                <select id="minLikes" onchange="updateSetting('minLikes', this.value)">
                    <option value="5">5+ likes</option>
                    <option value="10">10+ likes</option>
                    <option value="25">25+ likes</option>
                    <option value="50">50+ likes</option>
                </select>
            </div>
            <div class="setting-row">
                <span>Time Window</span>
                <select id="timeWindow" onchange="updateSetting('timeWindow', this.value)">
                    <option value="7">Last week</option>
                    <option value="14">Last 2 weeks</option>
                    <option value="30">Last month</option>
                </select>
            </div>
            <div class="setting-row">
                <span>Highlight Top</span>
                <select id="topPercent" onchange="updateSetting('topPercent', this.value)">
                    <option value="10">Top 10%</option>
                    <option value="20">Top 20%</option>
                    <option value="30">Top 30%</option>
                </select>
            </div>
            <button class="btn btn-secondary" style="width:100%;margin-top:8px" onclick="resetSettings()">Reset to Defaults</button>
        </div>
        
        <div class="section">
            <h2>YOUR BOOKMARKLET</h2>
            <div class="bookmarklet-box" id="bookmarkletCode">Loading...</div>
            <button class="btn btn-success btn-large" onclick="copyBookmarklet()">
                📋 Copy Bookmarklet to Clipboard
            </button>
            
            <div class="instructions">
                <h3>How to Use</h3>
                <ol>
                    <li>Click the button above to copy the bookmarklet</li>
                    <li>In your browser, create a new bookmark (Ctrl+D or Cmd+D)</li>
                    <li>Edit the bookmark and paste the code as the URL</li>
                    <li>Name it "📡 Signal"</li>
                    <li>Go to LinkedIn and click your new bookmark!</li>
                </ol>
            </div>
        </div>
        
        <div class="footer">
            Signal Desktop v2.1 by Almost Magic Tech Lab
        </div>
    </div>
    
    <div class="toast" id="toast">Copied!</div>
    
    <script>
        let settings = {};
        
        async function init() {
            settings = await pywebview.api.get_settings();
            renderTopics();
            renderFilters();
            updateBookmarklet();
        }
        
        function renderTopics() {
            const container = document.getElementById('topicsList');
            container.innerHTML = '';
            settings.topics.forEach(topic => {
                const el = document.createElement('span');
                el.className = 'topic';
                el.innerHTML = topic + '<span class="remove" onclick="removeTopic(\\''+topic+'\\')">×</span>';
                container.appendChild(el);
            });
        }
        
        function renderFilters() {
            document.getElementById('minLikes').value = settings.minLikes;
            document.getElementById('timeWindow').value = settings.timeWindow;
            document.getElementById('topPercent').value = settings.topPercent;
        }
        
        async function addTopic() {
            const input = document.getElementById('newTopic');
            const topic = input.value.trim();
            if (topic) {
                settings = await pywebview.api.add_topic(topic);
                input.value = '';
                renderTopics();
                updateBookmarklet();
            }
        }
        
        async function removeTopic(topic) {
            settings = await pywebview.api.remove_topic(topic);
            renderTopics();
            updateBookmarklet();
        }
        
        async function updateSetting(key, value) {
            settings = await pywebview.api.update_setting(key, parseInt(value));
            updateBookmarklet();
        }
        
        async function resetSettings() {
            if (confirm('Reset all settings to defaults?')) {
                settings = await pywebview.api.reset_settings();
                renderTopics();
                renderFilters();
                updateBookmarklet();
            }
        }
        
        async function updateBookmarklet() {
            const code = await pywebview.api.get_bookmarklet();
            document.getElementById('bookmarkletCode').textContent = code.slice(0, 200) + '...';
            window.bookmarkletCode = code;
        }
        
        function copyBookmarklet() {
            navigator.clipboard.writeText(window.bookmarkletCode).then(() => {
                const toast = document.getElementById('toast');
                toast.classList.add('show');
                setTimeout(() => toast.classList.remove('show'), 2000);
            });
        }
        
        document.getElementById('newTopic').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') addTopic();
        });
        
        window.addEventListener('pywebviewready', init);
    </script>
</body>
</html>
'''


def main():
    """Main entry point."""
    api = SignalAPI()
    
    window = webview.create_window(
        title='Signal Desktop',
        html=get_html(),
        js_api=api,
        width=650,
        height=800,
        resizable=True,
        min_size=(500, 600)
    )
    
    webview.start()


if __name__ == '__main__':
    main()