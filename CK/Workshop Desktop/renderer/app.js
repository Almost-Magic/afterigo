/**
 * The Workshop Desktop — Main UI Script
 * Author: Mani Padisetti
 * Almost Magic Tech Lab
 */

(function() {
    'use strict';
    
    let services = [], groups = [], tabs = [], activeTab = null;
    let expandedGroups = new Set(['Core']), theme = 'dark', recentApps = [];
    
    const ICONS = {
        'ELAINE': '🧠', 'Ripple CRM': '💼', 'Identity Atlas': '🆔', 'The Workshop API': '⚙️',
        'CK Writer': '✍️', 'Junk Drawer': '🎁', 'Opp Hunter': '🎯', 'Peterman': '📋',
        'Spark': '✨', 'Learning Assistant': '📚', 'Digital Sentinel': '🛡️',
        'CK Swiss Army Knife': '🔧', 'AMTL TTS': '🔊', 'ProcessLens': '🔍', 'Genie': '💰',
        'After I Go': '🏛️'
    };

    const LOADING_PORTS = [5000, 5005, 5006, 8000, 5173]; // Apps that take time to load
    
    // Check if a service is running by checking its port
    async function checkServiceRunning(port) {
        return new Promise((resolve) => {
            const http = require('http');
            const req = http.get(`http://127.0.0.1:${port}`, (res) => { resolve(true); });
            req.on('error', () => resolve(false));
            req.setTimeout(1000, () => { req.destroy(); resolve(false); });
        });
    }
    
    async function init() {
        loadSettings();
        applyTheme();
        await loadServices();
        setupEventListeners();
        setInterval(() => loadServices(), 10000);
    }
    
    async function loadServices() {
        try {
            const data = await window.workshop.getServices();
            services = data.services;
            groups = data.groups;
            renderSidebar();
            updateStatusBar();
        } catch (e) {
            console.error('Failed to load services:', e);
        }
    }
    
    function renderSidebar() {
        const container = document.getElementById('services-container');
        container.innerHTML = '';
        
        groups.forEach(groupName => {
            const groupSvcs = services.filter(s => s.group === groupName);
            if (!groupSvcs.length) return;
            
            const isExpanded = expandedGroups.has(groupName);
            const running = groupSvcs.filter(s => s.running).length;
            
        const el = document.createElement('div');
        el.className = 'group';
        el.innerHTML = `
            <div class="group-header ${isExpanded ? 'expanded' : ''}" data-group="${groupName}">
                <span class="group-arrow">${isExpanded ? '▼' : '▶'}</span>
                <span class="group-title">${groupName}</span>
                <span class="group-count">${running}/${groupSvcs.length}</span>
            </div>
            <div class="group-content ${isExpanded ? '' : 'collapsed'}">
                ${groupSvcs.map(svc => `
                    <div class="service-item ${activeTab === `http://localhost:${svc.port}` ? 'active' : ''}" 
                         data-name="${svc.name}" data-url="http://localhost:${svc.port}">
                        <div class="service-item-top">
                            <span class="service-icon">${ICONS[svc.name] || '⚡'}</span>
                            <span class="service-name">${svc.name}</span>
                            <span class="service-status status-${svc.running ? 'running' : (svc.installed ? 'stopped' : 'not-installed')}">
                                ${svc.running ? '●' : (svc.installed ? '○' : '◌')}
                            </span>
                        </div>
                        <div class="service-item-bottom">
                            <span class="service-port">:${svc.port}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
            
            el.querySelector('.group-header').addEventListener('click', () => {
                if (expandedGroups.has(groupName)) expandedGroups.delete(groupName);
                else expandedGroups.add(groupName);
                saveSettings();
                renderSidebar();
            });
            
            container.appendChild(el);
        });
    }
    
    function openService(name, url) {
        openAppTab(url, name);
        recentApps = [name, ...recentApps.filter(a => a !== name)].slice(0, 5);
        saveSettings();
    }
    
    async function openAppTab(url, name) {
        if (tabs.find(t => t.url === url)) {
            switchToTab(url);
            return;
        }
        if (tabs.length >= 8) return alert('Max 8 tabs');
        
        const port = parseInt(url.split(':')[2]);
        let svc = services.find(s => s.port === port);
        if (!svc && name) {
            svc = services.find(s => s.name === name) || { name, badge: ICONS[name] || '⚡' };
        }
        if (!svc) {
            const urlName = url.includes('localhost') ? `Service:${port}` : 'Web Tab';
            svc = { name: name || urlName, badge: '⚡' };
        }
        
        const isSlowApp = LOADING_PORTS.includes(port);
        const contentArea = document.getElementById('content-area');
        const wp = document.getElementById('welcome-panel');
        if (wp) wp.style.display = 'none';
        
        const container = document.createElement('div');
        container.className = 'webview-container';
        container.style.display = 'none';
        container.style.width = '100%';
        container.style.height = '100%';
        
        // Check if service is running before showing webview
        const isRunning = await checkServiceRunning(port);
        
        if (!isRunning && url.includes('localhost')) {
            // Show "not running" placeholder
            container.innerHTML = `
                <div class="not-running-panel">
                    <div class="not-running-icon">${ICONS[svc.name] || '⚡'}</div>
                    <h2>${svc.name}</h2>
                    <div class="status-text">Not Running</div>
                    <button class="start-btn" onclick="startAppFromPanel('${svc.name}', ${port})">
                        Start ${svc.name}
                    </button>
                    <div class="hint-text">Click to start the backend service</div>
                    <div class="port-text">Port: ${port}</div>
                </div>
            `;
            // Expose start function globally
            window.startAppFromPanel = async (appName, appPort) => {
                const btn = container.querySelector('.start-btn');
                btn.disabled = true;
                btn.textContent = 'Starting...';
                const result = await window.workshop.startService(appName);
                if (result.success) {
                    // Reload to show the app
                    setTimeout(() => {
                        openAppTab(url, name);
                    }, 2000);
                } else {
                    btn.disabled = false;
                    btn.textContent = 'Start Failed - ' + (result.error || 'Unknown error');
                }
            };
        } else if (isSlowApp) {
            // Add loading indicator for slow apps
            container.innerHTML = `
                <div class="loading-overlay" id="loading-${port}">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">Loading ${svc.name}...</div>
                </div>
                <webview data-url="${url}" src="${url}" style="width:100%;height:100%;border:none;" allowpopups></webview>
            `;
        } else {
            container.innerHTML = `<webview data-url="${url}" src="${url}" style="width:100%;height:100%;border:none;" allowpopups></webview>`;
        }
        contentArea.appendChild(container);
        
        // Listen for webview ready event
        const webview = container.querySelector('webview');
        webview.addEventListener('dom-ready', () => {
            const loadingEl = document.getElementById(`loading-${port}`);
            if (loadingEl) loadingEl.style.display = 'none';
        });
        
        // Fallback: hide loading after 5 seconds
        setTimeout(() => {
            const loadingEl = document.getElementById(`loading-${port}`);
            if (loadingEl) loadingEl.style.display = 'none';
        }, 5000);
        
        tabs.push({ id: Date.now().toString(), url, name: svc.name, icon: ICONS[svc.name] || svc.badge || '⚡' });
        renderTabs();
        switchToTab(url);
    }
    
    function switchToTab(url) {
        activeTab = url;
        renderTabs();
        const wp = document.getElementById('welcome-panel');
        if (wp) wp.style.display = tabs.length === 0 ? 'flex' : 'none';
        document.querySelectorAll('.webview-container').forEach(el => el.style.display = 'none');
        const wv = document.querySelector(`webview[data-url="${url}"]`);
        if (wv) wv.parentElement.style.display = 'block';
    }
    
    function closeTab(url, e) {
        e.stopPropagation();
        const idx = tabs.findIndex(t => t.url === url);
        tabs = tabs.filter(t => t.url !== url);
        
        const wvContainer = document.querySelector(`webview[data-url="${url}"]`);
        if (wvContainer && wvContainer.parentElement) {
            wvContainer.parentElement.remove();
        }
        
        if (activeTab === url) {
            if (tabs.length) switchToTab(tabs[Math.max(0, idx - 1)].url);
            else { activeTab = null; const wp = document.getElementById('welcome-panel'); if (wp) wp.style.display = 'flex'; }
        }
        renderTabs();
    }
    
    function renderTabs() {
        const tb = document.getElementById('tab-bar');
        tb.innerHTML = tabs.map(tab => `
            <div class="tab ${activeTab === tab.url ? 'active' : ''}" data-url="${tab.url}">
                <span class="tab-icon">${tab.icon}</span>
                <span class="tab-name">${tab.name}</span>
                <button class="tab-close" data-url="${tab.url}">×</button>
            </div>
        `).join('');
        
        tb.querySelectorAll('.tab').forEach(t => {
            t.addEventListener('click', e => {
                if (!e.target.classList.contains('tab-close')) switchToTab(t.dataset.url);
            });
        });
        
        tb.querySelectorAll('.tab-close').forEach(b => {
            b.addEventListener('click', e => closeTab(b.dataset.url, e));
        });
    }
    
    async function updateStatusBar() {
        const sa = document.getElementById('status-apps');
        const si = document.getElementById('status-infra');
        const sm = document.getElementById('status-message');
        const sauto = document.getElementById('status-autostart');
        
        const amtlApps = services.filter(s => ['Core AMTL', 'CK-Mani', 'CK', 'Intelligence', 'Marketing', 'Operations'].includes(s.group));
        const infraSvcs = services.filter(s => ['Infrastructure', 'Dev Tools'].includes(s.group));
        
        const runningApps = amtlApps.filter(s => s.running).length;
        const runningInfra = infraSvcs.filter(s => s.running).length;
        
        if (sa) sa.innerHTML = `● ${runningApps}/${amtlApps.length}`;
        if (si) si.innerHTML = `● ${runningInfra}/${infraSvcs.length}`;
        
        if (sauto) {
            try {
                const autoStart = await window.workshop.getAutoStart();
                sauto.innerHTML = `🚀 ${autoStart.autoStart ? 'On' : 'Off'}`;
            } catch (e) {
                sauto.innerHTML = '🚀 On';
            }
        }
        
        if (sm) {
            const allRunning = runningApps === amtlApps.length && amtlApps.length > 0;
            sm.textContent = allRunning ? 'All services running' : 
                           !runningApps ? 'No services running' : `${runningApps}/${amtlApps.length} apps running`;
        }
    }
    
    function toggleTheme() {
        theme = theme === 'dark' ? 'light' : 'dark';
        applyTheme();
        saveSettings();
    }
    
    function applyTheme() {
        document.body.className = `theme-${theme}`;
        const tt = document.getElementById('theme-toggle');
        if (tt) tt.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
    
    function setupEventListeners() {
        const tt = document.getElementById('theme-toggle');
        if (tt) tt.addEventListener('click', toggleTheme);
        
        document.getElementById('services-container').addEventListener('click', async e => {
            const item = e.target.closest('.service-item');
            if (item) {
                const svc = services.find(s => s.name === item.dataset.name);
                if (svc) {
                    // Check if this is a desktop app - launch in dedicated window
                    if (svc.hasDesktop) {
                        await window.workshop.openDesktop(svc.name);
                        recentApps = [svc.name, ...recentApps.filter(a => a !== svc.name)].slice(0, 5);
                        saveSettings();
                        return;
                    }
                    
                    // Web apps - open in tab
                    const url = svc.webviewUrl || `http://localhost:${svc.port}`;
                    openService(svc.name, url);
                }
            }
        });
        
        window.workshop.onServiceUpdate(data => {
            services = data.services;
            renderSidebar();
            updateStatusBar();
        });
        
        document.addEventListener('keydown', e => {
            if (e.ctrlKey && e.key >= '1' && e.key <= '8') {
                const idx = parseInt(e.key) - 1;
                if (tabs[idx]) switchToTab(tabs[idx].url);
            }
            if (e.ctrlKey && e.key === 'w' && activeTab) {
                e.preventDefault();
                closeTab(activeTab, e);
            }
            if (e.ctrlKey && e.key === 'd') {
                e.preventDefault();
                toggleTheme();
            }
        });
    }
    
    function loadSettings() {
        try {
            const saved = localStorage.getItem('workshop-settings');
            if (saved) {
                const data = JSON.parse(saved);
                theme = data.theme || 'dark';
                expandedGroups = new Set(data.expandedGroups || ['Core']);
                recentApps = data.recentApps || [];
            }
        } catch (e) {}
    }
    
    function saveSettings() {
        try {
            localStorage.setItem('workshop-settings', JSON.stringify({ theme, expandedGroups: Array.from(expandedGroups), recentApps }));
        } catch (e) {}
    }
    
    window.openAppTab = openAppTab;
    window.toggleTheme = toggleTheme;
    
    document.addEventListener('DOMContentLoaded', init);
})();
