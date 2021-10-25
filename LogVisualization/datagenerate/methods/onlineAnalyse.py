import os
import json
import numpy as np


# 基于时间间隔的分析
def onlineAnalyseLine(name, deltaTime, viewObject, viewTarget, beginTime, endTime):
    res = {}
    baseDir = os.path.dirname(os.path.abspath(__name__))
    fileName = os.path.join(baseDir, 'tmp', name)  # 日志文件路径
    metainfo = os.path.join(baseDir, 'tmp', 'meta', name)  # 元信息文件路径

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

    timeAcculate = {}  # 每个观察对象上一个访问时连续在线时长
    preAccess = {}  # 每个观察对象上一次的访问时间
    preState = {}  # 上一次访问的状态

    onlineTime = {}  # 每次访问时连续在线时长
    state = {}  # 每次访问的结果
    timeStr = {}  # 观察目标每次访问的时间

    for target in viewTarget:
        timeAcculate[target] = 0
        preAccess[target] = -1
        onlineTime[target] = []
        state[target] = []
        preState[target] = 0
        timeStr[target] = []

    with open(fileName) as file:
        infos = json.load(file)
        for info in infos:
            if info['time'] > endTime:
                break
            tmp_key = info[viewobject]  # 此次访问对象 ip/账户
            code = info['status']['code']  # 此次访问结果状态码
            if tmp_key not in viewTargets:
                continue
            if preAccess[tmp_key] == -1:  # 此对象第一次访问
                preAccess[tmp_key] = info['time']
                preState[tmp_key] = code
                continue
            # print(info['time'], preAccess[tmp_key], type(deltaTime))
            if info['time'] - preAccess[tmp_key] > float(deltaTime):  # 中途下线了
                timeAcculate[tmp_key] = 0
            else:
                timeAcculate[tmp_key] += (info['time'] - preAccess[tmp_key])
            if code == 1:
                if preState[tmp_key] == 1:  # 不是第一次封禁
                    preAccess[tmp_key] = info['time']
                    continue
            preState[tmp_key] = code
            preAccess[tmp_key] = info['time']
            if info['time'] < beginTime:  # 为进入观察范围
                continue
            onlineTime[tmp_key].append(timeAcculate[tmp_key])
            timeStr[tmp_key].append(info['timeStr'])
            state[tmp_key].append(code)

    for key in viewTarget:
        res[key] = {'time': timeStr[key], 'feature': timeAcculate[key], 'state': state[key]}

    for key in viewTarget:
        tmp = np.concatenate(
            (np.array(res[key]['time']).reshape((-1, 1)), np.array(res[key]['feature']).reshape((-1, 1)),
             np.array(res[key]['state']).reshape((-1, 1))), axis=1).tolist()
        combine = []

        idx = 0
        for i in range(len(res[key]['time']) + 1):
            if i == len(res[key]['time']) or res[key]['state'][i] == 2:
                k = 1
                if i == len(res[key]['time']):
                    k = 0
                combine.append(tmp[idx:i + k])
                idx = i + 1
        res[key] = combine

    return res


