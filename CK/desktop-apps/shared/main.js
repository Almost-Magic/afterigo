/**
 * AMTL Desktop App — Shared Electron Main Process
 *
 * Usage: Each app folder has a config.json that customises this template.
 * Run with: electron . --config=../apps/<appname>/config.json
 *
 * Features:
 *   - Loads the app's localhost URL in a native window
 *   - System tray with show/hide toggle
 *   - Window state persistence (position, size)
 *   - Health check with "Starting up..." splash screen
 *   - Auto-retry when backend is not yet running
 */

const { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain, Notification } = require('electron');
const path = require('path');
const fs = require('fs');
const http = require('http');

// ---------------------------------------------------------------------------
// Load app config
// ---------------------------------------------------------------------------
const configArg = process.argv.find(a => a.startsWith('--config='));
const configPath = configArg
    ? path.resolve(configArg.replace('--config=', ''))
    : path.join(__dirname, '..', 'apps', 'elaine', 'config.json');

const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));

const APP_NAME   = config.name;
const APP_URL    = config.url;
const HEALTH_URL = config.healthUrl || `${config.url}/api/health`;
const APP_PORT   = config.port;
const ACCENT     = config.accent || '#c9a84c';
const LETTER     = config.letter || APP_NAME[0].toUpperCase();

// ---------------------------------------------------------------------------
// Window state persistence
// ---------------------------------------------------------------------------
const STATE_FILE = path.join(app.getPath('userData'), `${config.id}-window-state.json`);

function loadWindowState() {
    try {
        return JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
    } catch {
        return { width: 1280, height: 800 };
    }
}

function saveWindowState(win) {
    if (!win || win.isDestroyed()) return;
    const bounds = win.getBounds();
    const maximised = win.isMaximized();
    fs.writeFileSync(STATE_FILE, JSON.stringify({ ...bounds, maximised }));
}

// ---------------------------------------------------------------------------
// Health check
// ---------------------------------------------------------------------------
function checkHealth(url, timeout = 3000) {
    return new Promise(resolve => {
        const req = http.get(url, { timeout }, res => {
            resolve(res.statusCode >= 200 && res.statusCode < 400);
            res.resume();
        });
        req.on('error', () => resolve(false));
        req.on('timeout', () => { req.destroy(); resolve(false); });
    });
}

