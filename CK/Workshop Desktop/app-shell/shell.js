/**
 * AMTL App Shell — Shared Electron Wrapper for AMTL Apps
 * Author: Mani Padisetti
 * Almost Magic Tech Lab
 * 
 * Usage: node shell.js --port 5000 --title "App Name" --cwd "Path\\To\\App" --cmd "start command"
 */

const { app, BrowserWindow, ipcMain, Menu, Tray, nativeImage } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const net = require('net');

// Parse command line args
const args = process.argv.slice(2);
const config = {
    port: 5000,
    title: 'AMTL App',
    cwd: process.cwd(),
    cmd: null,
    icon: path.join(__dirname, 'default.svg')
};

for (let i = 0; i < args.length; i++) {
    if (args[i] === '--port' && i + 1 < args.length) config.port = parseInt(args[i + 1]);
    if (args[i] === '--title' && i + 1 < args.length) config.title = args[i + 1];
    if (args[i] === '--cwd' && i + 1 < args.length) config.cwd = args[i + 1];
    if (args[i] === '--cmd' && i + 1 < args.length) config.cmd = args[i + 1];
    if (args[i] === '--icon' && i + 1 < args.length) config.icon = args[i + 1];
}

// Constants
const APP_NAME = config.title;
const BASE_PATH = 'C:\\Users\\ManiPadisetti\\Dropbox\\Desktop DB\\Books and Articles Mani\\Books\\Almost Magic Tech Lab AMTL\\Source and Brand';

// Global references
let mainWindow = null;
let tray = null;
let serverProcess = null;
let loadingInterval = null;

// Check if port is in use
function isPortInUse(port) {
    return new Promise((resolve) => {
        const socket = new net.Socket();
        socket.setTimeout(500);
        socket.on('connect', () => { socket.destroy(); resolve(true); });
        socket.on('timeout', () => { socket.destroy(); resolve(false); });
        socket.on('error', () => { resolve(false); });
        socket.connect(port, '127.0.0.1');
    });
}

// Start the backend server
function startServer() {
    return new Promise((resolve) => {
        console.log(`[${APP_NAME}] Starting server on port ${config.port}...`);
        
        // Parse the command - handle shell commands with args
        let cmd, cmdArgs;
        
        if (config.cmd) {
            // Handle commands like "python app.py" or ".venv/bin/uvicorn main:app"
            const cmdParts = config.cmd.split(' ');
            cmd = cmdParts[0];
            cmdParts.shift(); // Remove command
            cmdArgs = cmdParts;
        } else {
            cmd = 'python';
            cmdArgs = ['app.py'];
        }
        
        const options = {
            cwd: config.cwd.startsWith(BASE_PATH) ? config.cwd : path.join(BASE_PATH, config.cwd),
            detached: true,
            stdio: ['ignore', 'pipe', 'pipe'],
            windowsHide: true,
            env: { ...process.env }
        };
        
        serverProcess = spawn(cmd, cmdArgs, options);
        
        serverProcess.stdout.on('data', (data) => {
            console.log(`[${APP_NAME}] ${data.toString().trim()}`);
        });
        
        serverProcess.stderr.on('data', (data) => {
            console.error(`[${APP_NAME}] ${data.toString().trim()}`);
        });
        
        serverProcess.unref();
        
        // Wait for port to be ready
        let attempts = 0;
        const maxAttempts = 60; // 30 seconds max
        
        loadingInterval = setInterval(async () => {
            attempts++;
            if (await isPortInUse(config.port)) {
                clearInterval(loadingInterval);
                console.log(`[${APP_NAME}] Server ready on port ${config.port}`);
                resolve(true);
            } else if (attempts >= maxAttempts) {
                clearInterval(loadingInterval);
                console.error(`[${APP_NAME}] Server failed to start`);
                resolve(false);
            }
        }, 500);
    });
}

