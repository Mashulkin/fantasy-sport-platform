<template>
  <div>
    <h1 class="text-h3 mb-4">Admin Panel</h1>
    
    <v-row>
      <v-col cols="12" md="6">
        <v-card to="/admin/parsers" class="pa-4">
          <v-card-title>
            <v-icon left large color="primary">mdi-spider-web</v-icon>
            Parser Management
          </v-card-title>
          <v-card-text>
            Manage data parsers and schedules
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-card to="/admin/upload" class="pa-4">
          <v-card-title>
            <v-icon left large color="success">mdi-cloud-upload</v-icon>
            CSV Upload
          </v-card-title>
          <v-card-text>
            Upload CSV files with data
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
</script>
