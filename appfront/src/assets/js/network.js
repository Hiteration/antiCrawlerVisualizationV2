import axios from 'axios'


// 封装自己的get/post方法
export default {
  get: function (path = '', data = {}) {
    return new Promise(function (resolve, reject) {
      axios.get(path, {
        params: data
      })
        .then(function (response) {
          // 返回response.data，一般直接返回response
          // console.log(response)
          resolve(response);
        })
        .catch(function (error) {
          reject(error);
        });
    });
  },
  post: function (path = '', data = {}) {
    return new Promise(function (resolve, reject) {
      axios.post(path, data)
        .then(function (response) {
          resolve(response);
        })
        .catch(function (error) {
          reject(error);
        });
    });
  }
};