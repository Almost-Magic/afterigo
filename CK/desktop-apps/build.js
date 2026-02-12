/**
 * AMTL Desktop Apps — Build Script
 * Creates standalone .exe for each CK desktop app via electron-builder.
 *
 * Builds from the root desktop-apps/ dir using per-app config files.
 * No staging directories needed — avoids Dropbox symlink issues.
 *
 * Usage: node build.js [appId]   (omit appId to build all)
 * Output: dist/<appId>/
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const DIST = path.join(ROOT, 'dist');
const APPS_DIR = path.join(ROOT, 'apps');

// Get list of apps to build
const targetApp = process.argv[2];
const appIds = targetApp
    ? [targetApp]
    : fs.readdirSync(APPS_DIR).filter(d =>
          fs.statSync(path.join(APPS_DIR, d)).isDirectory() &&
          fs.existsSync(path.join(APPS_DIR, d, 'config.json'))
      );

console.log(`\n  AMTL Desktop Apps — Build`);
console.log(`  ${appIds.length} apps to build`);
console.log(`  Output: ${DIST}\n`);

const results = { success: [], failed: [] };

for (let i = 0; i < appIds.length; i++) {
    const appId = appIds[i];
    const configFile = path.join(APPS_DIR, appId, 'config.json');

    if (!fs.existsSync(configFile)) {
        console.log(`  [${i + 1}/${appIds.length}] SKIP ${appId} — no config.json`);
        continue;
    }

    const appConfig = JSON.parse(fs.readFileSync(configFile, 'utf-8'));
    console.log(`  [${i + 1}/${appIds.length}] Building ${appConfig.name} (${appId})...`);

    const outputDir = path.join(DIST, appId);

    // Find icon for this app
    const iconPath = path.join(ROOT, 'build', 'icons', `${appId}.png`);
    const defaultIcon = path.join(ROOT, 'build', 'icon.png');
    const winIcon = fs.existsSync(iconPath) ? iconPath : (fs.existsSync(defaultIcon) ? defaultIcon : undefined);

    // Write temporary electron-builder config for this app
    const buildConfig = {
        appId: `tech.almostmagic.${appId.replace(/-/g, '')}`,
        productName: appConfig.name,
        extends: null,
        files: [
            'shared/**/*',
            { from: `apps/${appId}`, to: '.', filter: ['config.json'] }
        ],
        extraMetadata: {
            main: 'shared/main.js'
        },
        directories: {
            output: `dist/${appId}`,
            buildResources: 'build'
        },
        win: {
            target: 'dir',
            icon: winIcon || undefined,
        },
        // dir target produces win-unpacked/<ProductName>.exe
    };

    const tempConfigPath = path.join(ROOT, `_build-config-${appId}.json`);
    fs.writeFileSync(tempConfigPath, JSON.stringify(buildConfig, null, 2));

    try {
        execSync(`npx electron-builder build --win --config "${tempConfigPath}"`, {
            cwd: ROOT,
            stdio: 'pipe',
            env: {
                ...process.env,
                CSC_IDENTITY_AUTO_DISCOVERY: 'false',
            },
            timeout: 600000  // 10 minutes per app
        });

        // Verify output (dir target produces win-unpacked/<Name>.exe)
        const unpackedDir = path.join(outputDir, 'win-unpacked');
        if (fs.existsSync(unpackedDir)) {
            const exeFiles = fs.readdirSync(unpackedDir).filter(f => f.endsWith('.exe'));
            if (exeFiles.length > 0) {
                const size = (fs.statSync(path.join(unpackedDir, exeFiles[0])).size / 1024 / 1024).toFixed(1);
                console.log(`    OK — win-unpacked/${exeFiles[0]} (${size} MB)`);
                results.success.push(appId);
            } else {
                console.log(`    WARN — built but no .exe found in win-unpacked`);
                results.failed.push(appId);
            }
        } else {
            console.log(`    WARN — output dir not created`);
            results.failed.push(appId);
        }
    } catch (e) {
        const stderr = e.stderr ? e.stderr.toString() : '';
        const stdout = e.stdout ? e.stdout.toString() : '';
        const combined = (stderr + '\n' + stdout).trim();
        const lastLines = combined.split('\n').filter(l => l.trim()).slice(-8).join('\n');
        console.log(`    FAIL —\n${lastLines}`);
        results.failed.push(appId);
    } finally {
        // Remove temp config
        try { fs.unlinkSync(tempConfigPath); } catch (e) { /* ignore */ }
    }
}

console.log(`\n  ========================================`);
console.log(`  Build complete: ${results.success.length} OK, ${results.failed.length} failed`);
if (results.failed.length > 0) {
    console.log(`  Failed: ${results.failed.join(', ')}`);
}
if (results.success.length > 0) {
    console.log(`  Success: ${results.success.join(', ')}`);
}
console.log(`  Output: ${DIST}`);
console.log(`  ========================================\n`);
