<template>
  <div>
    <el-row :span="24" align='middle'>
      <el-col :span="5">
        <el-form ref="form" label-width="100px" size="mini">
          <el-form-item label="画图窗口:">
            <el-select v-model="windowType" @change="windowselected" placeholder="请选择画图窗口"> <!--windowselected 根据 时间或次数窗口 改变窗口大小的单位-->
              <el-option label="时间窗口" value="时间窗口"></el-option>
              <el-option label="次数窗口" value="次数窗口"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="窗口大小:">
            <el-input v-model="windowSize" style="margin-right: 100px;">
              <i slot="suffix" style="font-style:normal;margin-right: 10px;">{{text}}</i> <!--给input内部加单位的方法-->
            </el-input>
          </el-form-item>

          <el-form-item label="文件:">
            <el-select v-model="fileName" @change="changeFile" placeholder="请选择日志文件">
              <el-option v-for='item in files' :key="item" :label="item" :value="item"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="目标类型:">
            <el-select v-model="targetType" @change="changeMethods" placeholder="请选择目标类型">
              <el-option label="IP" value="IP"></el-option>
              <el-option label="Account" value="Account"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="观察目标:">
            <el-select v-model="selectedTargets" multiple collapse-tags style="margin-left: 0px;" placeholder="请选择"><!--可多选,并且仅显示第一个-->
              <el-option v-for="item of targets" :key="item" :label="item" :value="item">
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="开始时间:"> <!--由picker-options决定starttime-->
            <el-date-picker 
              v-model="starttime" type="date" placeholder="选择日期" style="width: 100%;" value-format="yyyy-MM-dd HH:mm:ss" 
              @change="changeStarttime" :picker-options="pickerOptions"> <!--打印开始时间-->
            </el-date-picker>
          </el-form-item>

          <el-form-item label="结束时间:"> <!--由picker-options决定endtime-->
            <el-date-picker 
              v-model="endtime" type="date" placeholder="选择日期" style="width: 100%;" value-format="yyyy-MM-dd HH:mm:ss" 
              @change="changeEndtime" :picker-options="pickerOptions"> <!--打印结束时间-->
            </el-date-picker>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="getFrequency">开始画图</el-button>
          </el-form-item>
        </el-form>

        <el-card class="box-card" :span="5">
          <div v-if="newParams.stage > 1"> <!--stage不为1时 给出建议-->
            <p>
              建议的时间窗口：{{(newParams.newTimeWindow / 60).toFixed(2)}}分钟 <!--秒化分，保留两位小数-->
              <el-button @click="applyTime" style="float: right; padding: 3px 0" type="text">应用</el-button>
            </p>
            <p>
              建议的次数窗口: {{newParams.newNumberWindow}}次
              <el-button @click="applyNumber" style="float: right; padding: 3px 0" type="text">应用</el-button>
            </p>
            <p>推荐使用{{newType}}</p>
          </div>
          <div v-if="newParams.stage == 1"> <!--stage为1时 打印message-->
            {{ message }}
          </div>
        </el-card>

        <el-card class="box-card" :span="5">
          <div v-if="newParams.stage == 3">
            <div v-if="newType == '时间窗口'">
              <p>
                推测产生验证码的原因为：{{(newParams.newTimeWindow / 60).toFixed(2)}}分钟内,访问次数达到了{{newParams.newTimeBan}}次;
                产生验证码的概率为{{(newParams.newNumberMix*100).toFixed(2)}}%。
              </p>
            </div>
            <div v-if="newType == '次数窗口'">
              <p>
                推测产生验证码的原因为：{{(newParams.newNumberWindow)}}次访问的耗时小于{{(newParams.newNumberBan / 3600).toFixed(2)}}小时;
                产生验证码的概率为{{(newParams.newNumberMix*100).toFixed(2)}}%。
              </p>
            </div>
          </div>
          <div v-if="newParams.stage == 2">
            <div v-if="newType == '时间窗口'">
              <p>
                推测产生封禁的原因为：{{(newParams.newTimeWindow / 60).toFixed(2)}}分钟内,访问次数达到了{{newParams.newTimeBan}}次;
                封禁的概率为{{(newParams.newNumberMix*100).toFixed(2)}}%。
              </p>
            </div>
            <div v-if="newType == '次数窗口'">
              <p>
                推测产生封禁的原因为：{{(newParams.newNumberWindow)}}次访问的耗时小于{{(newParams.newNumberBan / 3600).toFixed(2)}}小时;
                封禁概率为{{(newParams.newNumberMix*100).toFixed(2)}}%。
              </p>
            </div>
          </div>
        </el-card>
      </el-col>
      <!-- 下面是画图的地方 -->
      <el-col :span="19">
        <div style="width:1000px; height:500px;" ref="chart"></div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as api from '../../assets/js/api'
