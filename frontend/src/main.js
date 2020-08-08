import Vue from 'vue'
import App from './App.vue'
import router from './routers'
import CountryFlag from 'vue-country-flag'
import config from './config.json'

Vue.config.productionTip = false

Vue.component('country-flag', CountryFlag)

Vue.prototype.$config = config

new Vue({
  render: h => h(App),
  router:router
}).$mount('#app')
