<template>
  <tr>
    <td>{{domainName}}</td>
    <td>
      <a v-bind:href="'https://www.virustotal.com/gui/domain/'+ domainName + '/detection'" target="_blank"  class="virustotal-value">
        <span class="border-value virustotal-score">{{vtScor}}</span>
        Engines Detected
      </a>
    </td>
    <td>
      Grade
      <a v-bind:href="'https://observatory.mozilla.org/analyze/'+ domainName" target="_blank">
      <span class="fill-value grade-value" :class="observatoryGrade.toLowerCase() +'-grade'">{{observatoryGrade}}</span>
      </a>
    </td>
    <td>
      <span class="tags" :class="provider +'-tag'">
        <i class="fas fa-circle"></i>
        {{provider}}
      </span>
    </td>
  </tr>
</template>

<script>
export default {
  name: "domainrow",
  props: {
    vtScor: String,
    domainName: String,
    observatoryGrade: String,
    provider: String
  },
  methods: {},
  created() {},
  components: {}
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
