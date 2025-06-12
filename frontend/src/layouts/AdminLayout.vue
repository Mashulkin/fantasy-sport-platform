<template>
  <div>
    <!-- Loading state -->
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
    
    <!-- Authorized content -->
    <router-view v-else-if="isAuthenticated && isSuperuser" />
    
    <!-- Unauthorized message -->
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

const isAuthenticated = computed(() => authStore.isLoggedIn)
const isSuperuser = computed(() => authStore.user?.is_superuser === true)

onMounted(async () => {
  try {
    // Проверяем авторизацию при загрузке
    if (authStore.token && !authStore.user) {
      await authStore.fetchUser()
    }
    
    // Проверяем права доступа
    if (!isAuthenticated.value) {
      // Если не авторизован, редиректим на логин
      await router.push('/login')
    } else if (!isSuperuser.value) {
      // Если авторизован, но не суперпользователь
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