// Create the main window
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1000,
        minHeight: 700,
        title: APP_NAME,
        titleBarStyle: 'hiddenInset',
        backgroundColor: '#0A0E14',
        icon: config.icon,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        show: false
    });

    // Loading screen
    mainWindow.loadFile('loading.html');
    mainWindow.show();

    // Start server if not running
    startServer().then((success) => {
        if (success) {
            // Load the actual app
            mainWindow.loadURL(`http://localhost:${config.port}`);
        } else {
            mainWindow.loadFile('error.html');
        }
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
        { label: 'View', submenu: [
            { label: 'Reload', accelerator: 'CmdOrCtrl+R', click: () => mainWindow.reload() },
            { label: 'Toggle DevTools', accelerator: 'F12', click: () => mainWindow.webContents.toggleDevTools() },
            { type: 'separator' },
            { label: 'Zoom In', accelerator: 'CmdOrCtrl+Plus', click: () => mainWindow.webContents.setZoomLevel(mainWindow.webContents.getZoomLevel() + 0.5) },
            { label: 'Zoom Out', accelerator: 'CmdOrCtrl+-', click: () => mainWindow.webContents.setZoomLevel(mainWindow.webContents.getZoomLevel() - 0.5) },
            { label: 'Reset Zoom', accelerator: 'CmdOrCtrl+0', click: () => mainWindow.webContents.setZoomLevel(0) }
        ]}
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

// Create tray
// Create tray with fallback icons
function createTray() {
    const iconPath = config.icon;
    const icon = nativeImage.createFromPath(iconPath);
    
    let trayIcon = icon;
    if (trayIcon.isEmpty()) {
        // Try default icon
        const defaultIcon = nativeImage.createFromPath(path.join(__dirname, 'default.svg'));
        if (!defaultIcon.isEmpty()) {
            trayIcon = defaultIcon;
        } else {
            // Create a simple fallback icon
            trayIcon = nativeImage.createFromDataURL('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNiAxNiI+PHJlY3Qgd2lkdGg9IjE2IiBoZWlnaHQ9IjE2IiByeD0iMiIgZmlsbD0iIzY0NjQ2NCIvPjx0ZXh0IHg9IjgiIHk9IjEyIiBmb250LWZhbWlseT0ic2Fucy1zZXJpZiIgZm9udC1zaXplPSIxMCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiPkQ8L3RleHQ+PC9zdmc+');
        }
    }
    
    try {
        tray = new Tray(trayIcon.resize({ width: 16, height: 16 }));
        tray.setToolTip(APP_NAME);
        tray.setContextMenu(Menu.buildFromTemplate([
            { label: 'Show', click: () => mainWindow.show() },
            { type: 'separator' },
            { label: 'Quit', click: () => quitApp() }
        ]));
        
        tray.on('click', () => {
            if (mainWindow.isVisible()) mainWindow.hide();
            else mainWindow.show();
        });
    } catch (e) {
        console.log(`[${APP_NAME}] Tray not available - skipping tray icon`);
    }
}

function showAbout() {
    mainWindow.webContents.executeJavaScript(`alert('${APP_NAME}\\n\\nAMTL App Shell\\nAlmost Magic Tech Lab');`);
}

function quitApp() {
    app.isQuitting = true;
    
    // Kill server process
    if (serverProcess) {
        try {
            if (process.platform === 'win32') {
                spawn('taskkill', ['/pid', serverProcess.pid, '/f', '/t']);
            } else {
                serverProcess.kill('SIGTERM');
            }
        } catch (e) {}
    }
    
    app.quit();
}

// IPC handlers
ipcMain.handle('app:reload', () => {
    mainWindow.reload();
    return { success: true };
});

ipcMain.handle('app:get-port', () => {
    return { port: config.port };
});

// App events
app.whenReady().then(() => {
    createWindow();
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
    if (serverProcess) {
        try {
            if (process.platform === 'win32') {
                spawn('taskkill', ['/pid', serverProcess.pid, '/f', '/t']);
            } else {
                serverProcess.kill('SIGTERM');
            }
        } catch (e) {}
    }
});

console.log(`[${APP_NAME}] App Shell starting on port ${config.port}`);
