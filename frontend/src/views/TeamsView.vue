<!--
  Teams overview and management component.
  
  Displays teams in a card grid layout with player statistics
  and detailed team information modal dialog.
-->
<template>
  <div>
    <v-card>
      <v-card-title class="text-h4">Teams</v-card-title>
      
      <v-card-text>
        <!-- Teams grid layout -->
        <v-row>
          <v-col 
            v-for="team in teams" 
            :key="team.id"
            cols="12"
            sm="6"
            md="4"
            lg="3"
          >
            <!-- Team card with hover effects -->
            <v-card 
              class="team-card"
              elevation="2"
              @click="showTeamPlayers(team)"
            >
              <v-card-text class="text-center">
                <!-- Team abbreviation (large) -->
                <div class="text-h3 font-weight-bold mb-2">
                  {{ team.abbreviation }}
                </div>
                
                <!-- Team full name -->
                <div class="text-subtitle-1">{{ team.name }}</div>
                
                <!-- League information -->
                <div class="text-caption text-grey">{{ team.league }}</div>
                
                <v-divider class="my-3"></v-divider>
                
                <!-- Team statistics -->
                <div class="d-flex justify-space-around">
                  <div>
                    <div class="text-h6">{{ getTeamPlayerCount(team.id) }}</div>
                    <div class="text-caption">Players</div>
                  </div>
                  <div>
                    <div class="text-h6">£{{ getTeamAvgPrice(team.id) }}</div>
                    <div class="text-caption">Avg Price</div>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Team players detail modal -->
    <v-dialog v-model="showDialog" max-width="800">
      <v-card>
        <v-card-title>
          {{ selectedTeam?.name }} Players
          <v-spacer></v-spacer>
          <v-btn icon @click="showDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        
        <v-card-text>
          <!-- Players table for selected team -->
          <v-simple-table>
            <template v-slot:default>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Position</th>
                  <th>Price</th>
                  <th>Form</th>
                  <th>Points</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="player in teamPlayers" :key="player.id">
                  <td>{{ player.web_name }}</td>
                  <td>
                    <v-chip 
                      size="small" 
                      :color="getPositionColor(getPosition(player))"
                    >
                      {{ getPosition(player) }}
                    </v-chip>
                  </td>
                  <td>£{{ getCost(player) }}</td>
                  <td>{{ getForm(player) }}</td>
                  <td>{{ getTotalPoints(player) }}</td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { teamsAPI, playersAPI } from '@/api/client'

// Component state
const teams = ref([])
const players = ref([])
const showDialog = ref(false)
const selectedTeam = ref(null)

/**
 * Get players for the currently selected team, sorted by points.
 * @returns {Array} Filtered and sorted players
 */
const teamPlayers = computed(() => {
  if (!selectedTeam.value) return []
  
  return players.value.filter(player => {
    const profile = player.platform_profiles?.find(p => p.platform === 'FPL')
    return profile?.team_id === selectedTeam.value.id
  }).sort((a, b) => {
    const aPoints = getFPLProfile(a)?.total_points || 0
    const bPoints = getFPLProfile(b)?.total_points || 0
    return bPoints - aPoints
  })
})

/**
 * Fetch teams data from API.
 */
const fetchTeams = async () => {
  try {
    const response = await teamsAPI.getAll()
    teams.value = response.data
  } catch (error) {
    console.error('Failed to fetch teams:', error)
  }
}

/**
 * Fetch players data from API.
 */
const fetchPlayers = async () => {
  try {
    const response = await playersAPI.getAll({ limit: 1000, platform: 'FPL' })
    players.value = response.data
  } catch (error) {
    console.error('Failed to fetch players:', error)
  }
}

/**
 * Count players in a specific team.
 * @param {number} teamId - Team ID
 * @returns {number} Number of players
 */
const getTeamPlayerCount = (teamId) => {
  return players.value.filter(player => {
    const profile = player.platform_profiles?.find(p => p.platform === 'FPL')
    return profile?.team_id === teamId
  }).length
}

/**
 * Calculate average price for team players.
 * @param {number} teamId - Team ID
 * @returns {string} Formatted average price
 */
const getTeamAvgPrice = (teamId) => {
  const teamPlayers = players.value.filter(player => {
    const profile = player.platform_profiles?.find(p => p.platform === 'FPL')
    return profile?.team_id === teamId
  })
  
  if (teamPlayers.length === 0) return '0.0'
  
  const totalPrice = teamPlayers.reduce((sum, player) => {
    const profile = player.platform_profiles?.find(p => p.platform === 'FPL')
    return sum + (profile?.current_cost || 0)
  }, 0)
  
  return (totalPrice / teamPlayers.length).toFixed(1)
}

/**
 * Show team players modal dialog.
 * @param {Object} team - Team object
 */
const showTeamPlayers = (team) => {
  selectedTeam.value = team
  showDialog.value = true
}

// Player data helper functions

/**
 * Get FPL profile for a player.
 * @param {Object} player - Player object
 * @returns {Object|null} FPL profile
 */
const getFPLProfile = (player) => {
  return player.platform_profiles?.find(p => p.platform === 'FPL')
}

/**
 * Get player position.
 * @param {Object} player - Player object
 * @returns {string} Player position
 */
const getPosition = (player) => {
  return getFPLProfile(player)?.player_position || '-'
}

/**
 * Get formatted player cost.
 * @param {Object} player - Player object
 * @returns {string} Formatted cost
 */
const getCost = (player) => {
  return getFPLProfile(player)?.current_cost?.toFixed(1) || '0.0'
}

/**
 * Get formatted player form.
 * @param {Object} player - Player object
 * @returns {string} Formatted form rating
 */
const getForm = (player) => {
  return getFPLProfile(player)?.form?.toFixed(1) || '0.0'
}

/**
 * Get player total points.
 * @param {Object} player - Player object
 * @returns {number} Total points
 */
const getTotalPoints = (player) => {
  return getFPLProfile(player)?.total_points || 0
}

/**
 * Get color for position display.
 * @param {string} position - Player position
 * @returns {string} Vuetify color name
 */
const getPositionColor = (position) => {
  switch (position) {
    case 'GK': return 'amber'
    case 'DEF': return 'green'
    case 'MID': return 'blue'
    case 'FWD': return 'red'
    default: return 'grey'
  }
}

// Initialize data on component mount
onMounted(() => {
  fetchTeams()
  fetchPlayers()
})
</script>

<style scoped>
/* Team card hover effects */
.team-card {
  cursor: pointer;
  transition: all 0.3s;
}

.team-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.2) !important;
}
</style>
