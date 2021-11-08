<template>
  <div class="Single-wrapper">
    <Header :nav_tab="currentNav"></Header>
    <el-tabs v-model="activeName" type="border-card">
      <el-tab-pane name="frequency" label="访问强度"><Frequency></Frequency></el-tab-pane>
      <el-tab-pane name="interval" label="访问间隔稳定性"><Interval></Interval></el-tab-pane>
      <el-tab-pane label="访问持续性"><Rest></Rest></el-tab-pane>
      <el-tab-pane label="访问多样性"><Diversity></Diversity></el-tab-pane>
      <el-tab-pane label="访问周期性"><Periodism></Periodism></el-tab-pane>
    </el-tabs>
  </div>
</template>
<script>
  import Header from '../Header'
  import Frequency from './Frequency'
  import Interval from './Interval'
  import Rest from './Rest'
  import Diversity from './Diversity'
  import Periodism from './Periodism'

  export default {
    components: {
      Header,
      Frequency,
      Interval,
      Rest,
      Diversity,
      Periodism,
    },
    data() {
      return {
        currentNav: "/plot/variate",
        activeName: "frequency"
      };
    }
  };
</script>
<style>
.Single-wrapper{
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.el-tabs {
  background-color: #f2f3f8;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}
.el-tabs__nav-scroll{
  background-color: #cfd9eb;
}

.el-tabs__item {
  color: #333740 !important;
  font-family: "Microsoft YaHei" !important;
  font-weight: bold !important;
  font-size: 16px !important;
}

.el-tabs__item.is-active {
  color: #3679fa !important;
  background-color: #f2f3f8 !important;
}
.el-tabs__item:hover {
  color: #3679fa !important;
}
.el-tabs__content {
  background-color: #f2f3f8;
  flex-grow: 1;
}
</style>

