<template>
  <div class="FileDisplay-wrapper">
    <Header :nav_tab="currentNav" @listenToChild="listenToChild"></Header>
    <el-table header-cell-style="color: #333740" :data="tableData" style="width: 100%">
      <el-table-column label="文件名" prop="fileName"></el-table-column>
      <el-table-column label="IP个数" prop="ipNum"></el-table-column>
      <el-table-column label="Account个数" prop="accountNum"></el-table-column>
      <el-table-column label="开始时间" prop="beginTimeStr"></el-table-column>
      <el-table-column label="结束时间" prop="endTimeStr"></el-table-column>
      <el-table-column label="">
        <template slot-scope="scope">
          <el-button size="mini" @click="fileDel(scope.row.fileName)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>

</template>

<script>
import Header from '../Header'
import * as api from '../../assets/js/api'

export default {
  components: {
    Header,
  },
  data () {
    return {
      currentNav: "/filemanager/filedisplay",
      tableData: [],
      chartList: '',
      fileName: '',
    }
  },
  mounted: function () {
    api.getMetaInfo().then(data => {
      this.tableData = data.data.data
    })
  },
  methods: {
    listenToChild: function (data) {
      this.tableData = data
    },
    fileDel: function(data) {
      console.log(data)
      this.axios.post("http://127.0.0.1:8000/filemanager/filedel", {data: data}).then(res => {
        api.getMetaInfo().then(data => {
          this.tableData = data.data.data
        })
      })
      .catch( res => {
        console.log(res)
      })
    }
  }
}
</script>

<style>
.FileDisplay-wrapper{
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.el-table{
  padding: 8px 16px;
  background-color: #f2f3f8;
  flex-grow: 1;
  font-family: "Microsoft YaHei" !important;
  font-weight: bold !important;
  font-size: 14px !important;
}
</style>

<style scoped>
.el-button{
  font-family: "Microsoft YaHei" !important;
}
</style>