// 导入封装好的网络请求类工具
import Network from './network';

// 封装各种接口请求
// export const 接口名 = () => Network.get('/路由',参数对象);

//获取元信息
export const getMetaInfo = () => Network.get('http://127.0.0.1:8000/filemanager/getmetainfo');

//获取频率特征数据
export const getFrequencyData = (params) => Network.post('http://127.0.0.1:8000/datagenerate/frequencydata', params)
  .then(data => {
    console.log("frequencydata返回的data.data.lineData: ", data.data.lineData)
    var freList = data.data.lineData
    var linedata = {} //生成更好格式的linedata
    for (const item in freList) {
      if (!(item in linedata)) {linedata[item] = []}
      for (const subitem of freList[item]) {
        for (const subsubitem of subitem) { //subsubitem是三元组
          linedata[item].push(subsubitem)
        }
      }
    }
    return { "lineData": linedata, "boxdData": data.data.boxdData }
  })
//获取频率特征自动化参数
export const getFrequencyParams = (params) => Network.post('http://127.0.0.1:8000/paramsgenerate/frequencyparams', params)

//获取连续在线时长特征数据
export const getOnlinetimeData = (params) => Network.post('http://127.0.0.1:8000/datagenerate/onlinetimedata', params)
  .then(data => {
    // console.log(data.data.lineData)
    var feaList = data.data.lineData
    var linedata = {}
    for (var ip in feaList) {
      if (!(ip in linedata)) { linedata[ip] = [] }
      for (var item of feaList[ip]) {
        for (var item_3tuples of item) {
          linedata[ip].push(item_3tuples)
        }
      }
    }
    return { "lineData": linedata, "boxdData": data.data.boxdData }
  })
export const getOnlinetimeParams = (params) => Network.post('http://127.0.0.1:8000/paramsgenerate/onlinetimeparams', params)

//获取间隔特征数据
export const getIntervalData = (params) => Network.post('http://127.0.0.1:8000/datagenerate/intervaldata', params)
  .then(data => {
    // console.log(data.data.lineData)
    var feaList = data.data.lineData
    var linedata = {}
    for (var ip in feaList) {
      if (!(ip in linedata)) { linedata[ip] = [] }
      for (var item of feaList[ip]) {
        for (var item_3tuples of item) {
          // linedata[ip].push([item_3tuples[0], Number(item_3tuples[1]), Number(item_3tuples[2])])
          linedata[ip].push(item_3tuples)
        }
      }
    }
    console.log(linedata)
    return { "lineData": linedata, "boxdData": data.data.boxdData }
  })
export const getIntervalParams = (params) => Network.post('http://127.0.0.1:8000/paramsgenerate/intervalparams', params)

//获取每日休息时长特征数据
export const getRestData = (params) => Network.post('http://127.0.0.1:8000/datagenerate/restdata', params)
  .then(data => {
    // console.log(data.data.lineData)
    var feaList = data.data.lineData
    var linedata = {}
    for (var ip in feaList) {
      if (!(ip in linedata)) { linedata[ip] = [] }
      for (var idx = 0; idx < feaList[ip].length; idx++) {
        if (idx > 0 && feaList[ip][idx][2] == 2 && feaList[ip][idx][2] == feaList[ip][idx - 1][2]) {
          continue
        }
        else {
          linedata[ip].push(feaList[ip][idx])
        }
      }
    }
    console.log('--+++++++++++++', linedata)
    return { "lineData": linedata, "boxdData": data.data.boxdData }
  })
export const getRestParams = (params) => Network.post('http://127.0.0.1:8000/paramsgenerate/restparams', params)

//获取多样性特征数据
export const getDiversityData = (params) => Network.post('http://127.0.0.1:8000/datagenerate/diversitydata', params)
  .then(data => {
    // console.log(data.data.lineData)
    var feaList = data.data.lineData_number
    var linedata = {}
    for (var ip in feaList) {
      if (!(ip in linedata)) { linedata[ip] = [] }
      for (var item of feaList[ip]) {
        for (var item_3tuples of item) {
          linedata[ip].push(item_3tuples)
        }
      }
    }
    return { "lineData_number": linedata, "boxdData_number": data.data.boxdData }
  })
//获取多样性参数
export const getDiversityParams = (params) => Network.post('http://127.0.0.1:8000/paramsgenerate/diversityparams', params)

//获取周期性特征数据
export const getPeriodismData = (params) => Network.post('http://127.0.0.1:8000/datagenerate/periodismdata', params)
  .then(data => {
    // console.log(data.data.lineData)
    var feaList = data.data.lineData
    var linedata = {}
    for (var ip in feaList) {
      if (!(ip in linedata)) { linedata[ip] = [] }
      for (var item of feaList[ip]) {
        for (var item_3tuples of item) {
          linedata[ip].push(item_3tuples)
        }
      }
    }
    return { "lineData_number": linedata, "boxdData_number": data.data.boxdData }
  })
export const getPeriodismParams = (params) => Network.post('http://127.0.0.1:8000/paramsgenerate/periodismparams', params)


// export const getSteplineData = (params) => Network.post('http://127.0.0.1:8000/datagenerate/steplinedata', params)
//   .then(data => {
//     return { "setplineData": data.data }
//   })


//多变量观察
export const getFrequencyPoints = (params) => Network.post('http://127.0.0.1:8000/pointsgenerate/frequencypoints', params)
  .then(data => {
    // console.log(data.data.lineData)
    // console.log(data.data)
    return { "frequency_points": data.data }
  })
export const getIntervalPoints = (params) => Network.post('http://127.0.0.1:8000/pointsgenerate/intervalpoints', params)
  .then(data => {
    // console.log(data.data.lineData)
    // console.log(data.data)
    return { "interval_points": data.data }
  })
export const getRestPoints = (params) => Network.post('http://127.0.0.1:8000/pointsgenerate/restpoints', params)
  .then(data => {
    // console.log(data.data.lineData)
    // console.log(data.data)
    return { "rest_points": data.data }
  })
export const getDiversityPoints = (params) => Network.post('http://127.0.0.1:8000/pointsgenerate/diversitypoints', params)
  .then(data => {
    // console.log(data.data.lineData)
    // console.log(data.data)
    return { "diversity_points": data.data }
  })

//多变量观察可视化数据
export const getPointsParams = (params) => Network.post('http://127.0.0.1:8000/pointsgenerate/paramsdata', params)
  .then(data => {
    return { "infos": data.data }
  })