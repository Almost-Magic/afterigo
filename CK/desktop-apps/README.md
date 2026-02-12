# AMTL Desktop Apps

Electron desktop wrappers for all CK tools. Each app loads its web backend in a native window with system tray support, health checking, and window state persistence.

## Quick Start

```bash
# Install dependencies (once)
npm install

# Launch a single app
npm run start:elaine
npm run start:workshop
npm run start:ripple

# Launch core apps (Elaine + Workshop + Ripple)
launch-all.bat

# Launch ALL 12 apps
launch-all.bat --all
```

## Apps

| App | Port | Command |
|-----|------|---------|
| Elaine | 5000 | `npm run start:elaine` |
| The Workshop | 5003 | `npm run start:workshop` |
| Ripple CRM | 3100 | `npm run start:ripple` |
| Touchstone | 3200 | `npm run start:touchstone` |
| CK Writer | 5004 | `npm run start:writer` |
| Learning Assistant | 5002 | `npm run start:learning` |
| Peterman | 5008 | `npm run start:peterman` |
| Genie | 3000 | `npm run start:genie` |
| Costanza | 5001 | `npm run start:costanza` |
| Author Studio | 5007 | `npm run start:author-studio` |
| Junk Drawer | 3005 | `npm run start:junk-drawer` |
| Supervisor | 9000 | `npm run start:supervisor` |

## Features

- **System tray**: Minimise to tray, double-click to restore, right-click for menu
- **Health check**: Shows a "Starting up..." splash if the backend isn't running yet
- **Auto-retry**: Polls the backend every 3 seconds for up to 6 minutes
- **Window state**: Remembers position and size between sessions
- **No bundler**: Each app is a thin Electron shell around the web UI

## Architecture

```
desktop-apps/
  shared/
    main.js        -- Shared Electron main process (reads config.json)
    preload.js     -- Secure IPC bridge
  apps/
    elaine/        -- config.json + package.json
    workshop/      -- config.json + package.json
    ...            -- One folder per app
  icons/           -- SVG icons (one per app)
  generate-apps.js -- Regenerate all configs from registry
  build-all.bat    -- Build standalone .exe files
  launch-all.bat   -- Start backends + open Electron apps
```

## Building Standalone .exe

```bash
build-all.bat
```

This installs electron-builder, builds all 12 apps as portable .exe files in `dist/`, and creates Desktop shortcuts.

## Adding a New App

1. Add an entry to the `apps` array in `generate-apps.js`
2. Run `node generate-apps.js`
3. Add an npm script to the root `package.json`
4. Test with `npm run start:<appname>`

## Design System

All apps use the AMTL design system:
- Background: #0a0e1a (Midnight)
- Accent: Per-app (gold, blue, green, etc.)
- Font: Segoe UI (system), Sora (web)
- Splash screen matches the app's accent colour

---

*Almost Magic Tech Lab -- Where Almost Magic Meets Real Results*
