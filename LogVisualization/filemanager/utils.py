import json
import os
import re
import numpy as np
from functools import cmp_to_key

SUCCESS = ['1', '000000']
SUSPECTED = ['2', '906010']
BANNED = ['3', '900006']


pattren_rate_limit_exceeded = r'Rate limit exceeded'
pattern_unusual_login = r'There was unusual login activity on your account.'

'''
序号 返回码(rtnCode) 返回信息(rtnMsg) 
000000: 安全1
906010: 怀疑2
900006且rate limit exceeded: 限流3
其他: 错误4
'''

beginTime = np.zeros((4,), dtype=int)  # 起始时间，表示为年、时、分、秒
beginTime[0] = 2020
beginTime[1] = 14
beginTime[2] = 6
beginTime[3] = 54
dayOfMonth = [[31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],  # 每个月对应的天数
              [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]]
pastDays = 0  # 起始时间距当年1月1日的天数
scale = np.array([3600 * 24, 3600, 60, 1])  # 两个时间点的差距，分别为天、时、分、秒


def getDays(year):
    if year % 4 == 0 and year % 100 != 0:
        return 366
    if year % 400 == 0:
        return 366
    return 365


# 将字符型日期转化为距起始时间的秒数
def strToTime(strDate, setBeginTime=False):
    '''
    strDate: 时间
    setBeginTime: 是否设定初始时间
    '''
    global pastDays  # 注: 需要声明global, 函数内部才会修改全局变量
    passTime = np.zeros((4,), dtype=int)  # 天、时、分、秒
    now = re.split('-|:|[ ]', strDate)  # 根据-或:或空格 拆开strDate, 返回数组(string)
    now = np.array(now, dtype=int)  # 数组(string)变数组(int)
    if not setBeginTime:
        beginYear = beginTime[0]
    else:
        beginYear = now[0]  # 如果需要根据strDate重设beginTime
    while now[0] > beginYear:
        passTime[0] += getDays(beginYear)
        beginYear += 1
    yearType = getDays(now[0]) - 365
    for i in range(now[1] - 1):  # 当前月之前的所有月份天数之和
        passTime[0] += dayOfMonth[yearType][i]
    passTime[0] += (now[2] - 1)  # 再加上当前月天数
    # 仅仅初始化开始时间
    if setBeginTime:
        pastDays = passTime[0]
        beginTime[0] = now[0]  # 更新beginTime 注: 不需要任何声明, 函数内部就可以修改全局列表
        beginTime[1:] = now[3:]
        print("utils中的beginTime ", beginTime)
        return
    passTime[0] -= pastDays
    passTime[1:] = now[3:] - beginTime[1:]
    time = np.sum(passTime * scale)
    return time


def compare(json1, json2):
    if json1['time'] < json2['time']:
        return -1
    elif json1['time'] > json2['time']:
        return 1
    return 0


