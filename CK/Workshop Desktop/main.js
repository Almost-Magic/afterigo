/**
 * The Workshop Desktop — Electron Main Process
 * Author: Mani Padisetti
 * Almost Magic Tech Lab
 */

const { app, BrowserWindow, ipcMain, Menu, Tray, nativeImage } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Fix PATH for packaged Electron apps on Windows
if (process.platform === 'win32') {
  const systemRoot = process.env.SystemRoot || 'C:\\WINDOWS';
  const existingPath = process.env.PATH || '';
  const systemDirs = [
    `${systemRoot}\\system32`,
    `${systemRoot}`,
    `${systemRoot}\\System32\\Wbem`
  ];
  // Prepend system dirs if missing (don't overwrite existing PATH)
  const missingDirs = systemDirs.filter(d => !existingPath.toLowerCase().includes(d.toLowerCase()));
  if (missingDirs.length > 0) {
    process.env.PATH = missingDirs.join(';') + ';' + existingPath;
  }
}

// Spawn helper with proper environment
function spawnService(command, args, options = {}) {
  return spawn(command, args, {
    shell: true,
    env: { ...process.env, PATH: process.env.PATH },
    windowsHide: true,
    ...options
  });
}

// Constants
const APP_NAME = 'The Workshop Desktop';
const APP_VERSION = '1.0.0';
const BASE_PATH = 'C:\\Users\\ManiPadisetti\\Dropbox\\Desktop DB\\Books and Articles Mani\\Books\\Almost Magic Tech Lab AMTL\\Source and Brand';

// Global references
let mainWindow = null;
let tray = null;

// Service Registry — 8 groups with 24+ services
const GROUPS = ['Core AMTL', 'CK-Mani', 'CK', 'Intelligence', 'Marketing', 'Operations', 'Infrastructure', 'Dev Tools'];

