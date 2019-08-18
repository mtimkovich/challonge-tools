<template>
  <v-dialog v-model="dialog" max-width="600">
    <v-card>
      <v-card-title class="headline">Report Match</v-card-title>

      <v-container>
        <v-layout row wrap>
          <v-flex xs6 class="text-xs-center">
            <v-btn>
              {{match.player1_tag}}
            </v-btn>
            <v-slider v-model="player1_score"
                      label="Score"
                      :min="-1"
                      :max="3"
                      thumb-label
                      ticks="always"
                      class="mr-4">
            </v-slider>
          </v-flex>
          <v-flex xs6 class="text-xs-center">
            <v-btn>
              {{match.player2_tag}}
            </v-btn>
            <v-slider v-model="player2_score"
                      label="Score"
                      :min="-1"
                      :max="3"
                      thumb-label
                      ticks="always"
                      class="mr-2">
            </v-slider>
          </v-flex>
        </v-layout>
      </v-container>

        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn color="success"
                 flat
                 disabled
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
      player1_score: 0,
      player2_score: 0,
    }
  },
  computed: {
    dialog: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit('input', value);
      }
    }
  },
}
</script>
