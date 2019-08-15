<template>
    <v-dialog v-model="dialog" max-width="600">
      <v-card>
        <v-card-title class="headline">Report Match</v-card-title>

        <v-card-text>
          <v-container>
            <span class="headline">{{match.player1_tag}} vs. {{match.player2_tag}}</span><br>
          </v-container>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn color="primary"
                 flat
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
    match: null,
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
