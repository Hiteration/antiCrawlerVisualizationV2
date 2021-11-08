<template>
  <div>
    <el-row :span="24" align='middle'>
      <el-col :span="5">
        <el-form ref="form" label-width="100px" size="mini">
          <el-form-item label="休眠时长:">
            <el-input v-model="deltaTime">
              <i slot="suffix" style="font-style:normal;margin-right: 10px;">小时</i>
            </el-input>
            <!-- <div>{{text}}</div> -->
          </el-form-item>

          <el-form-item label="文件：">
            <el-select v-model="filename" @change="changeFile" placeholder="请选择日志文件">
              <el-option v-for='item in files' :key="item" :label="item" :value="item"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="目标类型:">
            <el-select v-model="targettype" @change="changeMethods" placeholder="请选择目标类型">
              <el-option label="IP" value="IP"></el-option>
              <el-option label="Account" value="Account"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="观察目标:">
            <el-select v-model="selectedtarget" multiple collapse-tags placeholder="请选择">
              <el-option v-for="item of targets" :key="item" :label="item" :value="item">
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="开始时间:">
            <el-date-picker v-model="starttime" type="date" placeholder="选择日期" style="width: 100%;" value-format="yyyy-MM-dd HH:mm:ss" @change="changeStarttime" :picker-options="pickerOptions">
            </el-date-picker>
            <!-- <el-input v-model="starttime" placeholder="临时输入"></el-input> -->
          </el-form-item>
          <el-form-item label="结束时间:">
            <el-date-picker v-model="endtime" type="date" placeholder="选择日期" style="width: 100%;" value-format="yyyy-MM-dd HH:mm:ss" @change="changeEndtime" :picker-options="pickerOptions">
            </el-date-picker>
            <!-- <el-input v-model="endtime" placeholder="临时输入"></el-input> -->
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="getRest">开始画图</el-button>
          </el-form-item>
        </el-form>
        <el-card class="box-card" :span="5">
          <!-- <div slot="header" class="clearfix">
                  <span>推荐的窗口参数</span>
                </div> -->
          <div v-if="newParams.stage == 3">
            <p>建议的休眠时长：{{(newParams.newDeltaTimeWindow / 3600)}}小时
              <!-- ,推测封禁阈值的下界为{{newParams.newTimeBan}} 次 -->
              <el-button @click="applyRest" style="float: right; padding: 3px 0" type="text">应用</el-button>
            </p>
          </div>
          <div>
            {{message}}
          </div>
        </el-card>
        <el-card class="box-card" :span="5">
          <!-- <div slot="header" class="clearfix">
                  <span>推荐的窗口参数</span>
                </div> -->
          <div v-if="newParams.stage == 3">
            <p>推测出现验证码的原因为：连续{{(newParams.newDeltaTimeBan)}}天的每日最大间隔小于{{(newParams.newDeltaTimeWindow / 3600).toFixed(2)}}小时;在所有满足该条件的访问记录中，有{{(newParams.newDeltaTimeMix*100).toFixed(2)}}%的访问被封禁。
            </p>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <div id="rest" style="width: 1000px;height:500px;"></div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as api from '../../assets/js/api'
