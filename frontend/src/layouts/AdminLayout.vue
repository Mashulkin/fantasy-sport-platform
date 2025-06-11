<template>
  <div>
    <router-view v-if="isAuthenticated && isSuperuser" />
    <v-container v-else class="fill-height">
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="6">
          <v-alert type="error" prominent>
            <v-row align="center">
              <v-col class="grow">
                You don't have permission to access this page.
              </v-col>
              <v-col class="shrink">
                <v-btn @click="$router.push('/login')">Login</v-btn>
              </v-col>
            </v-row>
          </v-alert>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const isSuperuser = computed(() => authStore.user?.is_superuser)

onMounted(async () => {
  // Проверяем авторизацию при загрузке
  if (authStore.token && !authStore.user) {
    await authStore.fetchUser()
  }
  
  if (!isAuthenticated.value || !isSuperuser.value) {
    router.push('/login')
  }
})
</script>
