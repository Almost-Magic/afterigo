/**
 * Generate PNG icons for electron-builder from app configs.
 * Creates 256x256 PNG icons in build/icons/ directory.
 * Uses raw PNG encoding — no native dependencies needed.
 */

const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

const APPS_DIR = path.join(__dirname, 'apps');
const BUILD_DIR = path.join(__dirname, 'build');
const ICONS_DIR = path.join(BUILD_DIR, 'icons');

// Ensure output directory exists
fs.mkdirSync(ICONS_DIR, { recursive: true });

// Parse hex colour to RGB
function hexToRGB(hex) {
    hex = hex.replace('#', '');
    return {
        r: parseInt(hex.substring(0, 2), 16),
        g: parseInt(hex.substring(2, 4), 16),
        b: parseInt(hex.substring(4, 6), 16)
    };
}

// Create a minimal valid 256x256 PNG with a solid background colour
function createPNG(width, height, bgR, bgG, bgB) {
    // PNG consists of: signature + IHDR + IDAT + IEND

    // 1. PNG signature
    const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

    // 2. IHDR chunk (image header)
    const ihdrData = Buffer.alloc(13);
    ihdrData.writeUInt32BE(width, 0);    // width
    ihdrData.writeUInt32BE(height, 4);   // height
    ihdrData.writeUInt8(8, 8);           // bit depth
    ihdrData.writeUInt8(2, 9);           // colour type (RGB)
    ihdrData.writeUInt8(0, 10);          // compression method
    ihdrData.writeUInt8(0, 11);          // filter method
    ihdrData.writeUInt8(0, 12);          // interlace method
    const ihdr = createChunk('IHDR', ihdrData);

    // 3. IDAT chunk (image data)
    // Each row: filter byte (0 = None) + RGB * width
    const rowSize = 1 + width * 3;
    const rawData = Buffer.alloc(rowSize * height);

    for (let y = 0; y < height; y++) {
        const offset = y * rowSize;
        rawData[offset] = 0; // filter: None
        for (let x = 0; x < width; x++) {
            const px = offset + 1 + x * 3;
            // Create a rounded rectangle effect with darker edges
            const cx = width / 2, cy = height / 2;
            const dx = Math.abs(x - cx) / cx;
            const dy = Math.abs(y - cy) / cy;
            const cornerRadius = 0.18;
            const edgeDist = Math.max(dx, dy);

            if (edgeDist > 1 - cornerRadius) {
                // Corner rounding — darker or transparent effect
                const cornerDx = Math.max(0, dx - (1 - cornerRadius)) / cornerRadius;
                const cornerDy = Math.max(0, dy - (1 - cornerRadius)) / cornerRadius;
                const dist = Math.sqrt(cornerDx * cornerDx + cornerDy * cornerDy);
                if (dist > 1.0) {
                    // Outside rounded corner — use dark background
                    rawData[px] = 10;
                    rawData[px + 1] = 14;
                    rawData[px + 2] = 26;
                    continue;
                }
            }

            rawData[px] = bgR;
            rawData[px + 1] = bgG;
            rawData[px + 2] = bgB;
        }
    }

    const compressed = zlib.deflateSync(rawData);
    const idat = createChunk('IDAT', compressed);

    // 4. IEND chunk
    const iend = createChunk('IEND', Buffer.alloc(0));

    return Buffer.concat([signature, ihdr, idat, iend]);
}

function createChunk(type, data) {
    const length = Buffer.alloc(4);
    length.writeUInt32BE(data.length, 0);

    const typeBuffer = Buffer.from(type, 'ascii');
    const crcData = Buffer.concat([typeBuffer, data]);

    const crc = Buffer.alloc(4);
    crc.writeUInt32BE(crc32(crcData), 0);

    return Buffer.concat([length, typeBuffer, data, crc]);
}

// CRC32 implementation for PNG chunks
function crc32(buf) {
    let crc = 0xFFFFFFFF;
    for (let i = 0; i < buf.length; i++) {
        crc ^= buf[i];
        for (let j = 0; j < 8; j++) {
            if (crc & 1) {
                crc = (crc >>> 1) ^ 0xEDB88320;
            } else {
                crc = crc >>> 1;
            }
        }
    }
    return (crc ^ 0xFFFFFFFF) >>> 0;
}

// Process each app
const appDirs = fs.readdirSync(APPS_DIR).filter(d =>
    fs.statSync(path.join(APPS_DIR, d)).isDirectory() &&
    fs.existsSync(path.join(APPS_DIR, d, 'config.json'))
);

console.log(`Generating ${appDirs.length} PNG icons...`);

for (const appId of appDirs) {
    const config = JSON.parse(fs.readFileSync(path.join(APPS_DIR, appId, 'config.json'), 'utf-8'));
    const accent = config.accent || '#c9a84c';
    const { r, g, b } = hexToRGB(accent);

    const png = createPNG(256, 256, r, g, b);
    const iconPath = path.join(ICONS_DIR, `icon.png`);

    // electron-builder expects icon.png in build/ or icon in the app dir
    // For per-app icons, we'll save them separately
    const appIconPath = path.join(ICONS_DIR, `${appId}.png`);
    fs.writeFileSync(appIconPath, png);

    console.log(`  ${appId}: ${appIconPath} (${accent})`);
}

// Also create a default icon.png in build/
const defaultPng = createPNG(256, 256, 201, 168, 76); // AMTL gold
fs.writeFileSync(path.join(BUILD_DIR, 'icon.png'), defaultPng);
console.log(`\nDefault icon: ${path.join(BUILD_DIR, 'icon.png')}`);
console.log('Done.');