import * as utils from '../../assets/js/utils'
export default {
  components: {
  },
  data () {
    return {
      pickerOptions: {},
      metainfos: [],
      deltaTime: '',
      filename: '',
      files: [],
      featuretype: '每日休息时长',
      targettype: '',
      targettypes: ['IP', 'Account'],
      selectedtarget: [],
      targets: [],
      starttime: '',
      endtime: '',

      newParams: '',
      newType: '',
      message: '',

      lineData: [],
      lineOption: '',
      scale: [0, 100],
      selected: 'all',
      beginTimeStr: '',
      endTimeStr: '',

      boxData: [],

    }
  },
  mounted: function () {
    this.getFiles();
  },
  methods: {
    getFiles: function () {
      this.metainfos = []
      this.files = []
      api.getMetaInfo().then(data => {
        this.metainfos = data.data.data
        for (var item of this.metainfos) {
          this.files.push(item["filename"])
        }
      })

    },
    drawLine: function () {
      // 1.从后台获取数据
      let params = new FormData()
      params.append('deltaTime', this.deltaTime * 60 * 60)
      params.append('fileName', this.filename)
      /* if(this.featuretype === '每日休息时长'){
        params.append('featureType', 3)
      } */
      if (this.targettype === 'IP') {
        params.append('viewObject', 0)
      }
      if (this.targettype === 'Account') {
        params.append('viewObject', 1)
      }
      params.append('viewTarget', (this.selectedtarget))
      params.append('beginTime', this.starttime)
      console.log('-------------', this.starttime)
      var str_tmp = this.endtime.split(" ")[0] + " 23:59:59"
      params.append('endTime', str_tmp)
      console.log(str_tmp)

      api.getRestData(params).then(data => {
        this.lineData = data.lineData
        this.boxData = data.boxData
        console.log(this.lineData)
        // 2.准备option
        this.lineOption = utils.getLineOption(this.featuretype, this.windowtype,
          this.lineData, this.scale, this.selected,
          this.beginTimeStr, this.endTimeStr)

        // 3.获取实例，画图
        var t2 = new Date()
        var myChart_rest = this.$echarts.init(document.getElementById('rest'));
        myChart_rest.clear()
        console.log('初始化echarts实例,')

        myChart_rest.setOption(this.lineOption);
        // var that = this
        // myChart_rest.on('datazoom', function (params) {
        //   // console.log(params);//里面存有代表滑动条的起始的数字
        //   var start = myChart_rest.getModel().option.dataZoom[0].start;//获取axis
        //   var end = myChart_rest.getModel().option.dataZoom[0].end;//获取axis
        //   that.scale = [start, end]
        //   //that.lineOption = api.getLineOption()
        //   console.log('this.scale', that.scale)
        //   that.rechart++
        //   that.lineOption = utils.getLineOption(that.featuretype, that.windowtype,
        //     that.lineData, that.scale, that.selected,
        //     that.beginTimeStr, that.endTimeStr)
        //   myChart_rest.setOption(that.lineOption)
        // })
        // myChart_rest.on('legendselectchanged', function (params) {
        //   // console.log(params.selected)
        //   that.selected = params.selected
        //   that.rechart++
        // })

        var t3 = new Date()
        this.getRestParam();
      })
        .catch(function (error) {
          console.log(error);
        })

    },
    getRestParam: function () {
      let params = new FormData()
      params.append('fileName', this.filename)
      if (this.targettype === 'IP') {
        params.append('viewObject', 0)
      }
      if (this.targettype === 'Account') {
        params.append('viewObject', 1)
      }
      api.getRestParams(params).then(data => {
        if (data.data.deltaTime == 1) {
          this.message = '无封禁状态，难以推测服务器封禁原因，建议延长每日工作时间。'
        }
        else {
          this.newParams = data.data
        }
      })

        .catch(function (error) {
          console.log(error);
        })
    },
    getRest: function () {
      this.drawLine();
    },
    changeFile (e) {
      var _this = this
      _this.targettype = ''
      _this.selectedtarget = []

      var time1 = '';
      var time2 = '';
      for (var item of this.metainfos) {
        if (item.filename === this.filename) {
          time1 = item.beginTimeStr.split(' ')[0].replace(/-/g, '/')
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
      var date1 = new Date(time1);  //开始时间  
      var date2 = new Date(time2);
      console.log(date1, date2)
      var time1Sec = date1.getTime();
      var time2Sec = date2.getTime();
      console.log(time1Sec, time2Sec);
      this.pickerOptions = {
        disabledDate: (time) => {
          // console.log(time.getTime())
          if ((time.getTime() >= time1Sec) && (time.getTime() <= time2Sec)) {
            return false
          }
          else {
            return true
          };
        }
      }
    },
    changeMethods (e) {
      var _this = this
      _this.selectedtarget = []
      if (_this.targettype == 'IP') {
        for (var item of _this.metainfos) {
          if (item['filename'] === _this.filename) {
            _this.targets = []
            for (var ip in item['ipDetail']) {
              _this.targets.push(ip)
            }
          }
        }
      }
      if (_this.targettype == 'Account') {
        for (var item of _this.metainfos) {
          if (item['filename'] === _this.filename) {
            _this.targets = []
            for (var account in item['accountDetail']) {
              _this.targets.push(account)
            }
          }
        }
      }
    },
    changeStarttime (e) {
    },
    changeEndtime (e) {
      console.log(this.endtime)
    },
    applyRest: function () {
      this.deltaTime = (this.newParams.newDeltaTimeWindow / 3600).toFixed(0)
    },
  },
}
</script>

<style scoped>
.el-button {
  background-color: #3679fa
}
</style>