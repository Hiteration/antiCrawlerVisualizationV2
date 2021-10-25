import requests

ip_to_location = {'8.209.221.177': 'Japan', '173.82.200.74':'United States', \
  '104.149.140.226':'United States', '148.163.89.2': 'United States',\
  '104.149.232.21':'United States', '104.149.146.250':'United States',\
  '173.82.28.170':'United States','23.226.71.58':'United States', \
  '192.240.118.2':'United States'}

# 获取ip地址对应地区
def lookup(ip):
  if(ip in ip_to_location.keys()):
    # 手动配置代理ip地址
    return ip + ',' + ip_to_location[ip]
    URL = 'http://ip-api.com/json/' + ip
    # try:
    r = requests.get(URL, timeout=500)
    r_json = r.json()
    # except requests.RequestException as e:
    #   print(e)
    print(ip)
    print('所在国家：' + r_json['country'])
    print('所在地区：' + r_json['regionName'])
    return(ip + ',' + r_json['country'] + ',' + r_json['regionName'])
  else:
    return ip
