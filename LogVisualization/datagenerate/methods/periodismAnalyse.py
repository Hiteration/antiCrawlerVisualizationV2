import os
import json
import numpy as np
from datagenerate.utils import lookup

def get_max_nseq(seq, nseq):
    if(len(seq) < nseq):
        return 0
    tmp_dic = {}
    for i in range(len(seq) - nseq + 1):
        key = ''
        for j in range(i, i+nseq):
          key += seq[j]
        
        if(key in tmp_dic.keys()):
            tmp_dic[key] += 1
        else:
            tmp_dic[key] = 1
    return max(tmp_dic.values())
        

def periodismAnalyseLine(name, windowsType, viewObject, viewTarget, beginTime, endTime, windowsSize, seqLength):
    res = {}
    baseDir = os.path.dirname(os.path.abspath(__name__))
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
        tmp_diversity = {}
        timeStr = {}  # 每次访问的格式化时间
        count = {}  # 每次访问的时间窗口内资源种类数
        state = {}  # 每次访问的状态 0表示通过 1表示怀疑 2表示封禁
        flag = {}  # 记录tmp中是否出现过时间跨度大于windowsSize
        ignore = {}  # 记录每个ip是否处于连续访问封禁中

        for key in viewTarget:
            tmp[key] = []
            tmp_diversity[key] = []
            timeStr[key] = []
            count[key] = []
            state[key] = []
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
                tmp[tmp_key].append(info['time'])
                tmp_diversity[tmp_key].append(info['operationObject'])
                if info['time'] - windowsSize > tmp[tmp_key][0]:
                    flag[tmp_key] = True
                    while info['time'] - windowsSize > tmp[tmp_key][0]:
                        del tmp[tmp_key][0]
                        del tmp_diversity[tmp_key][0]

                if info['time'] >= beginTime and flag[tmp_key]:
                    code = info['status']['code']  # 得到此次访问的状态码
                    if code >=0 and code < 3  and not (code == 2 and ignore[info[viewobject]]):
                        timeStr[tmp_key].append(info['timeStr'])
                        # -------------- # 
                        max_length = get_max_nseq(tmp_diversity[tmp_key], seqLength)
                        count[tmp_key].append(max_length)

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
            res[key] = {'time':timeStr[key],'count':count[key],'state':state[key]}
        
    else:  # 使用的是次数窗口
        tmp = {}  # 节点历史访问时间
        tmp_diversity = {}
        timeStr = {}  # 每次访问的格式化时间
        count = {}  # 每次访问的时间窗口内频数
        state = {}  # 每次访问的状态 0表示通过 1表示怀疑 2表示封禁
        ignore = {}

        for key in viewTarget:
            tmp[key] = []
            tmp_diversity[key] = []
            timeStr[key] = []
            count[key] = []
            state[key] = []
            ignore[key] = False


        with open(fileName) as file:
            infos = json.load(file)  # 加载日志信息
            if endTime == -1:  # 如果结束时间没有设置
                endTime = infos[-1]['time']
            for info in infos:
                if info['time'] > endTime:
                    break
                if info[viewobject] not in viewTargets:
                    continue
                tmp[info[viewobject]].append(info['time'])
                tmp_diversity[info[viewobject]].append(info['operationObject'])
                if len(tmp[info[viewobject]]) == windowsSize:
                    if info['time'] >= beginTime:
                        code = info['status']['code']  # 得到此次访问的状态码
                        if code >=0 and code < 3  and not (code == 2 and ignore[info[viewobject]]):
                            timeStr[info[viewobject]].append(info['timeStr'])
                            max_length = get_max_nseq(tmp_diversity[info[viewobject]], seqLength)
                            count[info[viewobject]].append(max_length)
                            # count[info[viewobject]].append(len(set(tmp_diversity[info[viewobject]])))
                            if code == 0:
                                ignore[info[viewobject]] = False
                                state[info[viewobject]].append(0)
                            elif code == 1:
                                ignore[info[viewobject]] = False
                                state[info[viewobject]].append(1)
                            else:
                                ignore[info[viewobject]] = True
                                state[info[viewobject]].append(2)
                    del tmp[info[viewobject]][0]
                    del tmp_diversity[info[viewobject]][0]

        for key in state.keys():
            res[key] = {'time': timeStr[key], 'count': count[key], 'state': state[key]}

    for key in viewTarget:
        tmp = np.concatenate((np.array(res[key]['time']).reshape((-1,1)),np.array(res[key]['count']).reshape((-1,1)),np.array(res[key]['state']).reshape((-1,1))),axis=1).tolist()
        combine = []
        idx = 0
        for i in range(len(res[key]['time']) + 1):
            if i == len(res[key]['time']) or res[key]['state'][i] == 1:
                k = 1
                if i == len(res[key]['time']):
                    k=0
                combine.append(tmp[idx:i + k])
                idx = i + 1
        res[key] = combine
    # print(ignore)
    # print(res['92.168.1.5'][-1][-5:])
    res_new = {}
    for ip in res:
      ip_str = lookup(ip)
      res_new.update({ip_str: res[ip]}) 
          
    return res_new