// Service registry with CSS badge colours
const SERVICES = [
    // Group 1: Core AMTL
    { name: 'ELAINE', group: 'Core AMTL', port: 5000, type: 'Python', badge: 'E', badgeColor: '#E06C75', hasDesktop: false, processes: [{ cmd: 'python', args: ['app.py'], cwd: 'CK\\Elaine\\elaine_v4', port: 5000 }] },
    { name: 'The Workshop API', group: 'Core AMTL', port: 5003, type: 'Python', badge: 'W', badgeColor: '#C9944A', hasDesktop: false, processes: [{ cmd: 'python', args: ['app.py'], cwd: 'CK\\Hub', port: 5003 }] },
    { name: 'Sophia', group: 'Core AMTL', port: 5010, type: 'Python', badge: 'S', badgeColor: '#C678DD', hasDesktop: false, processes: [{ cmd: 'python', args: ['app.py'], cwd: 'Sophia', port: 5010 }] },
    { name: 'AMTL TTS', group: 'Core AMTL', port: 5015, type: 'Python', badge: 'T', badgeColor: '#56B6C2', hasDesktop: false, processes: [{ cmd: 'python', args: ['app.py'], cwd: 'AMTL TTS', port: 5015 }] },
    
    // Group 2: CK-Mani
    { name: 'CK Writer', group: 'CK-Mani', port: 5004, type: 'Node', badge: 'W', badgeColor: '#E5C07B', hasDesktop: false, processes: [{ cmd: 'node', args: ['server.js'], cwd: 'CK\\ck-mani-writer', port: 5004 }] },
    { name: 'Learning Assistant', group: 'CK-Mani', port: 5012, type: 'Node', badge: 'L', badgeColor: '#61AFEF', hasDesktop: false, processes: [{ cmd: 'node', args: ['server.js'], cwd: 'CK\\Learning Assistant', port: 5012 }] },
    
    // Group 3: CK
    { name: 'Ripple CRM', group: 'CK', port: 5001, type: 'Node', badge: 'R', badgeColor: '#98C379', hasDesktop: false, processes: [{ cmd: 'node', args: ['src/server.js'], cwd: 'CK\\Ripple CRM', port: 5001 }] },
    { name: 'Junk Drawer', group: 'CK', port: 5005, type: 'Python', badge: 'J', badgeColor: '#D19A66', hasDesktop: false, hasWebview: true, webviewUrl: 'http://localhost:3005', processes: [{ cmd: 'python', args: ['app.py'], cwd: 'CK\\Junk Drawer file management system\\junk-drawer-backend', port: 5005, wait: 3 }, { cmd: 'npm', args: ['start'], cwd: 'CK\\Junk Drawer file management system\\junk-drawer-app', port: 3000 }] },
    { name: 'Opp Hunter', group: 'CK', port: 5006, type: 'Python', badge: 'O', badgeColor: '#BE5046', hasDesktop: false, processes: [{ cmd: 'python', args: ['app.py'], cwd: 'CK\\Opportunity Hunter', port: 5006, wait: 3 }, { cmd: 'npm', args: ['start'], cwd: 'CK\\Opportunity Hunter\\frontend', port: 3002 }] },
    { name: 'CK Swiss Army Knife', group: 'CK', port: 5014, type: 'Node', badge: 'K', badgeColor: '#7E8590', hasDesktop: false, processes: [{ cmd: 'node', args: ['server.js'], cwd: 'CK\\CK Swiss Army Knife', port: 5014 }] },
    
    // Group 4: Intelligence
    { name: 'Identity Atlas', group: 'Intelligence', port: 5002, type: 'Node', badge: 'I', badgeColor: '#61AFEF', hasDesktop: false, processes: [{ cmd: 'node', args: ['src/server.js'], cwd: 'CK\\Identity Atlas', port: 5002 }] },
    { name: 'Digital Sentinel', group: 'Intelligence', port: 5013, type: 'Node', badge: 'D', badgeColor: '#4AA8D8', hasDesktop: false, processes: [{ cmd: 'node', args: ['server.js'], cwd: 'Digital Sentinel', port: 5013 }] },
    { name: 'Peterman', group: 'Intelligence', port: 5008, type: 'Node', badge: 'P', badgeColor: '#ABB2BF', hasDesktop: false, processes: [{ cmd: 'node', args: ['server.js'], cwd: 'Peterman', port: 5008 }] },
    
    // Group 5: Marketing
    { name: 'Spark', group: 'Marketing', port: 5011, type: 'Python', badge: 'S', badgeColor: '#E5C07B', hasDesktop: false, processes: [{ cmd: 'uvicorn', args: ['src.main:app', '--port', '5011'], cwd: 'Spark', port: 5011, shell: true }] },
    
    // Group 6: Operations
    { name: 'ProcessLens', group: 'Operations', port: 5016, type: 'Python', badge: 'P', badgeColor: '#56B6C2', hasDesktop: false, processes: [{ cmd: 'uvicorn', args: ['processlens.main:app', '--port', '5016'], cwd: 'Process Lens', port: 5016, shell: true }] },
    { name: 'Genie', group: 'Operations', port: 8000, type: 'Python', badge: 'G', badgeColor: '#98C379', hasDesktop: false, processes: [{ cmd: 'python', args: ['app.py'], cwd: 'Finance App\\Genie', port: 8000 }] },
    
    // Group 7: Infrastructure (monitored only, not auto-started)
    { name: 'Ollama', group: 'Infrastructure', port: 11434, type: 'system-service', badge: 'O', badgeColor: '#F0EDE8', hasWebview: false, healthUrl: 'http://localhost:11434/api/tags', autoStart: false },
    { name: 'PostgreSQL', group: 'Infrastructure', port: 5433, type: 'docker', badge: 'Pg', badgeColor: '#336791', hasWebview: false, containerName: 'pgvector', autoStart: false },
    { name: 'Redis', group: 'Infrastructure', port: 6379, type: 'docker', badge: 'Rs', badgeColor: '#DC382D', hasWebview: false, containerName: 'redis', autoStart: false },
    { name: 'SearXNG', group: 'Infrastructure', port: 8080, type: 'docker', badge: 'Sx', badgeColor: '#3498DB', hasWebview: true, webviewUrl: 'http://localhost:8080', containerName: 'searxng', autoStart: false },
    { name: 'n8n', group: 'Infrastructure', port: 5678, type: 'docker', badge: 'n8', badgeColor: '#FF6D5A', hasWebview: true, webviewUrl: 'http://localhost:5678', containerName: 'n8n', autoStart: false },
    { name: 'ComfyUI', group: 'Infrastructure', port: 8188, type: 'system-service', badge: 'C', badgeColor: '#7B68EE', hasWebview: true, webviewUrl: 'http://localhost:8188', healthUrl: 'http://localhost:8188', autoStart: false },
    
    // Group 8: Dev Tools (checked but not started)
    { name: 'Docker Desktop', group: 'Dev Tools', type: 'system-check', badge: 'Dk', badgeColor: '#2496ED', hasWebview: false, autoStart: false },
    { name: 'Ollama Web UI', group: 'Dev Tools', port: 3000, type: 'docker', badge: 'Ow', badgeColor: '#1A1A2E', hasWebview: true, webviewUrl: 'http://localhost:3000', containerName: 'open-webui', autoStart: false },
];

