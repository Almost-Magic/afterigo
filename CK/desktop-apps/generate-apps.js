/**
 * Generate config.json and package.json for each AMTL desktop app.
 * Run once: node generate-apps.js
 */
const fs = require('fs');
const path = require('path');

const apps = [
    {
        id: 'elaine',
        name: 'Elaine',
        desc: 'AI Chief of Staff',
        url: 'http://localhost:5000',
        healthUrl: 'http://localhost:5000/api/health',
        port: 5000,
        accent: '#c9a84c',
        letter: 'E',
    },
    {
        id: 'workshop',
        name: 'The Workshop',
        desc: 'Central App Launcher',
        url: 'http://localhost:5003',
        healthUrl: 'http://localhost:5003/api/health',
        port: 5003,
        accent: '#c9a84c',
        letter: 'W',
    },
    {
        id: 'ripple',
        name: 'Ripple CRM',
        desc: 'Relationship Intelligence Engine',
        url: 'http://localhost:3100',
        healthUrl: 'http://localhost:8100/api/health',
        port: 3100,
        accent: '#38bdf8',
        letter: 'R',
    },
    {
        id: 'touchstone',
        name: 'Touchstone',
        desc: 'Marketing Attribution Dashboard',
        url: 'http://localhost:3200',
        healthUrl: 'http://localhost:8200/api/health',
        port: 3200,
        accent: '#f59e0b',
        letter: 'T',
    },
    {
        id: 'writer',
        name: 'CK Writer',
        desc: '8-Mode Writing Studio',
        url: 'http://localhost:5004',
        healthUrl: 'http://localhost:5004/api/health',
        port: 5004,
        accent: '#34d399',
        letter: 'W',
    },
    {
        id: 'learning',
        name: 'Learning Assistant',
        desc: 'Micro-skill Training',
        url: 'http://localhost:5002',
        healthUrl: 'http://localhost:5002/api/health',
        port: 5002,
        accent: '#38bdf8',
        letter: 'L',
    },
    {
        id: 'peterman',
        name: 'Peterman',
        desc: 'Brand Intelligence Engine',
        url: 'http://localhost:5008',
        healthUrl: 'http://localhost:5008/api/health',
        port: 5008,
        accent: '#60a5fa',
        letter: 'P',
    },
    {
        id: 'genie',
        name: 'Genie',
        desc: 'AI Bookkeeper',
        url: 'http://localhost:3000',
        healthUrl: 'http://localhost:8000/api/health',
        port: 3000,
        accent: '#a78bfa',
        letter: 'G',
    },
    {
        id: 'costanza',
        name: 'Costanza',
        desc: 'Mental Models Engine',
        url: 'http://localhost:5001',
        healthUrl: 'http://localhost:5001/api/health',
        port: 5001,
        accent: '#a78bfa',
        letter: 'C',
    },
    {
        id: 'author-studio',
        name: 'Author Studio',
        desc: 'Book DNA & Amazon Listings',
        url: 'http://localhost:5007',
        healthUrl: 'http://localhost:5007/api/health',
        port: 5007,
        accent: '#e879f9',
        letter: 'A',
    },
    {
        id: 'junk-drawer',
        name: 'Junk Drawer',
        desc: 'Cognitive File Intelligence',
        url: 'http://localhost:3005',
        healthUrl: 'http://localhost:5005/api/health',
        port: 3005,
        accent: '#94a3b8',
        letter: 'J',
    },
    {
        id: 'supervisor',
        name: 'Supervisor',
        desc: 'AMTL Runtime Manager',
        url: 'http://localhost:9000/api/status',
        healthUrl: 'http://localhost:9000/api/health',
        port: 9000,
        accent: '#f87171',
        letter: 'S',
    },
];

for (const cfg of apps) {
    const appDir = path.join(__dirname, 'apps', cfg.id);
    fs.mkdirSync(appDir, { recursive: true });

    // config.json
    fs.writeFileSync(
        path.join(appDir, 'config.json'),
        JSON.stringify(cfg, null, 2) + '\n'
    );

    // package.json
    const pkg = {
        name: `amtl-${cfg.id}`,
        version: '1.0.0',
        description: `${cfg.name} -- ${cfg.desc} (AMTL Desktop)`,
        main: '../../shared/main.js',
        scripts: {
            start: `electron ../../shared/main.js --config=./config.json`,
            build: 'electron-builder --win',
        },
        author: 'Mani Padisetti <mani@almostmagic.tech>',
        license: 'Proprietary',
        build: {
            appId: `tech.almostmagic.${cfg.id.replace('-', '')}`,
            productName: cfg.name,
            extends: null,
            files: [
                '../../shared/**/*',
                'config.json',
            ],
            extraMetadata: {
                main: 'shared/main.js',
            },
            directories: {
                output: `../../dist/${cfg.id}`,
                buildResources: '../../shared',
            },
            win: {
                target: 'nsis',
                icon: `../../icons/${cfg.id}.ico`,
            },
            nsis: {
                oneClick: true,
                perMachine: false,
                createDesktopShortcut: true,
                shortcutName: cfg.name,
            },
        },
    };

    fs.writeFileSync(
        path.join(appDir, 'package.json'),
        JSON.stringify(pkg, null, 2) + '\n'
    );

    console.log(`Generated: ${cfg.id} (${cfg.name} on port ${cfg.port})`);
}

// Generate SVG icons
const iconsDir = path.join(__dirname, 'icons');
fs.mkdirSync(iconsDir, { recursive: true });

for (const cfg of apps) {
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
  <rect width="256" height="256" rx="48" fill="${cfg.accent}"/>
  <text x="128" y="140" dominant-baseline="middle" text-anchor="middle"
        font-family="Segoe UI, sans-serif" font-weight="700"
        font-size="128" fill="#0a0e1a">${cfg.letter}</text>
</svg>`;
    fs.writeFileSync(path.join(iconsDir, `${cfg.id}.svg`), svg);
    console.log(`Icon: ${cfg.id}.svg`);
}

console.log(`\nDone. ${apps.length} apps configured.`);
console.log('SVG icons in icons/. Convert to .ico for electron-builder builds.');
console.log('Run individual app: cd apps/<name> && npm start');
