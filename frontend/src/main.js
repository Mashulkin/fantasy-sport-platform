/**
 * Vue.js application entry point.
 * 
 * Configures and initializes the main Vue application with
 * Vuetify UI framework, Pinia state management, and routing.
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'

// Vuetify UI framework imports
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

import App from './App.vue'
import router from './router'

// Create Vuetify instance with custom theme configuration
const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1976D2',
          secondary: '#424242',
          accent: '#82B1FF',
          error: '#FF5252',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FFC107'
        }
      }
    }
  }
})

// Create and configure Vue application
const app = createApp(App)

app.use(createPinia())  // State management
app.use(router)         // Client-side routing
app.use(vuetify)        // UI framework

// Mount application to DOM
app.mount('#app')
