<template>
  <tr>
    <td>{{name}}</td>
    <td>
      <div class="flex-table-field">
        <div class="fill-value port-value">{{count}}</div>
      </div>
    </td>
  </tr>
</template>

<script>
export default {
  name: "dashboardtablerow",
  props: {
      name:String,
      count:Number
  },
  methods: {},
  created() {},
  components: {}
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
