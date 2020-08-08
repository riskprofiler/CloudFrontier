<template>
  <tr>
    <td>
      <a href="#">{{storageName}}</a>
    </td>
    <td>
      <span class="tags " :class="provider +'-tag'">
        <i class="fas fa-circle"></i> {{provider}}
      </span>
    </td>
    <td style="text-align: center;">
      <span v-if="publicIndicator === false" class="check-icon yes-value">
        <i class="fas fa-check-circle"></i>
      </span>
      <span v-else class="check-icon no-value">
        <i class="fas fa-times-circle"></i>
      </span>
    </td>
  </tr>
</template>

<script>
export default {
  name: "objectstorgaerow",
  props: {
    storageName:String,
    provider:String,
    publicIndicator:Boolean
  },
  methods: {},
  created() {},
  components: {}
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
