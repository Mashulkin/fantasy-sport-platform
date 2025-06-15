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
        <!-- Data table displaying all configured parsers with their status and controls -->
        <v-data-table
          :headers="headers"
          :items="parsers"
          :loading="loading"
          class="elevation-1"
        >
          <!-- Custom template for active status column with colored chips -->
          <template v-slot:item.is_active="{ item }">
            <v-chip
              :color="item.is_active ? 'success' : 'error'"
              size="small"
            >
              {{ item.is_active ? 'Active' : 'Inactive' }}
            </v-chip>
          </template>

          <!-- Custom template for last execution status with appropriate colors -->
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

          <!-- Format last run timestamp for display -->
          <template v-slot:item.last_run="{ item }">
            {{ formatDate(item.last_run) }}
          </template>

          <!-- Action buttons for each parser row -->
          <template v-slot:item.actions="{ item }">
            <!-- Run parser button with loading indicator -->
            <v-btn
              icon
              size="small"
              color="primary"
              @click="runParser(item)"
              :loading="runningParsers.includes(item.id)"
            >
              <v-icon>mdi-play</v-icon>
            </v-btn>
            <!-- View logs button -->
            <v-btn
              icon
              size="small"
              color="info"
              @click="showLogs(item)"
            >
              <v-icon>mdi-text-box-outline</v-icon>
            </v-btn>
            <!-- Edit parser button -->
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

    <!-- Create/Edit Parser Dialog -->
    <v-dialog v-model="showCreateDialog" max-width="600px">
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ editingParser ? 'Edit' : 'Create' }} Parser</span>
        </v-card-title>
        <v-card-text>
          <!-- Parser configuration form -->
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

    <!-- Parser Execution Logs Dialog -->
    <v-dialog v-model="showLogsDialog" max-width="800px">
      <v-card>
        <v-card-title>
          Parser Logs: {{ selectedParser?.name }}
        </v-card-title>
        <v-card-text>
          <!-- Display list of parser execution logs -->
          <v-list>
            <v-list-item v-for="log in logs" :key="log.id">
              <v-list-item-title>
                {{ formatDate(log.started_at) }} - {{ log.status }}
              </v-list-item-title>
              <v-list-item-subtitle>
                Records: {{ log.records_processed || 0 }}, 
                Errors: {{ log.errors_count || 0 }}
              </v-list-item-subtitle>
              <!-- Expandable section for detailed log data -->
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

// Reactive state variables
const loading = ref(false)
const parsers = ref([])
const runningParsers = ref([])  // Track which parsers are currently executing
const showCreateDialog = ref(false)
const showLogsDialog = ref(false)
const editingParser = ref(null)
const selectedParser = ref(null)
const logs = ref([])
const parserTypes = ref([])

// Supported fantasy platforms
const platforms = ['FPL', 'FANTEAM', 'SORARE', 'FANTON']

// Data table column configuration
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

// Form data for parser creation/editing
const parserForm = ref({
  name: '',
  platform: '',
  parser_type: '',
  schedule: '',
  is_active: true
})

/**
 * Fetch all parsers from the API
 * Updates the parsers list with current data from the server
 */
const fetchParsers = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/parsers')
    console.log('Parsers response:', response.data)
    parsers.value = response.data
  } catch (error) {
    console.error('Failed to fetch parsers:', error)
    // Show error to user with fallback for better UX
    alert('Failed to load parsers. Check console for details.')
  } finally {
    loading.value = false
  }
}

/**
 * Fetch available parser types from the API
 * Populates the parser type dropdown in the form
 */
const fetchParserTypes = async () => {
  try {
    const response = await apiClient.get('/parsers/types')
    parserTypes.value = response.data
  } catch (error) {
    console.error('Failed to fetch parser types:', error)
  }
}

/**
 * Execute a parser and monitor its progress
 * Handles the complete lifecycle of parser execution including status polling
 * 
 * @param {Object} parser - Parser configuration object to execute
 */
