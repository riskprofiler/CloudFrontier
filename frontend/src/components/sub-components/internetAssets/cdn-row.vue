<template>
  <tr>
    <td>{{name}}</td>
    <td>
      <a href="#">{{urlEndpoint}}</a>
    </td>
    <td>{{customeDomain}}</td>
    <td>
      <span class="status-icon enabled-value">
        <i class="fas fa-circle"></i> Enabled
      </span>
    </td>
    <td>
      <span class="tags " :class="provider +'-tag'">
        <i class="fas fa-circle"></i> {{provider}}
      </span>
    </td>
  </tr>
</template>

<script>
export default {
  name: "cdnrow",
  props: {
    name:String,
    urlEndpoint:String,
    customeDomain:String,
    status:String,
    provider:String
  },
  methods: {},
  created() {},
  components: {}
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
