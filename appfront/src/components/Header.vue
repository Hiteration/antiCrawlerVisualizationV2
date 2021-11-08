<template>
  <div>
    <el-row>
    <el-col :span="5">
      <div style="display: flex; justify-content: center; overflow: hidden;">
        <img src="../assets/img/日志可视化系统.png" height="60px">
      </div>
      
    </el-col>
    <el-col :span="13"><div style=""><el-menu
      height="65px"
      :default-active="activeIndex"
      router
      class="el-menu-demo"
      mode="horizontal"
      @select="handleSelect"
      background-color="#1e2129"
      text-color="#fff"
      active-text-color="#ffd04b"
    >
      <el-menu-item index="/filemanager/filedisplay">文件管理</el-menu-item>
      <el-menu-item index="/plot/variate">特征可视化</el-menu-item>
      <!-- <el-menu-item index="/plot/variates">多变量可视化</el-menu-item> -->
    </el-menu></div></el-col>
    <el-col :span="6"><div style="height:60px; background-color:#1e2129; line-height: 60px">
        <FileUpload v-show="visible" @listenToChild="listenToChild"></FileUpload></div></el-col>
    </el-row>
  </div>
  
</template>

<script>
import FileUpload from "./FileManager/FileUpload.vue";
import * as api from "../assets/js/api";

export default {
  components: {
    FileUpload,
  },

  props: ["nav_tab"],
  data() {
    return {
      activeIndex: this.nav_tab,
      visible: this.nav_tab == '/filemanager/filedisplay'
    };
  },
  mounted: function () {
    api.getMetaInfo().then((data) => {
      this.tableData = data.data.data;
    });
  },
  computed: {
    switchStatus: function () {
      return this.nav_tab; // 直接监听props里的status状态
    },
  },
  methods: {
    listenToChild: function (data) {
      this.$emit("listenToChild",data)
    },
    handleSelect(key, keyPath) {
      console.log(this.nav_tab);
      console.log(key, keyPath);
    },
  },
};
</script>


<style>
.el-menu.el-menu--horizontal{
  border-bottom-width: 0px !important;
}
.el-menu-item.is-active {
  color: #3679fa !important;
  border-bottom-color: #3679fa !important;
  font-family: "Microsoft YaHei" !important;
  font-weight: bold !important;
  font-size: 18px !important;
  border-bottom-width: 0px !important;
}
.el-menu-item {
  color: #f2f3f8 !important;
  font-family: "Microsoft YaHei" !important;
  font-weight: bold !important;
  font-size: 18px !important;
  border-bottom-width: 0px !important;
}
</style>