// Track running processes
const runningProcesses = new Map();
const logsDir = path.join(__dirname, 'logs');

// Ensure logs directory exists
if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
}

// Port checking
function isPortInUse(port) {
    return new Promise((resolve) => {
        const net = require('net');
        const socket = new net.Socket();
        socket.setTimeout(500);
        socket.on('connect', () => { socket.destroy(); resolve(true); });
        socket.on('timeout', () => { socket.destroy(); resolve(false); });
        socket.on('error', () => { resolve(false); });
        socket.connect(port, '127.0.0.1');
    });
}

// Health check
async function checkHealth(port, healthPath = '/api/health') {
    const http = require('http');
    return new Promise((resolve) => {
        const req = http.get(`http://127.0.0.1:${port}${healthPath}`, (res) => { resolve(res.statusCode === 200); });
        req.on('error', () => resolve(false));
        req.setTimeout(1000, () => { req.destroy(); resolve(false); });
    });
}

// Check if Docker is running
async function isDockerRunning() {
    return new Promise((resolve) => {
        const proc = spawnService('docker', ['info'], { stdio: ['pipe', 'pipe', 'pipe'] });
        let timeout = setTimeout(() => { proc.kill(); resolve(false); }, 3000);
        proc.on('close', (code) => {
            clearTimeout(timeout);
            resolve(code === 0);
        });
        proc.on('error', () => { clearTimeout(timeout); resolve(false); });
    });
}

// Get running Docker containers
async function getRunningContainers() {
    return new Promise((resolve) => {
        const proc = spawnService('docker', ['ps', '--format', '{{.Names}}'], { stdio: ['pipe', 'pipe', 'pipe'] });
        let stdout = '';
        proc.stdout.on('data', (data) => { stdout += data.toString(); });
        proc.on('close', () => {
            const containers = stdout.split('\n').filter(c => c.trim());
            resolve(new Set(containers));
        });
        proc.on('error', () => { resolve(new Set()); });
    });
}

// Check if service directory exists
function isInstalled(dir) {
    if (!dir) return false;
    return fs.existsSync(path.join(BASE_PATH, dir));
}

