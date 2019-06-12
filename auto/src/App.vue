<template>
  <v-app>
    <v-toolbar app>
      <v-toolbar-title class="headline">
        <span>auTO</span>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
                       hide-details
                       single-line
                       label="Tournament URL"
                       ></v-text-field>
    </v-toolbar>

    <v-content>
      <v-layout row wrap>
        <v-flex xs6 v-for="match in matches" :key="match.suggested_match_order" pa-3>
          <v-card>
            <v-card-title class="headline">
              {{match.player1_tag}} vs. {{match.player2_tag}}
            </v-card-title>

            <v-card-actions>
              <v-btn flat color="success">Report Score</v-btn>
              <v-btn flat icon>
                <v-icon>play_arrow</v-icon>
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
  mounted() {
    axios.post('http://localhost:5000/auTO/api/get_matches', {
      url: 'https://mtvmelee.challonge.com/100_amateur',
    })
    .then(response => (this.matches = response.data))
  }
}
</script>
