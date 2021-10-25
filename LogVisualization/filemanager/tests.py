from django.test import TestCase

import requests
 
def lookup(ip):
 
  URL = 'http://ip-api.com/json/' + ip
  # try:
  r = requests.get(URL, timeout=500)
  r_json = r.json()
  # except requests.RequestException as e:
  #   print(e)
 
  
  print('所在国家：' + r_json['country'])
  print('所在地区：' + r_json['regionName'])
  return(ip + ',' + r_json['country'] + ',' + r_json['regionName'])
 
ip='8.209.221.177'
address = lookup(ip)
print(address)