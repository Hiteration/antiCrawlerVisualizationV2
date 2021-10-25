import os
import json
import datetime
from datagenerate.utils import lookup


def parse_ymd(s):
    date = s.split(' ')[0]
    time = s.split(' ')[1].split('.')[0]
    year_s, mon_s, day_s = date.split('-')
    hour_s, min_s, sec_s = time.split(':')

    return datetime.datetime(int(year_s), int(mon_s), int(day_s), int(hour_s), int(min_s), int(sec_s))


def getSteplineData(name, time):
    baseDir = os.path.dirname(os.path.abspath(__name__))
    fileName = os.path.join(baseDir, 'tmp', name)

    rst = {}
    
    with open(fileName) as file:
        infos = json.load(file)  # 加载日志信息
    for info in infos:
        # print(info)
        if(info['ip'] not in rst.keys()):
            # starttime = info['timeStr']
            rst[info['ip']] = [[info['timeStr'], 1, info['status']['code'], info['time']]]
        else:
            x_idx = int((info['time'] - rst[info['ip']][0][3]) / time)
            if(x_idx < len(rst[info['ip']]) and \
                rst[info['ip']][x_idx][2] == info['status']['code']): continue
            elif(x_idx < len(rst[info['ip']]) and \
                rst[info['ip']][x_idx][2] != info['status']['code'] and \
                (info['status']['code'] == 1 or info['status']['code'] == 2)):
                rst[info['ip']][x_idx][2] = info['status']['code']
            else:
                while(x_idx >= len(rst[info['ip']])):
                    i = len(rst[info['ip']])    
                    num = i*time + rst[info['ip']][0][3]
                    time_str = datetime.datetime.strptime(rst[info['ip']][0][0],'%Y-%m-%d %H:%M:%S') + \
                        datetime.timedelta(minutes=int(i*time / 60) + 1)
                    rst[info['ip']].append([time_str.strftime("%Y-%m-%d %H:%M:%S"), 0, num])
                # rst[info['ip']].append([time_str.strftime("%Y-%m-%d %H:%M:%S"), 0, num])
                rst[info['ip']][x_idx][1] = 1
    res_new = {}
    for ip in rst:
      ip_str = lookup(ip)
      res_new.update({ip_str: rst[ip]}) 
    return res_new


if(__name__ == "__main__"):
    ss = parse_ymd('2020-12-24 18:16:20.145')
    print(type(ss))
    # print(getSteplineData('log_Twitter.json', 24*60*60))
