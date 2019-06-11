<template>
  <div>
    {{matches}}
  </div>
</template>

<script>
from axios import 'axios';

export default {
  name: 'app',

  data() {
    return {
      matches: [],
    }
  },

  mounted() {
    axios.post('http://localhost:5000/auTO/api/get_matches', {
      url: 'https://mtvmelee.challonge.com/120'
    })
    .then(response => (this.matches = response))
  }
}
</script>
