import * as api from './api'

export const getRandomArrayValue = (arr, num) => {
  var sData = arr.slice(0), i = arr.length, min = i - num, item, index;
  while (i-- > min) {
    index = Math.floor((i + 1) * Math.random());
    item = sData[index];
    sData[index] = sData[i];
    sData[i] = item;
  }
  return sData.slice(min);
}

export const getLineOption = (featureType, windowType, lineDataOriginal, scale, selected, beginstr, endstr) => {
  var lineData = {}
  console.log(beginstr) //字符串格式时间
  console.log(endstr) //字符串格式时间
  var begin = new Date(beginstr) 
  var end = new Date(endstr)  
  console.log('beginTime', begin) //日期格式时间
  console.log('endTime', end) //日期格式时间
  var beginTime = begin.getTime() //数字格式时间 毫秒为单位
  var endTime = end.getTime() //数字格式时间 毫秒为单位
  var time1 = (endTime - beginTime) * scale[0] / 100
  var time2 = (endTime - beginTime) * scale[1] / 100
  console.log('time1', time1) //数字格式时间 毫秒为单位 相对值
  console.log('time2', time2) //数字格式时间 毫秒为单位 相对值
  var prop = 0.05 //对正常点只选取一部分, prop代表选取百分数
  if (scale[1] - scale[0] < 50) prop = 0.1 //放大提高prop, 展示更多细节
  if (scale[1] - scale[0] < 20) prop = 0.5 //放大提高prop, 展示更多细节
  if (scale[1] - scale[0] < 10) prop = 1 //放大提高prop, 展示更多细节
  for (const item in lineDataOriginal) { //item可能是ip也可能是account
    lineData[item] = []
    for (const subitem of lineDataOriginal[item]) { //subitem是三元组
      if (subitem[2] == 2 || subitem[2] == 3) { //对怀疑和封禁的点 全部都要
        lineData[item].push(subitem)
        continue
      }
      var t = new Date(subitem[0])
      if (t.getTime() - begin.getTime() > time1 && t.getTime() - begin.getTime() < time2) { //对正常点 只按概率取一部分
        if(featureType === '每日休息时长'){
          lineData[item].push(subitem)
        }else{
          if (Math.random() < prop) { //prop是概率
            lineData[item].push(subitem)
          }
        }
      }
    }
  }

  console.log("getLineOption采集后的: ", lineData)

  /**
   * 根据featureType设置坐标轴名称
   */
  var x_type = ''
  var x_name = ''
  var y_name = ''
  switch(featureType){
    case '频率':
      x_type = 'time'
      x_name = '时间'
      if (windowType === '时间窗口') {
        y_name = '访问次数（次）'
      }
      if (windowType === '次数窗口') {
        y_name = '访问耗时（s）'
      }
      break
    case '访问间隔稳定性':
      x_type = 'time'
      x_name = '时间'
      y_name = '访问间隔标准差（s）'
      break
    case '每日休息时长':
      x_type = 'category'
      x_name = '次数'
      y_name = '连续无休工作天数'
      lineData = lineDataOriginal
      break
    case '多样性':
      x_type = 'time'
      x_name = '时间'
      y_name = '种类数'
      break
    case '周期性':
      x_type = 'time'
      x_name = '时间'
      y_name = '子序列重复次数'
      break
  }
  //准备option
  var titlename = '';
  var legendlist = [];
  var seriesdata = [];
  for (var item in lineData) {
    legendlist.push(item)
  }
  for (var legendname of legendlist) {
    console.log("开始生成series...")
    seriesdata.push({
      name: legendname,
      type: 'line',
      data: lineData[legendname],
      symbol: function (params) { 
        if (params[2] == 1) return 'pin'
        if (params[2] == 2) return 'circle'
      },
      // data: [[1, 2, 0], [2, 3, 0], [4, 6, 1]],
      symbolSize: function (params) {    //params对应data里一个数据点的值, 这里是一个含有三个数字的一维数组
        if (params[2] == 1) return 0
        if (params[2] == 2) return 8
        if (params[2] == 3) return 10
      },
    })
  }
  var option = {
    title: {
      show: true,
      text: titlename,
      textStyle: {
        fontStyle: 'normal', //风格
        fontWeight: 'normal',  //粗细
        fontFamily: 'Microsoft yahei', //字体
        fontSize: 14, //大小
        align: 'center' //水平对齐
      },
    },
    grid: {
      right: 150, //图的右边距
    },
    legend: {
      selectedMode: 'multiple', //默认选择多组数据
      orient: 'vertical', //垂直排列
      width: 150,
      right: 0,
      top: 50,
      data: legendlist, //数据来源
    },
    xAxis: [{
      type: x_type, // 根据x轴数据决定type类型
      boundaryGap: false, //左右边距：无
      name: x_name, //坐标轴名称
      // 注： x轴不指定data, 自动会从series取
      spiltLine: {
        show: false,  //想要不显示网格线, 改为false
      }
    }],
    yAxis: {
      type: 'value',
      name: y_name,
      spiltLine: {
        show: false,  //想要不显示网格线, 改为false
      }
    },
    dataZoom: [
      {
        type: "slider",//缩放通过外部滑动块
        show: true,
        xAxisIndex: [0],//表示x轴折叠
        start: scale[0],//数据窗口范围的起始百分比
        end: scale[1],//数据窗口范围的结束百分比
        realtime: false
      },
      {
        type: "inside",//缩放通过内置于坐标系中
        // yAxisIndex: [0],//表示y轴折叠
        // start: 0,
        // end: 100
      },
    ],
    tooltip: {
      trigger: "item", //鼠标放到点上会显示详细信息
      axisPointer: { //鼠标放在图里会显示虚线
        type: 'cross'
      },
    },
    series: seriesdata, //数据来源
  }
  if (selected !== 'all') { 
    option.legend.selected = selected //显示哪些数据
  }

  return option
}

