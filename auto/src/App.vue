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

    <v-content>
      <v-layout row wrap>
        <v-flex xs6 v-for="match in sorted_matches" :key="match.suggested_match_order" pa-3>
          <v-card :class="{'grey lighten-4': match.in_progress}">
            <v-card-title class="headline">
              {{match.player1_tag}} vs. {{match.player2_tag}}
            </v-card-title>

            <v-card-actions>
              <!-- TODO: Pull up reporting dialog. -->
              <v-btn flat color="success">Report Score</v-btn>
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
import axios from 'axios';

export default {
  name: 'App',
  data() {
    return {
      matches: [],
    }
  },
  methods: {
    // TODO: Save in progress as cookie so it persists on reload.
    toggle_in_progress(match) {
      match.in_progress = !match.in_progress;
    }
  },
  computed: {
    sorted_matches: function() {
      function compare(a, b) {
        if (a.in_progress === b.in_progress) {
          return a.suggested_match_order - b.suggested_match_order;
        } else {
          return a.in_progress ? 1 : -1;
        }
      }

      return this.matches.concat().sort(compare);
    }
  },
  mounted() {
    axios.post('http://localhost:5000/auTO/api/get_matches', {
      url: 'https://mtvmelee.challonge.com/100_amateur',
    })
    .then(response => (this.matches = response.data))
  }
}
</script>
