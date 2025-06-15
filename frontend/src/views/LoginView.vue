<!--
  User authentication login page.
  
  Provides login form with validation and error handling
  for user authentication via email or username.
-->
<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card>
          <!-- Login form header -->
          <v-card-title class="text-h5 text-center">
            Fantasy Sports Platform
          </v-card-title>
          <v-card-subtitle class="text-center">
            Sign in to your account
          </v-card-subtitle>
          
          <v-card-text>
            <!-- Login form -->
            <v-form @submit.prevent="handleLogin">
              <!-- Username/email input -->
              <v-text-field
                v-model="credentials.username"
                label="Email or Username"
                prepend-icon="mdi-account"
                variant="outlined"
                required
              ></v-text-field>
              
              <!-- Password input with toggle visibility -->
              <v-text-field
                v-model="credentials.password"
                label="Password"
                prepend-icon="mdi-lock"
                variant="outlined"
                :type="showPassword ? 'text' : 'password'"
                :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append="showPassword = !showPassword"
                required
              ></v-text-field>
              
              <!-- Error message display -->
              <v-alert
                v-if="error"
                type="error"
                variant="tonal"
                class="mb-4"
              >
                {{ error }}
              </v-alert>
              
              <!-- Submit button -->
              <v-btn
                type="submit"
                block
                color="primary"
                size="large"
                :loading="loading"
              >
                Sign In
              </v-btn>
            </v-form>
          </v-card-text>
          
          <!-- Registration link -->
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text to="/register">
              Don't have an account? Sign up
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Component state
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

// Form data
const credentials = ref({
  username: '',
  password: ''
})

/**
 * Handle login form submission.
 * Attempts to authenticate user and redirect on success.
 */
const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  const result = await authStore.login(credentials.value)
  
  if (result.success) {
    router.push('/')
  } else {
    error.value = result.error
  }
  
  loading.value = false
}
</script>
