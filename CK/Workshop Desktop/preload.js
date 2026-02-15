/**
 * The Workshop Desktop — Preload Script
 * Author: Mani Padisetti
 * Almost Magic Tech Lab
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('workshop', {
    // Service management
    getServices: () => ipcRenderer.invoke('services:get-all'),
    startService: (name) => ipcRenderer.invoke('services:start', name),
    stopService: (name) => ipcRenderer.invoke('services:stop', name),
    startAll: () => ipcRenderer.invoke('services:start-all'),
    stopAll: () => ipcRenderer.invoke('services:stop-all'),
    refresh: () => ipcRenderer.invoke('services:refresh'),
    
    // App control
    openApp: (url, name) => ipcRenderer.invoke('app:open-webview', url, name),
    openDesktop: (name) => ipcRenderer.invoke('app:open-desktop', name),
    
    // Theme
    toggleTheme: () => ipcRenderer.invoke('app:toggle-theme'),
    
    // Events
    onServiceUpdate: (callback) => {
        ipcRenderer.on('services:updated', (event, data) => callback(data));
    },
    
    // Platform info
    platform: process.platform,
    isElectron: true
});
