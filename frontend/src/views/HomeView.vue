<!--
  Application dashboard with statistics and quick actions.
  
  Displays key metrics, recent activity, and provides
  quick access to common platform functions.
-->
<template>
  <div>
    <h1 class="text-h3 mb-6">Dashboard</h1>
    
    <!-- Statistics cards row -->
    <v-row>
      <v-col 
        v-for="stat in stats" 
        :key="stat.title" 
        cols="12" 
        sm="6" 
        md="3"
      >
        <v-card>
          <v-card-text class="pa-4">
            <div class="d-flex align-center justify-space-between">
              <!-- Stat information -->
              <div>
                <p class="text-caption text-grey">{{ stat.title }}</p>
                <p class="text-h4 font-weight-bold">{{ stat.value }}</p>
                <p 
                  class="text-caption" 
                  :class="stat.change > 0 ? 'text-success' : 'text-error'"
                >
                  <v-icon size="small">
                    {{ stat.change > 0 ? 'mdi-arrow-up' : 'mdi-arrow-down' }}
                  </v-icon>
                  {{ Math.abs(stat.change) }}%
                </p>
              </div>
              <!-- Stat icon -->
              <v-icon 
                :icon="stat.icon" 
                size="40" 
                :color="stat.color"
              ></v-icon>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <!-- Recent activity section -->
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>Recent Activity</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item 
                v-for="activity in recentActivities" 
                :key="activity.id"
              >
                <template v-slot:prepend>
                  <v-icon 
                    :icon="activity.icon" 
                    :color="activity.color"
                  ></v-icon>
                </template>
                <v-list-item-title>{{ activity.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ activity.time }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Quick actions section -->
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Quick Actions</v-card-title>
          <v-card-text>
            <v-btn block color="primary" class="mb-2">
              <v-icon left>mdi-plus</v-icon>
              Create Tournament
            </v-btn>
            <v-btn block color="secondary" class="mb-2">
              <v-icon left>mdi-cloud-upload</v-icon>
              Import Data
            </v-btn>
            <v-btn block color="accent">
              <v-icon left>mdi-refresh</v-icon>
              Run Parser
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Dashboard statistics data
const stats = ref([
  { 
    title: 'Total Players', 
    value: '0', 
    change: 0, 
    icon: 'mdi-account-group', 
    color: 'primary' 
  },
  { 
    title: 'Active Tournaments', 
    value: '0', 
    change: 0, 
    icon: 'mdi-trophy', 
    color: 'warning' 
  },
  { 
    title: 'Total Teams', 
    value: '0', 
    change: 0, 
    icon: 'mdi-shield-outline', 
    color: 'success' 
  },
  { 
    title: 'Data Updates', 
    value: '0', 
    change: 0, 
    icon: 'mdi-database', 
    color: 'info' 
  },
])

// Recent activity data
const recentActivities = ref([
  { 
    id: 1, 
    title: 'System initialized', 
    time: 'Just now', 
    icon: 'mdi-check-circle', 
    color: 'success' 
  },
  { 
    id: 2, 
    title: 'Waiting for data import', 
    time: '1 minute ago', 
    icon: 'mdi-clock-outline', 
    color: 'info' 
  },
])
</script>
