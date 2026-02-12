/**
 * AMTL Desktop App — Shared Preload Script
 * Provides secure IPC bridge to renderer.
 */
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('amtl', {
    notify: (title, body) => ipcRenderer.invoke('show-notification', title, body),
});
