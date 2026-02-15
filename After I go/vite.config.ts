import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
// import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    // VitePWA({
    //   registerType: 'autoUpdate',
    //   includeAssets: ['favicon.svg', 'robots.txt'],
    //   manifest: {
    //     name: 'After I Go',
    //     short_name: 'After I Go',
    //     description: 'A private vault that helps the right people find what you need after you\'re gone',
    //     theme_color: '#7C9A72',
    //     background_color: '#FAFAF9',
    //     display: 'standalone',
    //     orientation: 'portrait',
    //     scope: '/afterigo/',
    //     start_url: '/afterigo/',
    //     icons: [
    //       {
    //         src: '/afterigo/icons/icon-192.png',
    //         sizes: '192x192',
    //         type: 'image/png'
    //       },
    //       {
    //         src: '/afterigo/icons/icon-512.png',
    //         sizes: '512x512',
    //         type: 'image/png'
    //       }
    //     ]
    //   }
    // })
  ],
  base: '/afterigo/',
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['framer-motion', 'lucide-react'],
          storage: ['dexie'],
          pdf: ['pdfmake']
        }
      }
    }
  },
  server: {
    port: 5173,
    host: true
  },
  define: {
    'process.env': {}
  }
})
