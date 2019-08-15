<template>
  <v-app>
    <v-toolbar app>
      <v-toolbar-title class="headline">
        <span>auTO</span>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <!-- TODO: "Call" matches. -->
      <v-text-field hide-details
                    single-line
                    label="Tournament URL">
      </v-text-field>
        <!-- TODO: # of setups. -->
    </v-toolbar>

    <ReportDialog v-model="report_dialog" :match="current_match"></ReportDialog>

    <v-content>
      <v-layout row wrap>
        <v-flex xs6 v-for="match in sorted_matches" :key="match.suggested_play_order" pa-3>
          <v-card :class="{'grey lighten-4': match.in_progress}">
            <v-card-title>
              <div>
                <span class="headline">{{match.player1_tag}} vs. {{match.player2_tag}}</span><br>
                <span class="grey--text">{{match.round}}</span>
              </div>
            </v-card-title>

            <v-card-actions>
              <!-- TODO: Pull up reporting dialog. -->
              <v-btn flat color="success" @click.stop="openReportDialog(match)">Report Score</v-btn>
              <v-btn flat icon @click="toggle_in_progress(match)">
                <v-icon v-if="match.in_progress">pause</v-icon>
                <v-icon v-else>play_arrow</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-flex>
      </v-layout>
    </v-content>
  </v-app>
</template>

<script>
import ReportDialog from './components/ReportDialog.vue';

import axios from 'axios';

export default {
  name: 'App',
  components: {
    ReportDialog
  },
  data() {
    return {
      matches: [],
      report_dialog: false,
      current_match: Object,
    }
  },
  methods: {
    // TODO: Save in progress as cookie so it persists on reload.
    toggle_in_progress(match) {
      match.in_progress = !match.in_progress;
    },

    openReportDialog(match) {
      this.current_match = match;
      this.report_dialog = true;
    },
  },
  computed: {
    sorted_matches() {
      return this.matches.concat().sort((a, b) => {
        if (a.in_progress === b.in_progress) {
          return a.suggested_play_order - b.suggested_play_order;
        } else {
          return a.in_progress ? 1 : -1;
        }
      })
    }
  },
  created() {
    axios.post('http://localhost:5000/auTO/api/get_matches', {
      url: 'https://mtvmelee.challonge.com/100_amateur',
    })
    .then(response => {
      this.matches = response.data
    });
  }
}
</script>
