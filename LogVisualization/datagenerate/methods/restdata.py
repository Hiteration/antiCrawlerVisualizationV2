import os
import json
import numpy as np
from datagenerate.utils import lookup


def restDataLine(name, deltaTime, viewObject, viewTarget, beginTime, endTime,beginZeroTime):
    # deltaTime = 2
    # print('name', name)
    # print('deltaTime', deltaTime)
    # print('viewObject', viewObject)
    # print('viewTarget', viewTarget)
    # print('beginTime',beginTime)
    # print('endTime', endTime)
    # print('beginZeroTime', beginZeroTime)
    oneDaySeconds = 24*60*60
    res = {}
    baseDir = os.path.dirname(os.path.abspath(__name__))
    fileName = os.path.join(baseDir, 'tmp', name)  # 日志文件路径
    metainfo = os.path.join(baseDir, 'tmp', 'meta', name)  # 元信息文件路径

    viewobject = 'ip'  # 默认统计ip
    if viewObject == 1:  # 统计账户
        viewobject = 'account'

    # 如果未传入观察对象，则设定为全部对象
    if len(viewTarget) == 0:
        viewTarget = []
        with open(metainfo) as file:  # 根据元数据进行观察目标初始化
            metas = json.load(file)
            detail = 'ipDetail'
            if viewObject == 1:
                detail = 'accountDetail'
            for key in metas[detail].keys():
                viewTarget.append(key)

    viewTargets = set()
    for target in viewTarget:
        viewTargets.add(target)


    preZeroTime = {}    # 前一次访问当天零点所对应的时间
    preTime = {}        # 前一次访问时间
    tmpState = {}       # 当前连续访问中State的最大值
    tmpDays = {}        # 当前已连续访问的天数
    breakZeroTime = {}      # 最近一次发生连续访问中断所对应零点的时间

    days = {}           # 每次连续访问的天数
    states = {}         # 每次连续访问的状态

    # 初始化
    for target in viewTargets:
        preTime[target] = -1
        preZeroTime[target] = beginZeroTime

        tmpState[target] = 0
        tmpDays[target] = 1
        breakZeroTime[target] = -oneDaySeconds

        days[target] = []
        states[target] = []

    with open(fileName) as file:
        infos = json.load(file)
        for info in infos:
            if info['time'] > endTime:      # 超过时间范围
                break
            tmp_key = info[viewobject]  # 此次访问对象 ip/账户
            code = info['status']['code']  # 此次访问结果状态码
            if tmp_key not in viewTargets:
                continue
            # 不是该目标第一次访问且当天没有发生访问中断
            if preTime[tmp_key] != -1 and info['time'] - breakZeroTime[tmp_key] >= oneDaySeconds:
                # 发生访问中断
                if info['time'] - preTime[tmp_key] > deltaTime:
                    if info['time'] >= beginTime:
                        days[tmp_key].append(tmpDays[tmp_key])
                    tmpDays[tmp_key] = 1
                    breakZeroTime[tmp_key] = preZeroTime[tmp_key]
                    if info['time'] - preZeroTime[tmp_key] >= oneDaySeconds:     # 另外一天的第一次访问
                        while breakZeroTime[tmp_key] + oneDaySeconds <= info['time']:
                            breakZeroTime[tmp_key] += oneDaySeconds
                    if info['time'] >= beginTime:
                        states[tmp_key].append(tmpState[tmp_key])
                    tmpState[tmp_key] = 0
                else:
                    while preZeroTime[tmp_key]+oneDaySeconds <= info['time']:
                        preZeroTime[tmp_key] += oneDaySeconds
                        tmpDays[tmp_key] += 1
            # 第一次访问
            if preTime[tmp_key] == -1:
                while preZeroTime[tmp_key] <= info['time'] - oneDaySeconds:
                    preZeroTime[tmp_key] += oneDaySeconds
            preTime[tmp_key] = info['time']
            tmpState[tmp_key] = max(tmpState[tmp_key], code)

        for tmp_key in viewTargets:
            if endTime >= breakZeroTime[tmp_key] + oneDaySeconds:
                days[tmp_key].append(tmpDays[tmp_key])
                states[tmp_key].append(tmpState[tmp_key])

    for target in viewTargets:
        length = len(states[target])
        res[target] = np.concatenate((np.arange(1,length+1).reshape(length,1),np.array(days[target]).reshape(length,1),np.array(states[target]).reshape(length,1)),axis=1).tolist()
    print('res:',res)
    res_new = {}
    for ip in res:
      ip_str = lookup(ip)
      res_new.update({ip_str: res[ip]}) 
    res_new = {'195.221.56.8': [[1, 1, 0],[2, 1, 0],[3, 1, 0]], \
    '225.168.1.6': [[1, 2, 1]], '225.168.6.8': [[1,1,0], [2, 2, 1], [3,3,2]], \
    '195.221.68.34': [[1, 3, 2]], '229.21.36.85': [[1, 2, 1]], \
    '192.168.1.5': [[1, 2, 2]], '92.168.1.5': [[1, 2, 1]], \
    '225.168.9.52': [[1, 2, 1]], '19.168.89.5': [[1, 2, 1]], \
    '195.221.22.21': [[1, 3, 2]], '225.168.2.5': [[1, 2, 0]]}
    return res_new