const runParser = async (parser) => {
  console.log(`Starting parser ${parser.name} (ID: ${parser.id})`)
  runningParsers.value.push(parser.id)
  let checkInterval = null
  let timeoutId = null
  
  try {
    // Start parser execution
    const response = await apiClient.post(`/parsers/${parser.id}/run`)
    const { task_id } = response.data
    
    console.log(`Parser ${parser.name} started with task ID: ${task_id}`)
    
    // Poll task status every 2 seconds until completion
    let checkCount = 0
    checkInterval = setInterval(async () => {
      checkCount++
      try {
        const statusResponse = await apiClient.get(`/parsers/task/${task_id}/status`)
        const { status, ready, successful, failed } = statusResponse.data
        
        console.log(`Check #${checkCount} - Task ${task_id} status:`, {
          status,
          ready,
          successful,
          failed
        })
        
        // Task completed - clean up and update UI
        if (ready) {
          console.log(`Task ${task_id} completed. Cleaning up...`)
          
          // Clear polling intervals
          if (checkInterval) {
            clearInterval(checkInterval)
            checkInterval = null
          }
          if (timeoutId) {
            clearTimeout(timeoutId)
            timeoutId = null
          }
          
          // Remove parser from running list
          const index = runningParsers.value.indexOf(parser.id)
          if (index > -1) {
            runningParsers.value.splice(index, 1)
            console.log(`Removed parser ${parser.id} from running list`)
          }
          
          // Log completion status
          if (successful) {
            console.log(`Parser ${parser.name} completed successfully`)
          } else if (failed) {
            console.error(`Parser ${parser.name} failed`)
          }
          
          // Refresh parsers data to show updated status
          console.log('Refreshing parsers data...')
          await fetchParsers()
        }
      } catch (error) {
        console.error(`Error checking task status (attempt ${checkCount}):`, error)
        // Continue polling, let timeout handle cleanup if needed
      }
    }, 2000)
    
    // Timeout handler - stop polling after 5 minutes to prevent infinite loops
    timeoutId = setTimeout(() => {
      console.log(`Timeout reached for parser ${parser.name}. Stopping status checks.`)
      
      if (checkInterval) {
        clearInterval(checkInterval)
        checkInterval = null
      }
      
      // Remove from running list
      const index = runningParsers.value.indexOf(parser.id)
      if (index > -1) {
        runningParsers.value.splice(index, 1)
        console.log(`Removed parser ${parser.id} from running list due to timeout`)
      }
      
      // Refresh data to show current state
      fetchParsers()
    }, 300000) // 5 minutes timeout
    
  } catch (error) {
    console.error('Failed to start parser:', error)
    // Ensure cleanup on error
    const index = runningParsers.value.indexOf(parser.id)
    if (index > -1) {
      runningParsers.value.splice(index, 1)
    }
  }
}

/**
 * Display execution logs for a specific parser
 * Fetches and shows historical execution data in a dialog
 * 
 * @param {Object} parser - Parser object to show logs for
 */
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

/**
 * Open edit dialog with parser data pre-filled
 * Prepares the form for editing an existing parser configuration
 * 
 * @param {Object} parser - Parser object to edit
 */
const editParser = (parser) => {
  editingParser.value = parser
  parserForm.value = { ...parser }
  showCreateDialog.value = true
}

/**
 * Save parser configuration (create new or update existing)
 * Handles both creation and update operations based on edit state
 */
const saveParser = async () => {
  try {
    if (editingParser.value) {
      // Update existing parser
      await apiClient.put(`/parsers/${editingParser.value.id}`, parserForm.value)
    } else {
      // Create new parser
      await apiClient.post('/parsers', parserForm.value)
    }
    closeDialog()
    fetchParsers()
  } catch (error) {
    console.error('Failed to save parser:', error)
  }
}

/**
 * Close the create/edit dialog and reset form state
 * Cleans up form data and editing state
 */
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

/**
 * Format date for display in the UI
 * Converts ISO date strings to localized format
 * 
 * @param {string|null} date - ISO date string or null
 * @returns {string} Formatted date or dash if no date
 */
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString()
}

/**
 * Get appropriate color for parser execution status
 * Maps status strings to Vuetify color names for consistent UI
 * 
 * @param {string} status - Parser execution status
 * @returns {string} Vuetify color name
 */
const getStatusColor = (status) => {
  switch (status) {
    case 'success': return 'success'
    case 'failed': return 'error'
    case 'running': return 'info'
    default: return 'grey'
  }
}

// Initialize component data when mounted
onMounted(() => {
  fetchParsers()
  fetchParserTypes()
})
</script>