# 处理源信息(2.0)
def metaInfoCreate(fileName):
    baseDir = os.path.dirname(os.path.abspath(__name__))
    ips = set()
    accounts = set()
    metaInfo = {}

    # 记录是否有安全，怀疑，封禁状态
    IS_SUCCESS = 0
    IS_SUSPECTED = 0
    IS_BANNED = 0

    logs_write = []
    with open(os.path.join(baseDir, 'tmp', fileName)) as f:
        logs = json.load(f)
        begin = -1
        beginStr = None
        end = -1
        endStr = None
        metaInfo['ipDetail'] = {}
        metaInfo['accountDetail'] = {}

        # 添加time项表示距特定时间所过去的秒
        strToTime('2020-1-1 00:00:00', True)  # 重置起始时间
        minTime = float(strToTime(logs[0]['operationTime'][:-4]))

        for log in logs:
            log['time'] = float(strToTime(log['operationTime'][:-4]))
            minTime = min(minTime, log['time'])
            code = str(log['operationResult']['rtnCode'])
            if code in SUCCESS:
                IS_SUCCESS = 1
                log['operationResult'] = '1'
                logs_write.append(log)
            if code in SUSPECTED:
                IS_SUSPECTED = 1
                log['operationResult'] = '2'
                logs_write.append(log)
            if code in BANNED:
                try:
                    if re.search(pattren_rate_limit_exceeded, log['operationResult']['result']):
                        print("there is ban!!!!")
                        IS_BANNED = 1
                        log['operationResult'] = '3'
                        logs_write.append(log)
                except:
                    continue
        # 将原始json转化为目标格式
        for log in logs_write:
            log['time'] -= minTime
            log['ip'] = log['clientIP']
            del log['clientIP']
            log['timeStr'] = log['operationTime'][:-4]
            del log['operationTime']
            log['status'] = {'code': 0}

            if str(log['operationResult']) in SUCCESS:
                log['status']['code'] = 1
            if str(log['operationResult']) in SUSPECTED:
                log['status']['code'] = 2
            if str(log['operationResult']) in BANNED:
                log['status']['code'] = 3
            del log['operationResult']
            log['account'] = log['operatorName']
            del log['operatorName']
        logs_write = sorted(logs_write, key=cmp_to_key(compare))  # 按照时间排序

        for log in logs_write:
            if log['status']['code'] > -1:
                endStr = log['timeStr']
                end = log['time']
                if begin == -1:
                    beginStr = log['timeStr']
                    begin = log['time']
            # 遇到新的IP
            if log['ip'] not in ips:
                ips.add(log['ip'])
                metaInfo['ipDetail'][log['ip']] = [0, 0, 0]
            # 遇到新的account
            if log['account'] not in accounts:
                accounts.add(log['account'])
                metaInfo['accountDetail'][log['account']] = [0, 0, 0]
            # 判断此次访问的结果
            if log['status']['code'] == 1:  # 成功状态
                metaInfo['ipDetail'][log['ip']][0] += 1
                metaInfo['accountDetail'][log['account']][0] += 1
            elif log['status']['code'] == 2:  # 怀疑状态
                metaInfo['ipDetail'][log['ip']][1] += 1
                metaInfo['accountDetail'][log['account']][1] += 1
            elif log['status']['code'] == 3:  # 封禁状态
                metaInfo['ipDetail'][log['ip']][2] += 1
                metaInfo['accountDetail'][log['account']][2] += 1

        metaInfo['beginTime'] = begin
        metaInfo['beginTimeStr'] = beginStr
        metaInfo['endTime'] = end
        metaInfo['endTimeStr'] = endStr
        metaInfo['ipNum'] = len(ips)
        metaInfo['accountNum'] = len(accounts)
        metaInfo['fileName'] = fileName

    with open(os.path.join(baseDir, 'tmp', 'meta', fileName), 'w') as f:
        json.dump(metaInfo, f)
    with open(os.path.join(baseDir, 'tmp', fileName), 'w') as f:
        json.dump(logs_write, f)

    '''
    # stage=1,无封禁 无怀疑
    # stage=2,无封禁 有怀疑
    # stage=3,有封禁
    '''
    stage = 0
    if (not IS_BANNED) and (not IS_SUSPECTED):
        stage = 1
    if (not IS_BANNED) and IS_SUSPECTED:
        stage = 2
    if IS_BANNED:
        stage = 3

    default_params = {
        "frequency": {
            "stage": stage,
            "windowType": 1,
            "windowSize": 500
        },
        "interval": {
            "stage": stage,
            "windowType": 1,
            "windowSize": 500
        },
        "rest": {
            "stage": stage,
            "deltaTime": 14400
        },
        "diversity": {
            "stage": stage,
            "windowType": 1,
            "windowSize": 500
        }
    }
    with open(os.path.join(baseDir, 'tmp', 'param', fileName), 'w') as f:
        json.dump(default_params, f)
