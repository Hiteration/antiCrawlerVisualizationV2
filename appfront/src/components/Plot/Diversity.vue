<template>
  <div>
    <el-row :span="24" align='middle'>
      <el-col :span="5">
        <el-form ref="form" label-width="100px" size="mini">
          <el-form-item label="画图窗口:">
            <el-select v-model="windowtype" @change="windowselected" placeholder="请选择画图窗口">
              <el-option label="时间窗口" value="时间窗口"></el-option>
              <el-option label="次数窗口" value="次数窗口"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="窗口大小:">
            <el-input v-model="windowsize" style="margin-right: 100px;">
              <i slot="suffix" style="font-style:normal;margin-right: 10px;">{{text}}</i>
            </el-input>

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
            <el-select v-model="selectedtarget" multiple collapse-tags style="margin-left: 0px;" placeholder="请选择">
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
            <el-button type="primary" @click="gtDiversity">开始画图</el-button>
            <!-- <el-button>重置</el-button> -->
          </el-form-item>

        </el-form>
        <el-card class="box-card" :span="5">
          <!-- <div slot="header" class="clearfix">
                  <span>推荐的窗口参数</span>
                </div> -->

          <div v-if="newParams.windowType > -1">{{message}}>
            <p>建议的时间窗口：{{(newParams.newTimeWindow / 60).toFixed(2)}}分钟
              <!-- ,推测封禁阈值的下界为{{newParams.newTimeBan}} 次 -->
              <el-button @click="applyTime" style="float: right; padding: 3px 0" type="text">应用</el-button>
            </p>
            <p>建议的次数窗口: {{newParams.newNumberWindow}}次
              <!-- ,推测的封禁阈值上界为{{(newParams.newNumberBan / 60).toFixed(2)}}分钟 -->
              <el-button @click="applyNumber" style="float: right; padding: 3px 0" type="text">应用</el-button>
            </p>
            <p>推荐使用{{newType}}</p>
          </div>
          <div else>{{message}}</div>
        </el-card>
        <el-card class="box-card" :span="5">
          <!-- <div slot="header" class="clearfix">
                  <span>推荐的窗口参数</span>
                </div> -->
          <div v-if="newType == '时间窗口'">
            <p>推测的封禁原因为：{{(newParams.newTimeWindow / 60).toFixed(2)}}分钟内,访问资源种类数未超过{{newParams.newTimeBan}}次;在所有访问资源种类数达到{{newParams.newTimeBan}}的访问记录中，有{{(newParams.newNumberMix*100).toFixed(2)}}%的访问被封禁。
            </p>
          </div>
          <div v-if="newType == '次数窗口'">
            <p>推测的封禁原因为：{{(newParams.newNumberWindow)}}次访问中，访问的资源种类数未超过{{newParams.newNumberBan}};在所有访问资源种类数达到{{newParams.newNumberBan}}的访问记录中，有{{(newParams.newNumberMix*100).toFixed(2)}}%的访问被封禁。
            </p>
          </div>
        </el-card>
      </el-col>

      <el-col :span="19">
        <div id="diversity" style="width: 1000px;height:500px;"></div>
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
      filename: '',
      files: [],
      featuretype: '多样性',
      targettype: '',
      targettypes: ['IP', 'Account'],
      selectedtarget: [],
      targets: [],
      windowtype: '',
      windowtypes: ['时间窗口', '次数窗口'],
      timerange: [],
      starttime: '',
      endtime: '',
      text: '',
      windowsize: '',
      scale: [0, 100],
      selected: 'all',

      newParams: '',
      newType: '',
      message: '',

      lineData_number: [],
      lineOption: '',
      scale: [0, 100],
      selected: 'all',
      beginTimeStr: '',
      endTimeStr: '',

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
      params.append('fileName', this.filename)
      if (this.featuretype === '频率') {
        params.append('featureType', 0)
      }
      if (this.windowtype === '时间窗口') {
        params.append('windowsType', 0)
        params.append('windowsSize', this.windowsize * 60)
      }
      if (this.windowtype === '次数窗口') {
        params.append('windowsType', 1)
        params.append('windowsSize', this.windowsize)
      }
      if (this.targettype === 'IP') {
        params.append('viewObject', 0)
      }
      if (this.targettype === 'Account') {
        params.append('viewObject', 1)
      }
      params.append('viewTarget', (this.selectedtarget))
      params.append('beginTime', this.starttime)
      var str_tmp = this.endtime.split(" ")[0] + " 23:59:59"
      params.append('endTime', str_tmp)
      console.log(str_tmp)

      api.getDiversityData(params).then(data => {
        this.lineData_number = data.lineData_number
        console.log('lineData', this.lineData_number)
        // 2.准备option
        this.lineOption = utils.getLineOption(this.featuretype, this.windowtype,
          this.lineData_number, this.scale, this.selected,
          this.beginTimeStr, this.endTimeStr)
        console.log(this.lineOption)
        // 3.获取实例，画图
        var t2 = new Date()
        var myChart_diversity = this.$echarts.init(document.getElementById('diversity'));
        myChart_diversity.clear()
        console.log('初始化echarts实例,')

        myChart_diversity.setOption(this.lineOption);
        var that = this
        myChart_diversity.on('datazoom', function (params) {
          // console.log(params);//里面存有代表滑动条的起始的数字
          var start = myChart_diversity.getModel().option.dataZoom[0].start;//获取axis
          var end = myChart_diversity.getModel().option.dataZoom[0].end;//获取axis
          that.scale = [start, end]
          //that.lineOption = api.getLineOption()
          console.log('this.scale', that.scale)
          that.rechart++
          that.lineOption = utils.getLineOption(that.featuretype, that.windowtype,
            that.lineData_number, that.scale, that.selected,
            that.beginTimeStr, that.endTimeStr)
          myChart_diversity.setOption(that.lineOption)
        })
        myChart_diversity.on('legendselectchanged', function (params) {
          // console.log(params.selected)
          that.selected = params.selected
          that.rechart++
        })

        var t3 = new Date()
        this.getDiversityParam();
      })
        .catch(function (error) {
          console.log(error);
        })

    },
    getDiversityParam: function () {
      let params = new FormData()
      params.append('fileName', this.filename)
      if (this.featuretype === '频率') {
        params.append('featureType', 0)
      }
      if (this.targettype === 'IP') {
        params.append('viewObject', 0)
      }
      if (this.targettype === 'Account') {
        params.append('viewObject', 1)
      }

      params.append('beginTime', this.starttime)
      params.append('endTime', this.endtime)

      api.getDiversityParams(params).then(data => {

        this.newParams = data.data
        if (this.newParams.windowType == -1) {
          this.message = '无封禁状态，难以推测服务器封禁原因，建议集中访问某类接口以探测服务器封禁阈值。'
        }
        else {
          if (this.newParams.newNumberMix > this.newParams.newTimeMix) {
            this.newType = "次数窗口"
          }
          else {
            this.newType = "时间窗口"
          }
        }

      })
        .catch(function (error) {
          console.log(error);
        })
    },
    gtDiversity: function () {
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
    windowselected (e) {
      var _this = this
      _this.windowsize = ''
      if (_this.windowtype == '时间窗口') {
        _this.text = '分钟'
      }
      else {
        _this.text = '次'
      }
    },
    changeStarttime (e) {
    },
    changeEndtime (e) {
      console.log(this.endtime)
    },
    applyTime: function () {
      this.windowtype = "时间窗口"
      this.windowsize = this.newParams.newTimeWindow
      this.text = "分钟"
    },
    applyNumber: function () {
      this.windowtype = "次数窗口"
      this.windowsize = this.newParams.newNumberWindow
      this.text = "次"
    },
  },
}

</script>

<style>
</style>