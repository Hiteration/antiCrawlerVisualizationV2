import os
import json
import numpy as np

from datagenerate.utils import lookup

# 基于频率的分析
def freAnalyseLine(fileName, windowType, targetType, selectedTargets, beginTime, endTime, windowsSize):
    res = {}
    baseDir = os.path.dirname(os.path.abspath(__name__))
    fileNameDir = os.path.join(baseDir, 'tmp', fileName)
    metaInfoDir = os.path.join(baseDir, 'tmp', 'meta', fileName)

    if targetType == 0:
        targetType = 'ip'
        detail = 'ipDetail'
    if targetType == 1:
        targetType = 'account'
        detail = 'accountDetail'

    # 如果未传入观察对象，则设定为全部对象
    if len(selectedTargets) == 0:
        with open(metaInfoDir) as file:  # 根据元数据进行观察目标初始化
            metaInfo = json.load(file)
            for key in metaInfo[detail].keys():
                selectedTargets.append(key)

    # 将selectedTargets转换为selectedTargets_set
    selectedTargets_set = set()
    for target in selectedTargets:
        selectedTargets_set.add(target)

    if windowType == 0:  # 使用的是时间窗口
        tmp = {}  # 节点历史访问时间
        timeStr = {}  # 每次访问的格式化时间
        count = {}  # 每次访问的时间窗口内频数
        state = {}  # 每次访问的状态 1表示安全 2表示怀疑 3表示封禁/限流
        flag = {}  # 记录tmp中是否出现过时间跨度大于windowsSize
        ignore = {}  # 记录每个ip是否处于连续访问封禁中

        for key in selectedTargets:
            tmp[key] = [] # tmp是个字典，里面每个key(ip/account)对应一个列表
            # 以下是三元组
            timeStr[key] = []
            count[key] = []
            state[key] = []
            # 以下是辅助
            flag[key] = False
            ignore[key] = False

        with open(fileNameDir) as file:
            fileInfo = json.load(file)  # 加载日志信息
            if endTime == -1:  # 如果结束时间没有设置
                endTime = fileInfo[-1]['time']
            for item in fileInfo: # item是每一次访问
                if item['time'] > endTime:
                    break
                # tmp_key是ip/account
                # tmp是个字典，里面每个key(ip/account)对应一个列表
                tmp_key = item[targetType] # 如果选的是ip就关注该对象的ip，如果选的是account就关注该对象的account
                if tmp_key not in selectedTargets_set: # 如果该ip/account不再选择的里面 则跳过
                    continue
                tmp[tmp_key].append(item['time']) # 给ip/acount对应的列表增加时间项
                # 删掉最靠前凑不够一个windowSize的时间点
                if item['time'] - windowsSize > tmp[tmp_key][0]:
                    flag[tmp_key] = True
                    while item['time'] - windowsSize > tmp[tmp_key][0]:
                        del tmp[tmp_key][0]

                if item['time'] >= beginTime and flag[tmp_key]:
                    code = item['status']['code']  # 得到此次访问的状态码
                    if code >= 1 and code < 4  and not (code == 3 and ignore[item[targetType]]):  # 如果此时是3(封禁)and之前也是封禁 则不添加
                        timeStr[tmp_key].append(item['timeStr'])
                        count[tmp_key].append(len(tmp[tmp_key]))
                        if code == 1:
                            ignore[tmp_key] = False
                            state[tmp_key].append(1)
                        elif code == 2:
                            ignore[tmp_key] = False
                            state[tmp_key].append(2)
                        else:
                            ignore[tmp_key] = True
                            state[tmp_key].append(3)

        for key in selectedTargets:
            res[key] = {'time': timeStr[key], 'count': count[key], 'state': state[key]}  # res格式{ip1:{'time': [], 'count': [], 'state': []}, ip2:{}, ... }

    else:  # 使用的是次数窗口
        tmp = {}  # 节点历史访问时间
        timeStr = {}  # 每次访问的格式化时间
        count = {}  # 每次访问的时间窗口内频数
        state = {}  # 每次访问的状态 1表示安全 2表示怀疑 3表示封禁/限流
        ignore = {}
        for key in selectedTargets:
            tmp[key] = []
            timeStr[key] = []
            count[key] = []
            state[key] = []
            ignore[key] = False
        with open(fileNameDir) as file:
            fileInfo = json.load(file)  # 加载日志信息
            if endTime == -1:  # 如果结束时间没有设置
                endTime = fileInfo[-1]['time']
            for item in fileInfo:
                if item['time'] > endTime:
                    break
                if item[targetType] not in selectedTargets_set:
                    continue
                tmp[item[targetType]].append(item['time'])
                if len(tmp[item[targetType]]) == windowsSize:
                    if item['time'] >= beginTime:
                        code = item['status']['code']  # 得到此次访问的状态码
                        if code >= 1 and code < 4  and not (code == 3 and ignore[item[targetType]]):
                            timeStr[item[targetType]].append(item['timeStr'])
                            count[item[targetType]].append(tmp[item[targetType]][-1] - tmp[item[targetType]][0])
                            if code == 1:
                                ignore[item[targetType]] = False
                                state[item[targetType]].append(1)
                            elif code == 2:
                                ignore[item[targetType]] = False
                                state[item[targetType]].append(2)
                            else:
                                ignore[item[targetType]] = True
                                state[item[targetType]].append(3)
                    del tmp[item[targetType]][0]
        for key in state.keys():
            res[key] = {'time': timeStr[key], 'count': count[key], 'state': state[key]}

    for key in selectedTargets:
        tmp_time = np.array(res[key]['time']).reshape(-1,1) # 取出时间列表[1, 2, 3] 然后二维化[[1][2][3]]
        tmp_count = np.array(res[key]['count']).reshape(-1,1)
        tmp_state = np.array(res[key]['state']).reshape(-1,1)
        tmp = np.concatenate((tmp_time, tmp_count, tmp_state), axis=1).tolist() # 按行拼接 成为多个三元组
        combine = [] # 带断开的多个三元组
        idx = 0
        # 下面用于从怀疑点处断开, 为什么?--应该是不需要的, 前端又缝合了
        for i in range(len(res[key]['time']) + 1):
            if i == len(res[key]['time']) or res[key]['state'][i] == 1:
                k = 1
                if i == len(res[key]['time']):
                    k = 0
                combine.append(tmp[idx: i+k])
                idx = i + 1
        res[key] = combine

    # 用于把ip转换为归属地(内置字典待更新)
    res_new = {}
    for ip in res:
      ip_str = lookup(ip)
      res_new.update({ip_str: res[ip]}) 
    return res_new