// Get all services with status
async function getAllServices() {
    const dockerRunning = await isDockerRunning();
    const runningContainers = dockerRunning ? await getRunningContainers() : new Set();
    
    const results = await Promise.all(SERVICES.map(async (svc) => {
        let installed = false;
        let running = false;
        let healthy = false;
        
        if (svc.type === 'docker') {
            // Docker container
            installed = true;
            running = dockerRunning && runningContainers.has(svc.containerName);
        } else if (svc.type === 'system-service' || svc.type === 'system-check') {
            // System service
            if (svc.port) {
                installed = await isPortInUse(svc.port);
                if (installed) running = true;
                if (svc.healthUrl && running) {
                    healthy = await checkHealth(svc.port, svc.healthUrl.includes('/api') ? '/api/tags' : '/');
                }
            } else {
                // System check like Docker Desktop
                installed = true;
                running = svc.name === 'Docker Desktop' ? dockerRunning : false;
            }
        } else {
            // AMTL app — use first process cwd as directory
            const appDir = svc.dir || (svc.processes && svc.processes[0] ? svc.processes[0].cwd : null);
            installed = isInstalled(appDir);
            if (installed && svc.port) {
                const portInUse = await isPortInUse(svc.port);
                if (portInUse) {
                    running = true;
                    healthy = await checkHealth(svc.port);
                }
            }
        }
        
        return {
            name: svc.name,
            group: svc.group,
            port: svc.port,
            type: svc.type,
            badge: svc.badge,
            badgeColor: svc.badgeColor,
            hasDesktop: svc.hasDesktop,
            hasWebview: svc.hasWebview,
            webviewUrl: svc.webviewUrl || `http://localhost:${svc.port}`,
            desktopDir: svc.desktopDir,
            dir: svc.dir,
            running,
            healthy,
            status: running ? (healthy ? 'healthy' : 'running') : (installed ? 'stopped' : 'not-installed'),
            autoStart: svc.autoStart !== false
        };
    }));
    
    return results;
}

// Start a service (AMTL apps only)
async function startService(name) {
    const svc = SERVICES.find(s => s.name === name);
    if (!svc) return { success: false, error: 'Service not found' };
    
    // Don't start infrastructure or dev tools
    if (svc.autoStart === false) {
        return { success: false, error: 'This service is managed externally' };
    }
    
    // Check if already running
    const portInUse = svc.port ? await isPortInUse(svc.port) : false;
    if (portInUse) {
        return { success: true, message: `${name} is already running`, alreadyRunning: true };
    }
    
    // Check if installed - use first process cwd as fallback
    const appDir = svc.dir || (svc.processes && svc.processes[0] ? svc.processes[0].cwd : null);
    const serviceDir = appDir ? path.join(BASE_PATH, appDir) : null;
    if (serviceDir && !fs.existsSync(serviceDir)) {
        return { success: false, error: `${name} is not installed (directory not found)` };
    }
    
    // Start all processes in the service
    const results = [];
    if (svc.processes) {
        for (let i = 0; i < svc.processes.length; i++) {
            const procDef = svc.processes[i];
            const logFile = path.join(logsDir, `${name.replace(/\s+/g, '_')}_${i}.log`);
            
            const options = {
                cwd: procDef.cwd ? path.join(BASE_PATH, procDef.cwd) : BASE_PATH,
                detached: true,
                stdio: ['ignore', 'pipe', 'pipe'],
                env: { ...process.env, PATH: process.env.PATH }
            };
            
            let proc;
            if (procDef.shell) {
                proc = spawnService(procDef.cmd, procDef.args, options);
            } else {
                proc = spawnService(procDef.cmd, procDef.args, options);
            }
            
            if (proc) {
                proc.unref(); // Don't keep Electron alive
                const logStream = fs.createWriteStream(logFile);
                proc.stdout.pipe(logStream);
                proc.stderr.pipe(logStream);
                
                const key = `${name}_${i}`;
                runningProcesses.set(key, { proc, logFile, startTime: Date.now() });
                results.push({ process: i, pid: proc.pid });
                
                // Wait if specified
                if (procDef.wait) {
                    await new Promise(r => setTimeout(r, procDef.wait * 1000));
                }
            }
        }
    }
    
    // Wait for port to be ready
    if (svc.port) {
        for (let i = 0; i < 10; i++) {
            await new Promise(r => setTimeout(r, 500));
            if (await isPortInUse(svc.port)) break;
        }
    }
    
    return { success: true, message: `${name} started`, processes: results };
}

