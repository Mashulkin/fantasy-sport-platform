<template>
  <div>
    <!-- Debug Panel -->
    <v-expansion-panels class="mb-4" v-if="showDebug">
      <v-expansion-panel>
        <v-expansion-panel-title>Debug Info</v-expansion-panel-title>
        <v-expansion-panel-text>
          <div>Sort By: {{ JSON.stringify(sortBy) }}</div>
          <div>Players count: {{ players.length }}</div>
          <div>Displayed count: {{ displayPlayers.length }}</div>
          <div>First player: {{ displayPlayers[0]?.web_name }}</div>
          <div>Last player: {{ displayPlayers[displayPlayers.length - 1]?.web_name }}</div>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>

    <!-- Filters Card -->
    <v-card class="mb-4" elevation="0" color="grey-lighten-5">
      <v-card-text>
        <v-row align="center">
          <v-col cols="12" md="4">
            <v-text-field
              v-model="search"
              prepend-inner-icon="mdi-magnify"
              label="Search players..."
              variant="outlined"
              density="compact"
              hide-details
              clearable
              @update:modelValue="performSearch"
            ></v-text-field>
          </v-col>
          
          <v-col cols="6" md="2">
            <v-select
              v-model="filterPosition"
              :items="positions"
              label="Position"
              variant="outlined"
              density="compact"
              hide-details
              clearable
              multiple
              chips
              closable-chips
              prepend-inner-icon="mdi-human"
            ></v-select>
          </v-col>
          
          <v-col cols="6" md="2">
            <v-select
              v-model="filterTeam"
              :items="teams"
              item-title="abbreviation"
              item-value="id"
              label="Team"
              variant="outlined"
              density="compact"
              hide-details
              clearable
              multiple
              chips
              closable-chips
              prepend-inner-icon="mdi-shield-outline"
            ></v-select>
          </v-col>
          
          <v-col cols="6" md="2">
            <v-select
              v-model="filterStatus"
              :items="statuses"
              item-title="text"
              item-value="value"
              label="Status"
              variant="outlined"
              density="compact"
              hide-details
              clearable
              prepend-inner-icon="mdi-heart-pulse"
            ></v-select>
          </v-col>
          
          <v-col cols="6" md="2">
            <v-btn
              variant="outlined"
              @click="resetFilters"
              block
            >
              <v-icon start>mdi-filter-off</v-icon>
              Reset
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Players Table -->
    <v-card>
      <v-data-table
        :headers="simpleHeaders"
        :items="tableData"
        :loading="loading"
        :items-per-page="50"
        v-model:sort-by="sortBy"
        class="modern-table"
        hover
      >
        <!-- Name with tooltip -->
        <template v-slot:item.web_name="{ item }">
          <v-tooltip location="bottom">
            <template v-slot:activator="{ props }">
              <span v-bind="props" class="font-weight-medium">
                {{ item.web_name }}
              </span>
            </template>
            <span>{{ item.first_name }} {{ item.last_name }}</span>
          </v-tooltip>
        </template>
        
        <!-- Team with tooltip -->
        <template v-slot:item.team="{ item }">
          <v-tooltip location="bottom">
            <template v-slot:activator="{ props }">
              <v-chip
                v-bind="props"
                size="small"
                variant="outlined"
              >
                {{ item.team }}
              </v-chip>
            </template>
            <span>{{ item.team_name }}</span>
          </v-tooltip>
        </template>
        
        <!-- Position with modern chip -->
        <template v-slot:item.position="{ item }">
          <v-chip 
            size="small" 
            :color="getPositionColor(item.position)"
            variant="flat"
          >
            {{ item.position }}
          </v-chip>
        </template>
        
        <!-- Status with better icons -->
        <template v-slot:item.status="{ item }">
          <v-tooltip location="bottom" v-if="item.status !== 'a'">
            <template v-slot:activator="{ props }">
              <v-icon 
                v-bind="props"
                :color="getStatusColor(item.status)"
                size="small"
              >
                {{ getStatusIcon(item.status) }}
              </v-icon>
            </template>
            <span>{{ getStatusText(item.status) }}</span>
          </v-tooltip>
        </template>
        
        <!-- Cost with currency -->
        <template v-slot:item.cost="{ item }">
          <span class="font-weight-medium">£{{ item.cost }}</span>
        </template>
        
        <!-- Ownership with progress -->
        <template v-slot:item.ownership="{ item }">
          <div style="min-width: 80px">
            <div class="text-caption">{{ item.ownership }}%</div>
            <v-progress-linear
              :model-value="item.ownership"
              height="4"
              :color="getOwnershipColor(item.ownership)"
            ></v-progress-linear>
          </div>
        </template>
        
        <!-- Form with gradient chip -->
        <template v-slot:item.form="{ item }">
          <v-chip 
            size="small" 
            :color="getFormColor(item.form)"
            variant="flat"
          >
            {{ item.form }}
          </v-chip>
        </template>
        
        <!-- Points with emphasis -->
        <template v-slot:item.total_points="{ item }">
          <span class="font-weight-bold text-h6">{{ item.total_points }}</span>
        </template>
        
        <!-- Event Points -->
        <template v-slot:item.event_points="{ item }">
          <v-chip
            v-if="item.event_points > 0"
            size="small"
            :color="item.event_points >= 10 ? 'success' : 'default'"
            variant="tonal"
          >
            {{ item.event_points }}
          </v-chip>
          <span v-else class="text-grey">-</span>
        </template>
      </v-data-table>
    </v-card>
    
    <!-- Statistics Cards -->
    <v-row class="mt-4">
      <v-col v-for="stat in statistics" :key="stat.title" cols="12" sm="6" md="3">
        <v-card>
          <v-card-text class="d-flex align-center justify-space-between">
            <div>
              <div class="text-overline">{{ stat.title }}</div>
              <div class="text-h4 font-weight-bold">{{ stat.value }}</div>
            </div>
            <v-icon :color="stat.color" size="40">{{ stat.icon }}</v-icon>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import apiClient, { playersAPI, teamsAPI } from '@/api/client'