# 基于频率分析的盒线图
""" count中5个数组对应的5种状态变化
0   安全->怀疑
1   安全->封禁
2   怀疑->安全
3   封禁->安全
4   怀疑->封禁
"""
def freAnalyseBox(fileName, windowType, targetType, selectedTargets, beginTime, endTime, windowsSize):
    res = {}
    baseDir = os.path.dirname(os.path.abspath(__name__))
    fileNameDir = os.path.join(baseDir, 'tmp', fileName)  # 原始文件路径
    metaInfoDir = os.path.join(baseDir, 'tmp', 'meta', fileName)  # 元信息文件路径

    if targetType == 0:
        targetType = 'ip'
        detail = 'ipDetail'
    if targetType == 1:
        targetType = 'account'
        detail = 'accountDetail'

    # 如果未传入观察对象，则设定为全部对象
    if len(selectedTargets) == 0:
        with open(metaInfoDir) as file:  # 根据元数据进行观察目标初始化
            metaInfo = json.load(file)
            for key in metaInfo[detail].keys():
                selectedTargets.append(key)

    selectedTargets_set = set()
    for target in selectedTargets:
        selectedTargets_set.add(target)


    if windowType == 1:  # 使用的是次数窗口
        tmp = {}
        count = {}  # 记录每次状态转变时的特征
        preState = {}  # 前一次访问的状态
        for key in selectedTargets:
            tmp[key] = []
            count[key] = [[], [], [], [], []]
            preState[key] = -1

        with open(fileNameDir) as file:
            fileInfo = json.load(file)
        if endTime == -1:  # 如果结束时间没有设置
            endTime = fileInfo[-1]['time']
        for item in fileInfo:
            if item['time'] > endTime:
                break
            if item[targetType] not in selectedTargets_set:
                continue

            tmp_key = item[targetType]
            tmp[tmp_key].append(item['time'])
            code = item['status']['code']  # 得到此次访问的状态码
            # 获取访问的状态 0表示通过 1表示怀疑 2表示封禁
            state = code
            if len(tmp[tmp_key]) == windowsSize:
                if state != preState[tmp_key] and item['time'] > beginTime and preState[tmp_key] != -1:  # 发生状态变化且时间符合条件
                    tmp_value = tmp[item[targetType]][-1] - tmp[item[targetType]][0]
                    if state == 0:
                        if preState[tmp_key] == 1:  # 怀疑->安全
                            count[tmp_key][2].append(tmp_value)
                        else:  # 封禁->安全
                            count[tmp_key][3].append(tmp_value)
                    elif state == 1:
                        if preState[tmp_key] == 0:  # 安全->怀疑
                            count[tmp_key][0].append(tmp_value)
                    elif state == 2:
                        if preState[tmp_key] == 0:  # 安全->封禁
                            count[tmp_key][1].append(tmp_value)
                        else:  # 怀疑->封禁
                            count[tmp_key][4].append(tmp_value)
                del tmp[tmp_key][0]  # 清除首记录
            preState[tmp_key] = state  # 记录前一次状态
        res = count


    else:  # 使用的是时间窗口
        tmp = {}
        count = {}  # 记录每次状态转变时的特征
        preState = {}  # 前一次访问的状态
        flag = {}
        for key in selectedTargets:
            tmp[key] = []
            count[key] = [[], [], [], [], []]
            preState[key] = -1
            flag[key] = False

        with open(fileNameDir) as file:
            fileInfo = json.load(file)
        if endTime == -1:  # 如果结束时间没有设置
            endTime = fileInfo[-1]['time']
        for item in fileInfo:
            if item['time'] > endTime:
                break
            if item[targetType] not in selectedTargets_set:
                continue

            tmp_key = item[targetType]
            tmp[tmp_key].append(item['time'])
            if item['time'] - tmp[tmp_key][0] >= windowsSize:
                flag[tmp_key] = True
                while item['time'] - tmp[tmp_key][0] > windowsSize:
                    del tmp[tmp_key][0]
            code = item['status']['code']  # 得到此次访问的状态码
            # 获取访问的状态 0表示通过 1表示怀疑 2表示封禁
            state = code
            if flag[tmp_key]:  # 满足记录条件
                if state != preState[tmp_key] and item['time'] > beginTime and preState[tmp_key] != -1:  # 发生状态变化且时间符合条件
                    tmp_value = len(tmp[item[targetType]])
                    if state == 0:
                        if preState[tmp_key] == 1:  # 怀疑->安全
                            count[tmp_key][2].append(tmp_value)
                        else:  # 封禁->安全
                            count[tmp_key][3].append(tmp_value)
                    elif state == 1:
                        if preState[tmp_key] == 0:  # 安全->怀疑
                            count[tmp_key][0].append(tmp_value)
                    elif state == 2:
                        if preState[tmp_key] == 0:  # 安全->封禁
                            count[tmp_key][1].append(tmp_value)
                        else:  # 怀疑->封禁
                            count[tmp_key][4].append(tmp_value)
            preState[tmp_key] = state  # 记录前一次状态
        res = count
    for key in res.keys():
        for i in range(len(res[key])):
            tmp = []
            if len(res[key][i])>0:
                tmp.append(np.min(np.array(res[key][i],dtype=float)))
                tmp.append(np.mean(np.array(res[key][i],dtype=float)))
                tmp.append(np.max(np.array(res[key][i],dtype=float)))
                tmp.append(np.std(np.array(res[key][i],dtype=float)))
            res[key][i] = tmp
    return res