// Stop a service
async function stopService(name) {
    const svc = SERVICES.find(s => s.name === name);
    if (!svc) return { success: false, error: 'Service not found' };
    
    const results = [];
    
    // Stop in reverse order (frontend first, then backend)
    if (svc.processes) {
        for (let i = svc.processes.length - 1; i >= 0; i--) {
            const key = `${name}_${i}`;
            const tracked = runningProcesses.get(key);
            
            if (tracked) {
                try {
                    if (process.platform === 'win32') {
                        spawnService('taskkill', ['/pid', tracked.proc.pid, '/f', '/t']);
                    } else {
                        tracked.proc.kill('SIGTERM');
                    }
                    runningProcesses.delete(key);
                    results.push({ process: i, stopped: true });
                } catch (error) {
                    results.push({ process: i, stopped: false, error: error.message });
                }
            }
        }
    }
    
    return { success: true, message: `${name} stopped`, results };
}

// Start all AMTL services
async function startAllServices() {
    const results = [];
    
    // Phase 1: Workshop API first
    const phase1 = SERVICES.filter(s => s.name === 'The Workshop API');
    for (const svc of phase1) {
        const result = await startService(svc.name);
        results.push({ name: svc.name, ...result });
    }
    await new Promise(r => setTimeout(r, 3000));
    
    // Phase 2: Core services
    const phase2 = SERVICES.filter(s => s.group === 'Core AMTL' && s.name !== 'The Workshop API');
    for (const svc of phase2) {
        const result = await startService(svc.name);
        results.push({ name: svc.name, ...result });
    }
    await new Promise(r => setTimeout(r, 3000));
    
    // Phase 3: All remaining AMTL apps
    const phase3 = SERVICES.filter(s => s.autoStart !== false && s.type !== 'Core AMTL' && s.name !== 'The Workshop API');
    for (const svc of phase3) {
        const result = await startService(svc.name);
        results.push({ name: svc.name, ...result });
    }
    
    return results;
}

// Stop all AMTL services
async function stopAllServices() {
    const results = [];
    for (const [key, tracked] of runningProcesses) {
        try {
            if (process.platform === 'win32') {
                spawnService('taskkill', ['/pid', tracked.proc.pid, '/f', '/t']);
            } else {
                tracked.proc.kill('SIGTERM');
            }
            results.push({ key, stopped: true });
        } catch (error) {
            results.push({ key, stopped: false, error: error.message });
        }
    }
    runningProcesses.clear();
    return results;
}

// Create window
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1500,
        height: 900,
        minWidth: 1200,
        minHeight: 700,
        titleBarStyle: 'hiddenInset',
        backgroundColor: '#0A0E14',
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js'),
            webviewTag: true
        },
        show: false
    });

    mainWindow.loadFile('renderer/index.html');

    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
    });

    mainWindow.on('close', (event) => {
        if (!app.isQuitting) {
            event.preventDefault();
            mainWindow.hide();
        }
    });

    createMenu();
    createTray();
}

