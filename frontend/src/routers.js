import Vue from 'vue'
import Router from 'vue-router'
import home from './components/home';
import internetassets from './components/internetAssets';

Vue.use(Router)

export default new Router({
    mode: 'history',
    routes: [
        {
            path: '/home',
            name: 'home',
            component: home
        },
        {
            path: '/',
            name: 'internet assets',
            component: internetassets
        }
    ]
})