<template>
  <div>
    <v-card>
      <v-card-title>
        <span class="text-h5">Parser Management</span>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="showCreateDialog = true">
          <v-icon left>mdi-plus</v-icon>
          Add Parser
        </v-btn>
      </v-card-title>

      <v-card-text>
        <!-- Parsers Table -->
        <v-data-table
          :headers="headers"
          :items="parsers"
          :loading="loading"
          class="elevation-1"
        >
          <template v-slot:item.is_active="{ item }">
            <v-chip
              :color="item.is_active ? 'success' : 'error'"
              size="small"
            >
              {{ item.is_active ? 'Active' : 'Inactive' }}
            </v-chip>
          </template>

          <template v-slot:item.last_status="{ item }">
            <v-chip
              v-if="item.last_status"
              :color="getStatusColor(item.last_status)"
              size="small"
            >
              {{ item.last_status }}
            </v-chip>
            <span v-else>-</span>
          </template>

          <template v-slot:item.last_run="{ item }">
            {{ formatDate(item.last_run) }}
          </template>

          <template v-slot:item.actions="{ item }">
            <v-btn
              icon
              size="small"
              color="primary"
              @click="runParser(item)"
              :loading="runningParsers.includes(item.id)"
            >
              <v-icon>mdi-play</v-icon>
            </v-btn>
            <v-btn
              icon
              size="small"
              color="info"
              @click="showLogs(item)"
            >
              <v-icon>mdi-text-box-outline</v-icon>
            </v-btn>
            <v-btn
              icon
              size="small"
              color="warning"
              @click="editParser(item)"
            >
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Create/Edit Dialog -->
    <v-dialog v-model="showCreateDialog" max-width="600px">
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ editingParser ? 'Edit' : 'Create' }} Parser</span>
        </v-card-title>
        <v-card-text>
          <v-form ref="form">
            <v-text-field
              v-model="parserForm.name"
              label="Name"
              required
            ></v-text-field>
            
            <v-select
              v-model="parserForm.platform"
              :items="platforms"
              label="Platform"
              required
            ></v-select>
            
            <v-select
              v-model="parserForm.parser_type"
              :items="parserTypes"
              label="Parser Type"
              required
            ></v-select>
            
            <v-text-field
              v-model="parserForm.schedule"
              label="Schedule (Cron)"
              hint="e.g., 0 */4 * * * (every 4 hours)"
            ></v-text-field>
            
            <v-switch
              v-model="parserForm.is_active"
              label="Active"
            ></v-switch>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="closeDialog">Cancel</v-btn>
          <v-btn color="primary" variant="flat" @click="saveParser">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Logs Dialog -->
    <v-dialog v-model="showLogsDialog" max-width="800px">
      <v-card>
        <v-card-title>
          Parser Logs: {{ selectedParser?.name }}
        </v-card-title>
        <v-card-text>
          <v-list>
            <v-list-item v-for="log in logs" :key="log.id">
              <v-list-item-title>
                {{ formatDate(log.started_at) }} - {{ log.status }}
              </v-list-item-title>
              <v-list-item-subtitle>
                Records: {{ log.records_processed || 0 }}, 
                Errors: {{ log.errors_count || 0 }}
              </v-list-item-subtitle>
              <div v-if="log.log_data" class="mt-2">
                <v-expansion-panels flat>
                  <v-expansion-panel>
                    <v-expansion-panel-title>View Log</v-expansion-panel-title>
                    <v-expansion-panel-text>
                      <pre>{{ log.log_data }}</pre>
                    </v-expansion-panel-text>
                  </v-expansion-panel>
                </v-expansion-panels>
              </div>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="showLogsDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'

const loading = ref(false)
const parsers = ref([])
const runningParsers = ref([])
const showCreateDialog = ref(false)
const showLogsDialog = ref(false)
const editingParser = ref(null)
const selectedParser = ref(null)
const logs = ref([])
const parserTypes = ref([])

const platforms = ['FPL', 'FANTEAM', 'SORARE', 'FANTON']

const headers = [
  { title: 'Name', key: 'name' },
  { title: 'Platform', key: 'platform' },
  { title: 'Type', key: 'parser_type' },
  { title: 'Schedule', key: 'schedule' },
  { title: 'Status', key: 'is_active' },
  { title: 'Last Run', key: 'last_run' },
  { title: 'Last Status', key: 'last_status' },
  { title: 'Actions', key: 'actions', sortable: false }
]

const parserForm = ref({
  name: '',
  platform: '',
  parser_type: '',
  schedule: '',
  is_active: true
})

const fetchParsers = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/parsers')
    console.log('Parsers response:', response.data)
    parsers.value = response.data
  } catch (error) {
    console.error('Failed to fetch parsers:', error)
    // Показываем ошибку пользователю
    alert('Failed to load parsers. Check console for details.')
  } finally {
    loading.value = false
  }
}

const fetchParserTypes = async () => {
  try {
    const response = await apiClient.get('/parsers/types')
    parserTypes.value = response.data
  } catch (error) {
    console.error('Failed to fetch parser types:', error)
  }
}

const runParser = async (parser) => {
  runningParsers.value.push(parser.id)
  try {
    await apiClient.post(`/parsers/${parser.id}/run`)
    // Show success message
    console.log(`Parser ${parser.name} started`)
  } catch (error) {
    console.error('Failed to run parser:', error)
  } finally {
    // Remove from running list after 5 seconds
    setTimeout(() => {
      const index = runningParsers.value.indexOf(parser.id)
      if (index > -1) {
        runningParsers.value.splice(index, 1)
      }
      fetchParsers() // Refresh data
    }, 5000)
  }
}

const showLogs = async (parser) => {
  selectedParser.value = parser
  try {
    const response = await apiClient.get(`/parsers/${parser.id}/logs`)
    logs.value = response.data
    showLogsDialog.value = true
  } catch (error) {
    console.error('Failed to fetch logs:', error)
  }
}

const editParser = (parser) => {
  editingParser.value = parser
  parserForm.value = { ...parser }
  showCreateDialog.value = true
}

const saveParser = async () => {
  try {
    if (editingParser.value) {
      await apiClient.put(`/parsers/${editingParser.value.id}`, parserForm.value)
    } else {
      await apiClient.post('/parsers', parserForm.value)
    }
    closeDialog()
    fetchParsers()
  } catch (error) {
    console.error('Failed to save parser:', error)
  }
}

const closeDialog = () => {
  showCreateDialog.value = false
  editingParser.value = null
  parserForm.value = {
    name: '',
    platform: '',
    parser_type: '',
    schedule: '',
    is_active: true
  }
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString()
}

const getStatusColor = (status) => {
  switch (status) {
    case 'success': return 'success'
    case 'failed': return 'error'
    case 'running': return 'info'
    default: return 'grey'
  }
}

onMounted(() => {
  fetchParsers()
  fetchParserTypes()
})
</script>