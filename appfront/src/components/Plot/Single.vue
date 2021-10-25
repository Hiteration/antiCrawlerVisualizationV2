<template>
  <div>
    <Header :nav_tab="currentNav"></Header>
    <el-tabs v-model="activeName" style="height: 200px;" type="card">
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