// Create menu
function createMenu() {
    const template = [
        { label: APP_NAME, submenu: [
            { label: 'About', click: () => showAbout() },
            { type: 'separator' },
            { label: 'Quit', accelerator: 'CmdOrCtrl+Q', click: () => quitApp() }
        ]},
        { label: 'Services', submenu: [
            { label: 'Start All AMTL', accelerator: 'Ctrl+Shift+S', click: () => startAllServices() },
            { label: 'Stop All AMTL', accelerator: 'Ctrl+Shift+X', click: () => stopAllServices() },
            { type: 'separator' },
            { label: 'Refresh Status', accelerator: 'Ctrl+R', click: () => refreshServices() }
        ]},
        { label: 'View', submenu: [
            { label: 'Toggle Theme', accelerator: 'Ctrl+T', click: () => toggleTheme() },
            { type: 'separator' },
            { label: 'Zoom In', accelerator: 'CmdOrCtrl+Plus', click: () => mainWindow.webContents.setZoomLevel(mainWindow.webContents.getZoomLevel() + 0.5) },
            { label: 'Zoom Out', accelerator: 'CmdOrCtrl+-', click: () => mainWindow.webContents.setZoomLevel(mainWindow.webContents.getZoomLevel() - 0.5) },
            { label: 'Reset Zoom', accelerator: 'CmdOrCtrl+0', click: () => mainWindow.webContents.setZoomLevel(0) }
        ]},
        { label: 'Help', submenu: [
            { label: 'Open Workshop API', click: () => mainWindow.webContents.executeJavaScript('window.open("http://localhost:5003", "_blank")') },
            { type: 'separator' },
            { label: 'About', click: () => showAbout() }
        ]}
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

// Create tray
function createTray() {
    const iconPath = path.join(__dirname, 'icon.svg');
    const icon = nativeImage.createFromPath(iconPath);
    tray = new Tray(icon);
    tray.setToolTip(APP_NAME);

    tray.setContextMenu(Menu.buildFromTemplate([
        { label: 'Show', click: () => mainWindow.show() },
        { type: 'separator' },
        { label: 'Start All AMTL', click: () => startAllServices() },
        { label: 'Stop All AMTL', click: () => stopAllServices() },
        { type: 'separator' },
        { label: 'Quit', click: () => quitApp() }
    ]));

    tray.on('click', () => {
        if (mainWindow.isVisible()) mainWindow.hide();
        else mainWindow.show();
    });
}

function showAbout() {
    mainWindow.webContents.executeJavaScript(`alert('${APP_NAME} v${APP_VERSION}\\n\\nAuthor: Mani Padisetti\\nAlmost Magic Tech Lab\\n\\nYour launchpad. Every tool. One click.');`);
}

function quitApp() {
    app.isQuitting = true;
    stopAllServices();
    app.quit();
}

function toggleTheme() {
    mainWindow.webContents.executeJavaScript('window.toggleTheme()');
}

function refreshServices() {
    return getAllServices();
}

// IPC Handlers
ipcMain.handle('services:get-all', async () => {
    return { services: await getAllServices(), groups: GROUPS };
});

ipcMain.handle('services:start', async (event, name) => {
    return await startService(name);
});

ipcMain.handle('services:stop', async (event, name) => {
    return await stopService(name);
});

ipcMain.handle('services:start-all', async () => {
    return await startAllServices();
});

ipcMain.handle('services:stop-all', async () => {
    return await stopAllServices();
});

ipcMain.handle('services:refresh', async () => {
    return await getAllServices();
});

ipcMain.handle('app:open-webview', async (event, url, name) => {
    const safeName = (name || 'App').replace(/'/g, "\\'");
    const safeUrl = (url || '').replace(/'/g, "\\'");
    mainWindow.webContents.executeJavaScript(
        `window.openAppTab('${safeUrl}', '${safeName}')`
    );
    return { success: true };
});

ipcMain.handle('app:open-desktop', async (event, name) => {
    const svc = SERVICES.find(s => s.name === name);
    if (svc && svc.port) {
        const url = svc.webviewUrl || `http://localhost:${svc.port}`;
        const safeName = (name || 'App').replace(/'/g, "\\'");
        mainWindow.webContents.executeJavaScript(
            `window.openAppTab('${url}', '${safeName}')`
        );
    }
    return { success: true };
});

ipcMain.handle('app:toggle-theme', async () => {
    toggleTheme();
    return { success: true };
});

app.whenReady().then(() => {
    createWindow();

    setInterval(async () => {
        if (mainWindow && !mainWindow.isDestroyed()) {
            try {
                const services = await getAllServices();
                mainWindow.webContents.send('services:updated', { services });
            } catch (e) {}
        }
    }, 30000);
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

app.on('before-quit', () => {
    app.isQuitting = true;
    stopAllServices();
});