// Debug mode
const showDebug = ref(false)

const loading = ref(false)
const players = ref([])
const teams = ref([])
const search = ref('')
const filterPosition = ref([])
const filterTeam = ref([])
const filterStatus = ref(null)
const totalPlayers = ref(0)

const positions = ['GK', 'DEF', 'MID', 'FWD']
const statuses = [
  { text: 'Available', value: 'a' },
  { text: 'Injured', value: 'i' },
  { text: 'Doubtful', value: 'd' },
  { text: 'Suspended', value: 's' }
]

// Сортировка
const sortBy = ref([{ key: 'total_points', order: 'desc' }])

// Простые заголовки без кастомных функций
const simpleHeaders = [
  { title: 'Name', key: 'web_name', sortable: true },
  { title: 'Team', key: 'team', sortable: true },
  { title: 'Pos', key: 'position', sortable: true },
  { title: '', key: 'status', sortable: false, width: '40px' },
  { title: 'Price', key: 'cost', sortable: true },
  { title: 'Own', key: 'ownership', sortable: true },
  { title: 'Form', key: 'form', sortable: true },
  { title: 'Total', key: 'total_points', sortable: true },
  { title: 'GW', key: 'event_points', sortable: true }
]

// Преобразуем данные в плоскую структуру для таблицы
const tableData = computed(() => {
  console.log('Computing tableData...')
  
  let result = players.value.map(player => {
    const profile = getFPLProfile(player)
    
    return {
      // Основные данные игрока
      id: player.id,
      web_name: player.web_name || '',
      first_name: player.first_name || '',
      last_name: player.last_name || '',
      
      // Данные из профиля
      team: profile?.team?.abbreviation || '-',
      team_name: profile?.team?.name || '-',
      position: profile?.player_position || '-',
      status: profile?.status || 'a',
      cost: profile?.current_cost?.toFixed(1) || '0.0',
      ownership: parseFloat(profile?.ownership_percent?.toFixed(1) || 0),
      form: parseFloat(profile?.form?.toFixed(1) || 0),
      total_points: profile?.total_points || 0,
      event_points: profile?.event_points || 0,
      
      // Для фильтров
      team_id: profile?.team_id,
      platform_player_id: profile?.platform_player_id
    }
  })

  // Применяем фильтры
  if (filterPosition.value && filterPosition.value.length > 0) {
    result = result.filter(p => filterPosition.value.includes(p.position))
  }

  if (filterTeam.value && filterTeam.value.length > 0) {
    result = result.filter(p => filterTeam.value.includes(p.team_id))
  }

  if (filterStatus.value) {
    result = result.filter(p => p.status === filterStatus.value)
  }

  if (search.value) {
    const searchLower = search.value.toLowerCase()
    result = result.filter(p => 
      p.web_name.toLowerCase().includes(searchLower) ||
      p.first_name.toLowerCase().includes(searchLower) ||
      p.last_name.toLowerCase().includes(searchLower)
    )
  }

  console.log('TableData computed, count:', result.length)
  return result
})

