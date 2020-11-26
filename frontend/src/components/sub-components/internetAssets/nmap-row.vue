<template>
  <tr>
    <td>{{host}}</td>
    <td>{{port}}/{{protocol}}</td>
    <td>{{service}}</td>
    <td>{{script}}</td>
  </tr>
</template>

<script>
export default {
  name: "nmapresultsrow",
  props: {
    host: String,
    port: Number,
    protocol: String,
    service: String,
    script: String
  },
  methods: {},
  created() {},
  components: {}
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
