<!--
  Admin layout component with authentication guard.
  
  Provides access control for admin routes, ensuring only
  authenticated superusers can access admin functionality.
-->
<template>
  <div>
    <!-- Loading state during authentication check -->
    <v-container v-if="loading" class="fill-height">
      <v-row align="center" justify="center">
        <v-col cols="12" class="text-center">
          <v-progress-circular
            indeterminate
            color="primary"
            size="64"
          ></v-progress-circular>
          <p class="mt-4">Loading...</p>
        </v-col>
      </v-row>
    </v-container>
    
    <!-- Admin content for authorized users -->
    <router-view v-else-if="isAuthenticated && isSuperuser" />
    
    <!-- Access denied message for unauthorized users -->
    <v-container v-else class="fill-height">
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="6">
          <v-alert type="error" prominent>
            <v-row align="center">
              <v-col class="grow">
                <div v-if="!isAuthenticated">
                  You need to be logged in to access this page.
                </div>
                <div v-else>
                  You don't have permission to access this page. Admin privileges required.
                </div>
              </v-col>
              <v-col class="shrink">
                <v-btn 
                  v-if="!isAuthenticated"
                  @click="$router.push('/login')"
                  color="white"
                  variant="outlined"
                >
                  Login
                </v-btn>
                <v-btn 
                  v-else
                  @click="$router.push('/')"
                  color="white"
                  variant="outlined"
                >
                  Go Home
                </v-btn>
              </v-col>
            </v-row>
          </v-alert>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(true)

// Computed properties for authentication state
const isAuthenticated = computed(() => authStore.isLoggedIn)
const isSuperuser = computed(() => authStore.user?.is_superuser === true)

/**
 * Check authentication and authorization on component mount.
 */
onMounted(async () => {
  try {
    // Fetch user data if token exists but user data is missing
    if (authStore.token && !authStore.user) {
      await authStore.fetchUser()
    }
    
    // Redirect based on authentication status
    if (!isAuthenticated.value) {
      await router.push('/login')
    } else if (!isSuperuser.value) {
      console.log('User is not superuser:', authStore.user)
    }
  } catch (error) {
    console.error('Auth check error:', error)
    await router.push('/login')
  } finally {
    loading.value = false
  }
})
</script>