// Для отладки - следим за изменениями sortBy
watch(sortBy, (newVal) => {
  console.log('Sort changed:', newVal)
}, { deep: true })

// Отображаемые игроки (устарело, теперь используем tableData)
const displayPlayers = computed(() => tableData.value)

// Статистика
const statistics = computed(() => [
  {
    title: 'Total Players',
    value: totalPlayers.value,
    icon: 'mdi-account-group',
    color: 'primary'
  },
  {
    title: 'Injured',
    value: injuredPlayers.value,
    icon: 'mdi-medical-bag',
    color: 'error'
  },
  {
    title: 'Top Form',
    value: topFormPlayers.value,
    icon: 'mdi-fire',
    color: 'success'
  },
  {
    title: 'Teams',
    value: teams.value.length,
    icon: 'mdi-shield-outline',
    color: 'info'
  }
])

// Computed для статистики
const injuredPlayers = computed(() => {
  return tableData.value.filter(p => p.status === 'i').length
})

const topFormPlayers = computed(() => {
  return tableData.value.filter(p => p.form >= 7).length
})

const fetchPlayers = async () => {
  loading.value = true
  try {
    const response = await playersAPI.getAll({ 
      limit: 1000,
      platform: 'FPL'
    })
    console.log('Players fetched:', response.data.length)
    players.value = response.data || []
    
    // Get count
    try {
      const countResponse = await apiClient.get('/players/count', {
        params: { platform: 'FPL' }
      })
      totalPlayers.value = countResponse.data.total
    } catch (error) {
      console.error('Failed to fetch count:', error)
    }
  } catch (error) {
    console.error('Failed to fetch players:', error)
    players.value = []
  } finally {
    loading.value = false
  }
}

const fetchTeams = async () => {
  try {
    const response = await teamsAPI.getAll()
    teams.value = response.data
  } catch (error) {
    console.error('Failed to fetch teams:', error)
  }
}

// Вспомогательные функции
const getFPLProfile = (player) => {
  if (!player || !player.platform_profiles || player.platform_profiles.length === 0) {
    return null
  }
  return player.platform_profiles.find(p => p.platform === 'FPL')
}

// Функции для UI
const getPositionColor = (position) => {
  switch (position) {
    case 'GK': return 'amber'
    case 'DEF': return 'green'
    case 'MID': return 'blue'
    case 'FWD': return 'red'
    default: return 'grey'
  }
}

const getFormColor = (form) => {
  const f = parseFloat(form)
  if (f >= 7) return 'success'
  if (f >= 5) return 'light-green'
  if (f >= 3) return 'warning'
  return 'error'
}

const getOwnershipColor = (ownership) => {
  const o = parseFloat(ownership)
  if (o >= 30) return 'error'
  if (o >= 15) return 'warning'
  if (o >= 5) return 'success'
  return 'grey'
}

const getStatusIcon = (status) => {
  switch(status) {
    case 'i': return 'mdi-ambulance'
    case 'd': return 'mdi-help-circle'
    case 's': return 'mdi-card-off'
    default: return ''
  }
}

const getStatusColor = (status) => {
  switch(status) {
    case 'i': return 'error'
    case 'd': return 'warning'
    case 's': return 'error'
    default: return 'success'
  }
}

const getStatusText = (status) => {
  switch(status) {
    case 'i': return 'Injured'
    case 'd': return 'Doubtful'
    case 's': return 'Suspended'
    case 'a': return 'Available'
    default: return 'Unknown'
  }
}

// Поиск с задержкой
let searchTimeout = null
const performSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    // Поиск выполняется через computed tableData
  }, 300)
}

const resetFilters = () => {
  search.value = ''
  filterPosition.value = []
  filterTeam.value = []
  filterStatus.value = null
}

onMounted(() => {
  fetchPlayers()
  fetchTeams()
})
</script>

<style scoped>
.modern-table :deep(.v-data-table__th) {
  background-color: rgb(var(--v-theme-primary)) !important;
  color: white !important;
  font-weight: 600 !important;
  text-transform: uppercase;
  font-size: 0.875rem;
}

.modern-table :deep(.sortable) {
  cursor: pointer;
}

.modern-table :deep(.v-data-table__th:hover) {
  background-color: rgba(var(--v-theme-primary), 0.9) !important;
}
</style>