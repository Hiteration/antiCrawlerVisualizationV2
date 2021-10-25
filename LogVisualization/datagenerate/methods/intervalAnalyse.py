import os
import json
import numpy as np
from datagenerate.utils import lookup


# 基于时间间隔的分析
def intervalAnalyseLine(name, windowsType, viewObject, viewTarget, beginTime, endTime, windowsSize):
    res = {}
    baseDir = os.path.dirname(os.path.abspath(__name__))
    # baseDir = 'C:\\Users\\renwei\\Desktop\\日志可视化\\LogVisualization'
    fileName = os.path.join(baseDir, 'tmp', name)
    metainfo = os.path.join(baseDir, 'tmp', 'meta', name)

    viewobject = 'ip'  # 默认统计ip
    if viewObject == 1:  # 统计账户
        viewobject = 'account'

    # 如果未传入观察对象，则设定为全部对象
    if len(viewTarget) == 0:
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

    if windowsType == 0:  # 使用的是时间窗口

        tmp = {}  # 节点历史访问时间
        timeStr = {}  # 每次访问的格式化时间
        intervals = {}  # 每次访问与前一次的时间间隔
        preTimes = {}  # 前一次访问的时间
        state = {}  # 每次访问的状态 0表示通过 1表示怀疑 2表示封禁
        flag = {}  # 记录tmp中是否出现过时间跨度大于windowsSize
        ignore = {}  # 记录每个ip是否处于连续访问封禁中
        stds = {}  # 每次访问时间窗口内时间间隔的标注差

        for key in viewTarget:
            tmp[key] = []
            timeStr[key] = []
            intervals[key] = []
            preTimes[key] = -1
            state[key] = []
            stds[key] = []
            flag[key] = False
            ignore[key] = False

        with open(fileName) as file:
            infos = json.load(file)  # 加载日志信息
            if endTime == -1:  # 如果结束时间没有设置
                endTime = infos[-1]['time']
            for info in infos:
                if info['time'] > endTime:
                    break
                tmp_key = info[viewobject]
                if tmp_key not in viewTargets:
                    continue
                if preTimes[tmp_key] == -1:  # 这个tmp_key第一次访问，所以不存在与前一次的间隔
                    preTimes[tmp_key] = info['time']
                    continue
                tmp[tmp_key].append(info['time'])
                intervals[tmp_key].append(info['time'] - preTimes[tmp_key])
                preTimes[tmp_key] = info['time']
                if info['time'] - windowsSize > tmp[tmp_key][0]:
                    flag[tmp_key] = True
                    while info['time'] - windowsSize > tmp[tmp_key][0]:
                        del tmp[tmp_key][0]
                        del intervals[tmp_key][0]

                if info['time'] >= beginTime:
                    if flag[tmp_key]:
                        code = info['status']['code']  # 得到此次访问的状态码
                        if code >= 0 and code < 3 and not (code == 2 and ignore[info[viewobject]]):
                            timeStr[tmp_key].append(info['timeStr'])
                            stds[tmp_key].append(np.std(np.array(intervals[tmp_key])))

                            if code == 0:
                                ignore[tmp_key] = False
                                state[tmp_key].append(0)
                            elif code == 1:
                                ignore[tmp_key] = False
                                state[tmp_key].append(1)
                            else:
                                ignore[tmp_key] = True
                                state[tmp_key].append(2)
        for key in viewTarget:
            res[key] = {'time': timeStr[key], 'stds': stds[key], 'state': state[key]}

    else:  # 使用的是次数窗口
        tmp = {}  # 节点历史访问时间
        timeStr = {}  # 每次访问的格式化时间
        state = {}  # 每次访问的状态 0表示通过 1表示怀疑 2表示封禁
        ignore = {}
        preTimes = {}
        intervals = {}
        stds = {}  # 每次访问时间窗口内时间间隔的标注差

        for key in viewTarget:
            tmp[key] = []
            timeStr[key] = []
            intervals[key] = []
            preTimes[key] = -1
            state[key] = []
            ignore[key] = False
            stds[key] = []

        with open(fileName) as file:
            infos = json.load(file)  # 加载日志信息
            if endTime == -1:  # 如果结束时间没有设置
                endTime = infos[-1]['time']
            for info in infos:
                if info['time'] > endTime:
                    break
                if info[viewobject] not in viewTargets:
                    continue
                tmp_key = info[viewobject]
                if preTimes[tmp_key] == -1:
                    preTimes[tmp_key] = info['time']
                    continue
                tmp[tmp_key].append(info['time'])
                intervals[tmp_key].append(info['time'] - preTimes[tmp_key])
                preTimes[tmp_key] = info['time']
                if len(tmp[tmp_key]) == windowsSize:
                    if info['time'] >= beginTime:
                        code = info['status']['code']  # 得到此次访问的状态码
                        if code >= 0 and code < 3 and not (code == 2 and ignore[tmp_key]):
                            timeStr[tmp_key].append(info['timeStr'])
                            stds[tmp_key].append(np.std(np.array(intervals[tmp_key])))
                            if code == 0:
                                ignore[tmp_key] = False
                                state[tmp_key].append(0)
                            elif code == 1:
                                ignore[tmp_key] = False
                                state[tmp_key].append(1)
                            else:
                                ignore[tmp_key] = True
                                state[tmp_key].append(2)
                    del tmp[tmp_key][0]

        for key in state.keys():
            res[key] = {'time': timeStr[key], 'stds': stds[key], 'state': state[key]}

    for key in viewTarget:
        tmp = np.concatenate((np.array(res[key]['time']).reshape((-1, 1)), np.array(res[key]['stds']).reshape((-1, 1)),
                              np.array(res[key]['state']).reshape((-1, 1))), axis=1).tolist()
        combine = []

        idx = 0
        for i in range(len(res[key]['time']) + 1):
            if i == len(res[key]['time']) or res[key]['state'][i] == 1:
                k = 1
                if i == len(res[key]['time']):
                    k = 0
                combine.append(tmp[idx:i + k])
                idx = i + 1
        res[key] = combine
    res_new = {}
    for ip in res:
      ip_str = lookup(ip)
      res_new.update({ip_str: res[ip]}) 
    return res_new