// ---------------------------------------------------------------------------
// SVG icon generation
// ---------------------------------------------------------------------------
function generateIcon(letter, bgColour, fgColour, size) {
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
        <rect width="${size}" height="${size}" rx="${Math.round(size * 0.2)}" fill="${bgColour}"/>
        <text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle"
              font-family="Segoe UI, sans-serif" font-weight="700"
              font-size="${Math.round(size * 0.5)}" fill="${fgColour}">${letter}</text>
    </svg>`;
    return nativeImage.createFromBuffer(Buffer.from(svg));
}

// ---------------------------------------------------------------------------
// App lifecycle
// ---------------------------------------------------------------------------
let mainWindow = null;
let tray = null;
let isQuitting = false;

function createSplashHTML() {
    return `<!DOCTYPE html>
<html><head><style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        background: #0a0e1a;
        color: #e8e2d6;
        font-family: 'Segoe UI', sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
    }
    .icon {
        width: 80px; height: 80px;
        background: ${ACCENT};
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px;
        font-weight: 700;
        color: #0a0e1a;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px ${ACCENT}44;
    }
    h1 { font-size: 24px; font-weight: 600; margin-bottom: 8px; }
    .subtitle { color: #9ca3af; font-size: 14px; margin-bottom: 32px; }
    .spinner {
        width: 40px; height: 40px;
        border: 3px solid #1a2035;
        border-top-color: ${ACCENT};
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .status { color: #9ca3af; font-size: 13px; margin-top: 16px; }
    .retry { color: #6b7280; font-size: 12px; margin-top: 8px; }
</style></head><body>
    <div class="icon">${LETTER}</div>
    <h1>${APP_NAME}</h1>
    <div class="subtitle">Almost Magic Tech Lab</div>
    <div class="spinner"></div>
    <div class="status">Waiting for backend on port ${APP_PORT}...</div>
    <div class="retry">Auto-retrying every 3 seconds</div>
</body></html>`;
}

async function createWindow() {
    const state = loadWindowState();

    mainWindow = new BrowserWindow({
        width: state.width || 1280,
        height: state.height || 800,
        x: state.x,
        y: state.y,
        minWidth: 800,
        minHeight: 600,
        title: APP_NAME,
        icon: generateIcon(LETTER, ACCENT, '#0a0e1a', 256),
        backgroundColor: '#0a0e1a',
        show: false,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js'),
        },
    });

    if (state.maximised) mainWindow.maximize();

    // Save state on resize/move
    mainWindow.on('resize', () => saveWindowState(mainWindow));
    mainWindow.on('move', () => saveWindowState(mainWindow));

    // Minimise to tray on close
    mainWindow.on('close', event => {
        if (!isQuitting) {
            event.preventDefault();
            mainWindow.hide();
        }
    });

    mainWindow.once('ready-to-show', () => mainWindow.show());

    // Health check loop
    const healthy = await checkHealth(HEALTH_URL);
    if (healthy) {
        mainWindow.loadURL(APP_URL);
    } else {
        mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(createSplashHTML())}`);
        waitForBackend();
    }
}

async function waitForBackend() {
    const maxRetries = 120; // 6 minutes
    for (let i = 0; i < maxRetries; i++) {
        await new Promise(r => setTimeout(r, 3000));
        const healthy = await checkHealth(HEALTH_URL);
        if (healthy) {
            if (mainWindow && !mainWindow.isDestroyed()) {
                mainWindow.loadURL(APP_URL);
            }
            return;
        }
    }
    // After 6 minutes, show error
    if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(`<!DOCTYPE html>
<html><head><style>
    body { background: #0a0e1a; color: #f87171; font-family: 'Segoe UI', sans-serif;
           display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }
    h1 { margin-bottom: 12px; }
    p { color: #9ca3af; }
</style></head><body>
    <h1>Could not connect to ${APP_NAME}</h1>
    <p>Backend on port ${APP_PORT} did not respond after 6 minutes.</p>
    <p>Check that the service is running, then restart this app.</p>
</body></html>`)}`);
    }
}

function createTray() {
    const icon = generateIcon(LETTER, ACCENT, '#0a0e1a', 16);
    tray = new Tray(icon);
    tray.setToolTip(`${APP_NAME} — AMTL`);

    const contextMenu = Menu.buildFromTemplate([
        { label: `Open ${APP_NAME}`, click: () => { mainWindow.show(); mainWindow.focus(); } },
        { type: 'separator' },
        { label: 'Reload', click: () => { if (mainWindow) mainWindow.reload(); } },
        { label: 'Health Check', click: async () => {
            const ok = await checkHealth(HEALTH_URL);
            new Notification({
                title: APP_NAME,
                body: ok ? 'Backend is healthy' : 'Backend is not responding',
            }).show();
        }},
        { type: 'separator' },
        { label: `Quit ${APP_NAME}`, click: () => { isQuitting = true; app.quit(); } },
    ]);

    tray.setContextMenu(contextMenu);
    tray.on('double-click', () => { mainWindow.show(); mainWindow.focus(); });
}

// ---------------------------------------------------------------------------
// IPC handlers
// ---------------------------------------------------------------------------
ipcMain.handle('show-notification', (_event, title, body) => {
    new Notification({ title, body }).show();
});

// ---------------------------------------------------------------------------
// App events
// ---------------------------------------------------------------------------
app.whenReady().then(() => {
    createTray();
    createWindow();
});

app.on('before-quit', () => { isQuitting = true; });

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
    if (mainWindow === null) createWindow();
    else mainWindow.show();
});
