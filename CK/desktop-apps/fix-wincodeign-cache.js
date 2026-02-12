// Fix winCodeSign cache symlink issue on Windows
const fs = require('fs');
const path = require('path');

const cacheDir = path.join(process.env.LOCALAPPDATA, 'electron-builder', 'Cache', 'winCodeSign');
if (!fs.existsSync(cacheDir)) { console.log('No cache dir found'); process.exit(0); }

const dirs = fs.readdirSync(cacheDir).filter(d =>
    fs.statSync(path.join(cacheDir, d)).isDirectory()
);

let fixed = 0;
for (const dir of dirs) {
    const darwinLib = path.join(cacheDir, dir, 'darwin', '10.12', 'lib');
    if (!fs.existsSync(darwinLib)) continue;

    const source1 = path.join(darwinLib, 'libcrypto.1.0.0.dylib');
    const target1 = path.join(darwinLib, 'libcrypto.dylib');
    const source2 = path.join(darwinLib, 'libssl.1.0.0.dylib');
    const target2 = path.join(darwinLib, 'libssl.dylib');

    if (fs.existsSync(source1) && !fs.existsSync(target1)) {
        fs.copyFileSync(source1, target1);
        fs.copyFileSync(source2, target2);
        console.log(`Fixed: ${dir}`);
        fixed++;
    }
}

console.log(`Done. Fixed ${fixed} directories.`);
