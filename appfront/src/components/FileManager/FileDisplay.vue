<template>
  <div>
    <Header :nav_tab="currentNav" @listenToChild="listenToChild"></Header>
    <el-table :data="tableData" style="width: 100%">
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
.demo-table-expand {
  font-size: 0;
}
.demo-table-expand label {
  width: 90px;
  color: #99a9bf;
}
.demo-table-expand .el-form-item {
  margin-right: 0;
  margin-bottom: 0;
  width: 50%;
}
</style>