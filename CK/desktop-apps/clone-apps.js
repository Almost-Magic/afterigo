/**
 * Clone the built Elaine app for all other desktop apps.
 * Since all apps use the same shared/main.js + preload.js,
 * only the config.json differs. This is much faster than
 * building each app separately with electron-builder.
 *
 * Usage: node clone-apps.js
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = __dirname;
const DIST = path.join(ROOT, 'dist');
const APPS_DIR = path.join(ROOT, 'apps');

// Source: the already-built elaine app
const SOURCE_DIR = path.join(DIST, 'elaine', 'win-unpacked');
const SOURCE_EXE = 'Elaine.exe';

if (!fs.existsSync(path.join(SOURCE_DIR, SOURCE_EXE))) {
    console.error('ERROR: Elaine.exe not found. Build elaine first.');
    process.exit(1);
}

// Get all app IDs except elaine
const appIds = fs.readdirSync(APPS_DIR).filter(d =>
    d !== 'elaine' &&
    fs.statSync(path.join(APPS_DIR, d)).isDirectory() &&
    fs.existsSync(path.join(APPS_DIR, d, 'config.json'))
);

console.log(`\n  Cloning Elaine build for ${appIds.length} other apps...\n`);

// Find rcedit for renaming the .exe product name
let rcedit = null;
const cacheDir = path.join(process.env.LOCALAPPDATA, 'electron-builder', 'Cache', 'winCodeSign');
if (fs.existsSync(cacheDir)) {
    const dirs = fs.readdirSync(cacheDir).filter(d =>
        fs.statSync(path.join(cacheDir, d)).isDirectory()
    );
    for (const d of dirs) {
        const r = path.join(cacheDir, d, 'rcedit-x64.exe');
        if (fs.existsSync(r)) { rcedit = r; break; }
    }
}

let count = 0;
for (const appId of appIds) {
    count++;
    const config = JSON.parse(fs.readFileSync(path.join(APPS_DIR, appId, 'config.json'), 'utf-8'));
    const targetDir = path.join(DIST, appId, 'win-unpacked');
    const targetExe = `${config.name}.exe`;

    console.log(`  [${count}/${appIds.length}] ${config.name} (${appId})...`);

    // Clean target
    fs.rmSync(path.join(DIST, appId), { recursive: true, force: true });
    fs.mkdirSync(targetDir, { recursive: true });

    // Copy all files from source (robocopy for speed, fallback to recursive copy)
    try {
        execSync(`robocopy "${SOURCE_DIR}" "${targetDir}" /E /NFL /NDL /NJH /NJS /NC /NS /NP`, {
            stdio: 'pipe',
            timeout: 60000
        });
    } catch (e) {
        // robocopy returns non-zero even on success (1 = files copied)
        if (e.status > 7) {
            console.log(`    WARN: robocopy returned ${e.status}`);
        }
    }

    // Rename the exe
    const sourceExePath = path.join(targetDir, SOURCE_EXE);
    const targetExePath = path.join(targetDir, targetExe);
    if (fs.existsSync(sourceExePath) && sourceExePath !== targetExePath) {
        fs.renameSync(sourceExePath, targetExePath);
    }

    // Replace config.json in the app.asar resources
    // The config is loaded by main.js at runtime from the asar
    // For now, copy config.json next to the exe as a fallback
    fs.copyFileSync(
        path.join(APPS_DIR, appId, 'config.json'),
        path.join(targetDir, 'config.json')
    );

    // Also update the config inside the resources/app directory if it exists (unpacked asar)
    const resourcesApp = path.join(targetDir, 'resources', 'app');
    if (fs.existsSync(resourcesApp)) {
        fs.copyFileSync(
            path.join(APPS_DIR, appId, 'config.json'),
            path.join(resourcesApp, 'config.json')
        );
    }

    // If asar exists, we need to extract, replace config, repack
    const asarPath = path.join(targetDir, 'resources', 'app.asar');
    if (fs.existsSync(asarPath)) {
        try {
            // Extract asar
            const extractDir = path.join(targetDir, 'resources', '_app_temp');
            execSync(`npx asar extract "${asarPath}" "${extractDir}"`, {
                cwd: ROOT, stdio: 'pipe', timeout: 30000
            });
            // Replace config.json
            fs.copyFileSync(
                path.join(APPS_DIR, appId, 'config.json'),
                path.join(extractDir, 'config.json')
            );
            // Repack asar
            fs.unlinkSync(asarPath);
            execSync(`npx asar pack "${extractDir}" "${asarPath}"`, {
                cwd: ROOT, stdio: 'pipe', timeout: 30000
            });
            // Cleanup
            fs.rmSync(extractDir, { recursive: true, force: true });
            console.log(`    OK (asar updated)`);
        } catch (e) {
            console.log(`    OK (asar update failed: ${e.message.split('\n')[0]}, using exe-level config)`);
        }
    } else {
        console.log(`    OK (no asar)`);
    }

    // Update exe product name and description using rcedit
    if (rcedit) {
        try {
            execSync(`"${rcedit}" "${targetExePath}" --set-product-version "1.0.0" --set-file-description "${config.name} — AMTL" --set-version-string "ProductName" "${config.name}"`, {
                stdio: 'pipe', timeout: 10000
            });
        } catch (e) {
            // rcedit errors are non-critical
        }
    }
}

console.log(`\n  Done. ${count} apps cloned from Elaine build.`);
console.log(`  Output: ${DIST}\n`);
