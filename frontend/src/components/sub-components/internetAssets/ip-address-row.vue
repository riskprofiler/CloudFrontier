<template>
  <tr>
    <td>{{sk}}</td>
    <td v-if="asn">{{asn}}</td>
    <td v-else>NA</td>
    <td>
      <span>
        <country-flag v-if="countryCode" :country="countryCode"  size='normal'/>
      </span>
    </td>
    <td>
      <a v-bind:href="'https://www.virustotal.com/gui/ip-address/'+ sk + '/detection'" target="_blank"  class="virustotal-value">
        <span class="border-value virustotal-score">{{vtScor}}</span>
        Engines Detected
      </a>
    </td>
    <td>
      <span class="tags " :class="provider +'-tag'">
        <i class="fas fa-circle"></i> {{provider}}
      </span>
    </td>
    <td>

    <div class="tooltip cve-tooltips">
        <div class="flex-table-field" style="position: relative;">
            <a v-bind:href="'https://www.shodan.io/host/'+ sk" target="_blank">
            <div class="fill-value port-value" v-if="ports">{{ ports.length }}</div>
            <div class="fill-value port-value" v-else>NA</div>
            </a>
            
        </div>

        <div class="hover-cve-tooltip">
            <h6>Ports:</h6>
            <div v-for="value in ports" :key="value">{{ value }}</div>
        </div>
    </div>

    </td>
  <td>

    <div class="tooltip cve-tooltips">
        <div class="flex-table-field" style="position: relative;">
          <a v-bind:href="'https://www.shodan.io/host/'+ sk" target="_blank">
            <div class="fill-value port-value" v-if="vulns">{{ vulns.length }}</div>
            <div class="fill-value port-value" v-else>NA</div>
          </a>
        </div>

        <div class="hover-cve-tooltip">
            <h6>Vulnerabilities:</h6>
            <div v-for="value in vulns" :key="value">{{ value }}</div>
        </div>
    </div>

      <!-- <div class="flex-table-field">
        <div class="fill-value port-value" v-for="value in vulns" :key="value">{{ value }}</div>
      </div> -->
    </td>
  </tr>
</template>

<script>
export default {
  name: "ipaddressrow",
  props: {
    sk: String,
    countryCode: String,
    provider:String,
    asn:String,
    ports:Array,
    vtScor:String,
    vulns:Array
  },
  methods: {
  },
  created(){

  },
  components: {}
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
