// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import echarts from 'echarts'
import 'echarts/lib/component/title'
import axios from 'axios'
import VueAxios from 'vue-axios'

axios.defaults.timeout = 5000000;
Vue.use(VueAxios, axios);
Vue.prototype.$echarts = echarts
Vue.use(ElementUI)

Vue.config.productionTip = false

//全局注册组件

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