import * as utils from '../../assets/js/utils' //可以得到绘图参数
export default {
  components: {
  },
  data () {
    return {
      metainfos: [], //存储元信息
      files: [], //日志文件名(多)
      windowType: '', //画图窗口：时间/次数
      windowSize: '', //窗口大小
      fileName: '', //日志文件名(单)
      targetType: '', //目标类型IP/Account
      targets: [], //总共有哪些目标
      selectedTargets: [], //选择了哪些目标
      text: '', //单位
      pickerOptions: {}, //可选时间框
      starttime: '', //开始日期时间
      endtime: '', //结束日期时间
      beginTimeStr: '',
      endTimeStr: '',

      featureType: '频率', //默认 该模块就是频率模块
      selected: 'all', //默认 向后端获取全部目标

      lineData: [],
      lineOption: '',
      scale: [0, 100], //x轴

      newParams: '', //新的参数 包括时间、次数、stage
      newType: '', //最终推荐的时间/次数
      newSize: '', //最终推荐的时间/次数的大小
      message: '', //stage为1时才显示出来
    }
  },

  mounted: function () { //生命周期函数, 一上来就执行里面的getFiles()
    this.getFiles();
  },

  methods: {
    getFiles: function () { 
      this.metainfos = [] //读取多个元信息到metainfos, 每一项对应一个日志文件.
      this.files = [] //将日志名放入, 每一项对应一个日志名.
      api.getMetaInfo().then(data => {
        this.metainfos = data.data.data
        console.log(this.metainfos)
        for (const item of this.metainfos) {
          this.files.push(item["fileName"])
        }
      })
    },
    /**
     * 根据窗口类型(时间/次数), 改变窗口大小的单位
     */
    windowselected () {
      this.windowSize = ''
      if (this.windowType == '时间窗口') {
        this.text = '分钟'
      }else {
        this.text = '次'
      }
    },
    /**
     * 选择日志文件, 并根据日志文件起止时间确定时间框可选位置
     */
    changeFile () { 
      this.targetType = ''; //换日志 需要 清空选择的目标类型
      this.selectedTargets = []; //换日志 需要 清空选择了哪些目标
      var time1 = '';
      var time2 = '';
      for (const item of this.metainfos) {
        if (item.fileName === this.fileName) {
          time1 = item.beginTimeStr.split(' ')[0].replace(/-/g, '/')//根据空格分组, 选取列表中的第一个元素, 即日期, 将全部'-'替换为'/'
          time2 = item.endTimeStr.split(' ')[0].replace(/-/g, '/')
          if (this.beginTimeStr == '') {
            this.beginTimeStr = item['beginTimeStr']
            this.endTimeStr = item['endTimeStr']
          }
          else {
            if (this.beginTimeStr > item['beginTimeStr']) {
              this.beginTimeStr = item['beginTimeStr']
            }
            if (this.endTimeStr < item['endTimeStr']) {
              this.endTimeStr = item['endTimeStr']
            }
          }
        }
      }
      console.log(time1, time2)
      var date1 = new Date(time1); //开始日期  
      var date2 = new Date(time2); //结束日期
      console.log(date1, date2)
      var time1Sec = date1.getTime(); //开始秒 
      var time2Sec = date2.getTime(); //结束秒
      console.log(time1Sec, time2Sec);
      this.pickerOptions = { //生成时间框可选位置
        disabledDate(time) {
          return !((time.getTime() >= time1Sec) && (time.getTime() <= time2Sec))//选择disable的日期, return ture的部分被disable
        }
      }
    },
    /**
     * 改变目标类型(IP/Account)，将该日志中所有该类型目标存入targets供后续选择
     */
    changeMethods () {
      this.selectedTargets = [] //清空已选目标
      if (this.targetType == 'IP') {
        for (const item of this.metainfos) {
          if (item['fileName'] === this.fileName) {
            this.targets = []
            for (const ip in item['ipDetail']) {
              this.targets.push(ip)
            }
          }
        }
      }
      if (this.targetType == 'Account') {
        for (const item of this.metainfos) { //for of 遍历值
          if (item['fileName'] === this.fileName) {
            this.targets = []
            for (const account in item['accountDetail']) { //for in 遍历键
              this.targets.push(account)
            }
          }
        }
      }
    },

    /**
     * 打印开始时间 打印结束时间
     */    
    changeStarttime () {
      console.log(this.starttime)
    },
    changeEndtime () {
      console.log(this.endtime)
    },
    /**
     * 开始画图
     */  
    getFrequency: function () {
      this.drawLine();
    },
    drawLine: function () {
      // 1.准备请求参数
      let params = new FormData() //params是请求参数
      params.append('fileName', this.fileName)
      if (this.featureType === '频率') {
        params.append('featureType', 0)
      }
      if (this.windowType === '时间窗口') {
        params.append('windowType', 0)
        params.append('windowSize', this.windowSize * 60) //时间窗口以秒做单位
      }
      if (this.windowType === '次数窗口') {
        params.append('windowType', 1)
        params.append('windowSize', this.windowSize) //次数窗口以1做单位
      }
      if (this.targetType === 'IP') {
        params.append('targetType', 0)
      }
      if (this.targetType === 'Account') {
        params.append('targetType', 1)
      }
      params.append('selectedTargets', this.selectedTargets)
      params.append('beginTime', this.starttime)
      let str_tmp = this.endtime.split(" ")[0] + " 23:59:59" //取最后一天最后时刻作为endtime
      params.append('endTime', str_tmp)
      params.forEach((value, key) => { //打印查看params对象
        console.log(`key ${key}: value ${value}`);
      })
      // 2.向后台发送请求(这里经过了api.js的处理)
      api.getFrequencyData(params).then(data => {
        this.lineData = data.lineData
        // 3.配置options
        var t1 = new Date()
        this.lineOption = utils.getLineOption(this.featureType, this.windowType,
          this.lineData, this.scale, this.selected, this.beginTimeStr, this.endTimeStr)
        var t2 = new Date()
        console.log("---------------------options配置用时：", (t2.getTime() - t1.getTime()) / 1000)
        // 4.获取实例，画图
        var myChart_fre = this.$echarts.init(this.$refs.chart);
        myChart_fre.clear()
        console.log('初始化echarts实例...')
        myChart_fre.setOption(this.lineOption);
        var that = this
        /**
         * 监听缩放
         */
        myChart_fre.on('datazoom', function (params) {//params里存有代表滑动条的起始的数字
          var start = myChart_fre.getModel().option.dataZoom[0].start;//获取axis
          var end = myChart_fre.getModel().option.dataZoom[0].end;//获取axis
          that.scale = [start, end]
          console.log('new scale: ', that.scale)
          that.lineOption = utils.getLineOption(that.featureType, that.windowType,
            that.lineData, that.scale, that.selected, that.beginTimeStr, that.endTimeStr)
          myChart_fre.setOption(that.lineOption)
        })
        /**
         * 监听选择了哪些线，修改图例
         */
        myChart_fre.on('legendselectchanged', function (params) {
          console.log(params.selected)
          that.selected = params.selected
        })

        var t3 = new Date()
        console.log("---------------------图形渲染用时：", (t3.getTime() - t1.getTime()) / 1000)

        this.getFreParam() //推荐参数
      }).catch(function (error) {
          console.log(error);
      })
    },

    /**
     * 得到推荐参数
     */
    getFreParam: function () {
      //准备发送的参数
      let params = new FormData()
      params.append('fileName', this.fileName)
      if (this.featureType === '频率') {
        params.append('featureType', 0)
      }
      if (this.targetType === 'IP') {
        params.append('targetType', 0)
      }
      if (this.targetType === 'Account') {
        params.append('targetType', 1)
      }
      params.append('beginTime', this.starttime)
      params.append('endTime', this.endtime)
      //向后端发送请求
      api.getFrequencyParams(params).then(data => {
        this.newParams = data.data
        console.log(this.newParams)
        if (this.newParams.stage == 1) { //没有怀疑/封禁 不需要推荐
          this.message = '目标网站即未产生封禁，又未出现验证码，建议加大访问频率。'
          console.log(this.message)
        }
        if (this.newParams.stage == 3) {
          this.message = '目标网站未产生封禁，但出现了验证码'
          if (this.newParams.newNumberMix > this.newParams.newTimeMix) { //Mix代表概率，大者决定最终推荐(时间还是次数)
            this.newType = "次数窗口"
            this.newSize = newNumberWindow
          }
          else {
            this.newType = "时间窗口"
            this.newSize = this.newParams.newTimeWindow
          }
        }
        if (this.newParams.stage == 2) {
          this.message = '目标网站产生了封禁'
          if (this.newParams.newNumberMix > this.newParams.newTimeMix) { //Mix代表概率，大者决定最终推荐(时间还是次数)
            this.newType = "次数窗口"
            this.newSize = newNumberWindow
          }
          else {
            this.newType = "时间窗口"
            this.newSize = this.newParams.newTimeWindow
          }
        }
      }).catch(function (error) {
          console.log(error);
      })
    },
    applyTime: function () { //使用推荐时间参数
      this.windowType = "时间窗口"
      this.windowSize = this.newParams.newTimeWindow / 60 //秒化分
      this.text = "分钟"
    },
    applyNumber: function () { //使用推荐次数参数
      this.windowType = "次数窗口"
      this.windowSize = this.newParams.newNumberWindow
      this.text = "次"
    },
  },
}
</script>

<style>
</style>