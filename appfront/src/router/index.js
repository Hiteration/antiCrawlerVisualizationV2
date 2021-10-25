import Vue from 'vue'
import Router from 'vue-router'
import FileDisplay from '@/components/FileManager/FileDisplay'
import Single from '@/components/Plot/Single'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path:'/',
      redirect:'/filemanager/filedisplay'
    },
    {
      path: '/filemanager/filedisplay',
      component: FileDisplay,
    },
    {
      path: '/plot/variate',
      component: Single
    }
  ]
})
