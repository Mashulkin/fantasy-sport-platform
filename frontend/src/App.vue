<!-- 
  Main application component with navigation and layout structure.
  
  Provides the root layout including navigation drawer, app bar,
  and main content area with authentication-aware menu items.
-->
<template>
  <v-app>
    <!-- Side navigation drawer -->
    <v-navigation-drawer v-model="drawer" app>
      <v-list>
        <!-- User info section -->
        <v-list-item
          v-if="authStore.isLoggedIn"
          prepend-avatar="https://randomuser.me/api/portraits/men/85.jpg"
          :title="authStore.user?.username || 'User'"
          :subtitle="authStore.user?.email"
        ></v-list-item>
        <v-list-item
          v-else
          title="Not logged in"
          subtitle="Please sign in"
        ></v-list-item>
      </v-list>

      <v-divider></v-divider>

      <!-- Navigation menu -->
      <v-list density="compact" nav>
        <v-list-item
          v-for="item in menuItems"
          :key="item.title"
          :to="item.route"
          :prepend-icon="item.icon"
          :title="item.title"
        ></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- Top application bar -->
    <v-app-bar app>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>Fantasy Sports Platform</v-toolbar-title>
      
      <v-spacer></v-spacer>

      <!-- Login button for unauthenticated users -->
      <v-btn 
        v-if="!authStore.isLoggedIn"
        color="primary"
        @click="$router.push('/login')"
      >
        Login
      </v-btn>
      
      <!-- User menu for authenticated users -->
      <v-menu v-else>
        <template v-slot:activator="{ props }">
          <v-btn icon v-bind="props">
            <v-icon>mdi-account</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item @click="handleLogout">
            <v-list-item-title>Logout</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- Main content area -->
    <v-main>
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const drawer = ref(true)

// Navigation menu items configuration
const menuItems = [
  { title: 'Dashboard', icon: 'mdi-view-dashboard', route: '/' },
  { title: 'Players', icon: 'mdi-account-group', route: '/players' },
  { title: 'Teams', icon: 'mdi-shield-outline', route: '/teams' },
  { title: 'Tournaments', icon: 'mdi-trophy', route: '/tournaments' },
  { title: 'Statistics', icon: 'mdi-chart-line', route: '/statistics' },
  { title: 'Admin', icon: 'mdi-cog', route: '/admin' },
]

/**
 * Handle user logout and redirect to login page.
 */
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

// Check authentication status on app initialization
if (authStore.token) {
  authStore.fetchUser()
}
</script>