export const getmultpleOption = (x_value, y_value, x_name, y_name) => {
  // var x_name = ''
  // if(x_feature == '访问频率'){
  //   if(x_windowtype == '次数'){
  //     x_name = '秒/500次'
  //   }
  // }
  var legendlist = []
  for (var ip in x_value) {
    legendlist.push(ip)
  }
  var seriesdata = []
  console.log(legendlist)
  console.log(x_value)
  for (var legendname of legendlist) {
    console.log("开始生成series...")
    console.log(x_value)
    console.log(y_value)
    seriesdata.push({
      name: legendname,
      type: 'line',
      data: [[x_value[legendname][0], y_value[legendname][0], x_value[legendname][1]]],
      // data: [[1, 2, 0],  [2, 3, 0], [4, 6, 1]],
      symbolSize: function (params) {    //params对应data里一个数据点的值, 这里是一个含有三个数字的一维数组
        if (params[2] == 0) return 5
        if (params[2] == 1) return 10
        if (params[2] == 2) return 20
      },
    })
  }
  var option = {
    grid: {
      right: 150,
      /* width: '100%',
      height: '100%', */
    },
    legend: {
      selectedMode: 'multiple',
      orient: 'vertical',
      width: 150,
      right: 0,
      top: 50,
      data: legendlist,
    },
    xAxis: {
      // 根据x轴数据决定type类型
      type: 'value',
      boundaryGap: false,
      name: x_name,
      // 注： x轴不指定data,自动会从series取
    },
    yAxis: {
      type: 'value',
      name: y_name,
    },
    dataZoom: [
      {
        type: "slider",//slider表示有滑动块的，
        show: true,
        xAxisIndex: [0],//表示x轴折叠
        // start:1,//数据窗口范围的起始百分比,表示1%
        // end:35//数据窗口范围的结束百分比,表示35%坐标
      },
      {
        type: "inside",//           
        // yAxisIndex:[0],//表示y轴折叠
        // start:1,
        // end:35
      },
    ],
    tooltip: {
      trigger: "item",
      axisPointer: {
        type: 'cross'
      },
      /* formatter(params){
        for(x in params){
          let firstP = params[x].name
          let secondP = params[x].
          return params[x].name +":"+params[x].data.value+"/"+params[x].data.date;
        }
      } */
    },
    series: seriesdata
  }
  return option
}

export const getPoints = (type, params) => {
  if (type === '访问频率') {
    return new Promise(function (resolve, reject) {
      api.getFrequencyPoints(params)
        .then(data => {
          resolve(data.frequency_points)
        })
    })
  }
  if (type === '访问间隔稳定性') {
    return new Promise(function (resolve, reject) {
      api.getIntervalPoints(params)
        .then(data => {
          resolve(data.interval_points)
        })
    })
  }
  if (type === '每日休息时长') {
    return new Promise(function (resolve, reject) {
      api.getRestPoints(params)
        .then(data => {
          resolve(data.rest_points)
        })
    })
  }
  if (type === '访问资源多样性') {
    return new Promise(function (resolve, reject) {
      api.getDiversityPoints(params)
        .then(data => {
          resolve(data.diversity_points)
        })
    })
  }
}

export const getSteplineOption = (chartList) => {
  var chartOptions = {}
  for (var titlename in chartList) {
    var option = {
      // title: {
      //   show:true,
      //     text: titlename,
      //     textStyle:{
      //       fontStyle:'normal',     //风格
      //       fontWeight:'normal',    //粗细
      //       fontFamily:'Microsoft yahei',   //字体
      //       fontSize:14,     //大小
      //       align:'center'   //水平对齐
      //     },
      // },
      xAxis: {
        // 根据x轴数据决定type类型
        type: 'category',
        boundaryGap: false,
      },
      yAxis: {
        type: 'value',
      },
      legend: {
        data: [titlename],
      },
      // dataZoom:[
      //   {
      //       type:"slider",//slider表示有滑动块的，
      //       show:true,
      //       xAxisIndex:[0],//表示x轴折叠
      //       // start:1,//数据窗口范围的起始百分比,表示1%
      //       // end:35//数据窗口范围的结束百分比,表示35%坐标
      //   },
      //   {
      //     type:"inside",//           
      //     // yAxisIndex:[0],//表示y轴折叠
      //     // start:1,
      //     // end:35
      //   },
      // ],
      series: [{
        name: titlename,
        type: 'line',
        step: 'middle',
        data: chartList[titlename],
        // data: [[1, 2, 0],  [2, 3, 0], [4, 6, 1]],
        symbolSize: function (params) {    //params是一个数据点的值, 这里是一个含有三个数字的一维数组
          if (params[2] == 0) return 5
          if (params[2] == 1) return 10
          if (params[2] == 2) return 20
        },
      }]
    }
    chartOptions[titlename] = option
  }
  return chartOptions
}