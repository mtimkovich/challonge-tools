<template>
  <v-dialog v-model="dialog" max-width="600" persistent>
    <v-card>
      <v-card-title class="headline">Report Match</v-card-title>

      <v-container>
        <v-layout row wrap>
          <v-flex xs6 class="text-xs-center" v-for="player of players" :key="player.id">
            <v-btn class="mb-4" :class="{success: player.id === selected}"
                   @click="select(player.id)">
              {{player.tag}}
            </v-btn>
            <v-slider v-model="player.score"
                      label="Score"
                      :min="-1"
                      :max="3"
                      thumb-label="always"
                      thumb-size="24"
                      ticks="always"
                      tick-size="2"
                      class="mr-4">
            </v-slider>
          </v-flex>
        </v-layout>
      </v-container>

      <v-card-actions>
        <v-spacer></v-spacer>

        <v-btn flat @click.stop="dialog=false">
          Close
        </v-btn>

        <v-btn color="success"
               flat
               :disabled="!valid"
               @click.stop="dialog=false">
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>


<script>
export default {
  props: {
    value: Boolean,
    match: Object,
  },
  data() {
    return {
      selected: -1,
      players: [
        {id: 0, tag: '', score: 0},
        {id: 1, tag: '', score: 0},
      ],
    }
  },
  watch: {
    match() {
      this.players[0].tag = this.match.player1_tag;
      this.players[1].tag = this.match.player2_tag;
    }
  },
  methods: {
    // Toggle the selected winning player.
    select(id) {
      this.selected = this.selected === id ? -1 : id;
    }
  },
  computed: {
    dialog: {
      get() {
        return this.value;
      },
      set(value) {
        if (!value) {
          // Reset.
          this.selected = -1;
          this.players[0].score = 0;
          this.players[1].score = 0;
        }
        this.$emit('input', value);
      }
    },
    valid() {
      const p1 = this.players[0].score;
      const p2 = this.players[1].score;
      return (this.selected === 0 && p1 > p2) || (this.selected === 1 && p1 < p2);
    },
  },
}
</script>
