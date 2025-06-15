/**
 * Vite configuration for Vue.js development server.
 * 
 * Configures build tool settings, development server options,
 * and path aliases for the frontend application.
 */

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  
  resolve: {
    alias: {
      // Set up @ alias for src directory
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  
  server: {
    host: true,           // Allow external connections
    port: 3000,           // Development server port
    watch: {
      usePolling: true    // Enable polling for Docker file watching
    },
    allowedHosts: [       // Allowed host names
      'fantasy.local', 
      'localhost', 
      '.local'
    ]
  }
})
