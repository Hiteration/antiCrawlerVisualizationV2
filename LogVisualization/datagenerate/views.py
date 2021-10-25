from django.http import HttpResponse
import json
import os

# 分析前端传过来的参数调用不同的分析函数
# 分析频率参数
from datagenerate.methods.freAnalyse import freAnalyseLine, freAnalyseBox
# 分析间隔参数
from datagenerate.methods.intervalAnalyse import intervalAnalyseLine
# 分析连续在线时长参数
from datagenerate.methods.onlineAnalyse import onlineAnalyseLine
# 分析多样性参数
from datagenerate.methods.diversityAnalyse import diversityAnalyseLine
# 分析周期性参数
from datagenerate.methods.periodismAnalyse import periodismAnalyseLine
# 分析休眠时长参数
from datagenerate.methods.restdata import restDataLine
# 分析???参数
from datagenerate.methods.stepLineData import getSteplineData
from filemanager.utils import strToTime

def frequencydata(request):
    fileName = request.POST.get('fileName')  # 获取解析文件名
    windowType = int(request.POST.get('windowType', 0))  # 获取窗口类型，默认为0(时间窗口)
    targetType = int(request.POST.get('targetType', 0))  # 获取目标类型，默认为0(ip)
    selectedTargets = request.POST.get('selectedTargets', []).split(',')  # 获取目标，默认为all(全部目标）
    beginTime = request.POST.get('beginTime', '')
    endTime = request.POST.get('endTime', '')
    windowSize = int(request.POST.get('windowSize', 200))  # 特征窗口大小，默认为200
    print(beginTime)
    print(endTime)
    res = {'code': 200}
    # 将beginTime和endTime转化为数值型
    baseDir = os.path.dirname(os.path.abspath(__name__))
    with open(os.path.join(baseDir, 'tmp', 'meta', fileName)) as f:
        metaData = json.load(f)
    if len(beginTime) == 0:
        beginTime = 0
    else:
        strToTime(metaData['beginTimeStr'], True) # 更新utils中的beginTime(从metaData的beginTimeStr而来)
        beginTime = strToTime(beginTime) # 以utils中的beginTime为基准, 计算前端传来的beginTime对应的秒(这里由于由于前端调整为当日00:00:00, 故为负值)

    if len(endTime) == 0:
        endTime = metaData['endTime']
    else:
        strToTime(metaData['beginTimeStr'], True)
        endTime = strToTime(endTime)

    if beginTime >= endTime and endTime != -1:
        res['code'] = 410

    if res['code'] != 200:  # 传送的参数错误，直接返回
        return HttpResponse(json.dumps(res), content_type="application/json")

    res['lineData'] = freAnalyseLine(fileName, windowType, targetType, selectedTargets, beginTime, endTime, windowSize) # freAnalyseLine方法
    res['boxData'] = freAnalyseBox(fileName, windowType, targetType, selectedTargets, beginTime, endTime, windowSize)

    return HttpResponse(json.dumps(res), content_type="application/json")

def intervaldata(request):
    fileName = request.POST.get('fileName')  # 获取解析文件名
    windowType = int(request.POST.get('windowType', 0))  # 获取窗口类型，默认为0(时间窗口)
    targetType = int(request.POST.get('targetType', 0))  # 获取观察对象，默认为0(ip)
    selectedTargets = request.POST.getlist('selectedTargets', [])[0].split(',')  # 获取目标，默认为all(全部目标）
    beginTime = (request.POST.get('beginTime', ''))  # 开始时间，默认为0
    endTime = (request.POST.get('endTime', ''))  # 结束时间，默认为-1(最大时间值）
    windowSize = int(request.POST.get('windowSize', 200))  # 特征窗口大小，默认为200
    res = {'code': 200}

    # 将beginTime和endTime转化为数值型
    baseDir = os.path.dirname(os.path.abspath(__name__))
    with open(os.path.join(baseDir, 'tmp', 'meta', fileName)) as f:
        metaData = json.load(f)
    if len(beginTime)==0:
        beginTime = 0
    else:
        strToTime(metaData['beginTimeStr'],True)
        beginTime = strToTime(beginTime)

    if len(endTime) == 0:
        endTime = metaData['endTime']
    else:
        strToTime(metaData['beginTimeStr'], True)
        endTime = strToTime(endTime)

    res['lineData'] = intervalAnalyseLine(fileName, windowType, targetType, selectedTargets, beginTime, endTime, windowSize)

    return HttpResponse(json.dumps(res), content_type="application/json")

def onlinetimedata(request):
    fileName = request.POST.get('fileName')  # 获取解析文件名
    targetType = int(request.POST.get('targetType', 0))  # 获取观察对象，默认为0(ip)
    selectedTargets = request.POST.getlist('selectedTargets', [])[0].split(',')  # 获取目标，默认为all(全部目标）
    beginTime = (request.POST.get('beginTime', ''))  # 开始时间，默认为0
    endTime = (request.POST.get('endTime', ''))  # 结束时间，默认为-1(最大时间值）
    deltaTime = request.POST.get('deltaTime')
    res = {'code': 200}

    # 将beginTime和endTime转化为数值型
    baseDir = os.path.dirname(os.path.abspath(__name__))
    with open(os.path.join(baseDir, 'tmp', 'meta', fileName)) as f:
        metaData = json.load(f)
    if len(beginTime) == 0:
        beginTime = 0
    else:
        strToTime(metaData['beginTimeStr'], True)
        beginTime = strToTime(beginTime)

    if len(endTime) == 0:
        endTime = metaData['endTime']
    else:
        strToTime(metaData['beginTimeStr'], True)
        endTime = strToTime(endTime)

    if beginTime >= endTime:
        res['code'] = 410

    res['lineData'] = onlineAnalyseLine(fileName, deltaTime, targetType, selectedTargets, beginTime, endTime,)
    return HttpResponse(json.dumps(res), content_type="application/json")

def restdata(request):
    fileName = request.POST.get('fileName')  # 获取解析文件名
    targetType = int(request.POST.get('targetType', 0))  # 获取观察对象，默认为0(ip)
    selectedTargets = request.POST.getlist('selectedTargets', [])[0].split(',')  # 获取目标，默认为all(全部目标）
    beginTime = (request.POST.get('beginTime', ''))  # 开始时间，默认为0
    endTime = (request.POST.get('endTime', ''))  # 结束时间，默认为-1(最大时间值）
    deltaTime = float(request.POST.get('deltaTime'))   # 连续在线访问最长间隔
    res = {'code': 200}

    # 将beginTime和endTime转化为数值型
    baseDir = os.path.dirname(os.path.abspath(__name__))
    with open(os.path.join(baseDir, 'tmp', 'meta', fileName)) as f:
        metaData = json.load(f)
    if len(beginTime) == 0:
        beginTime = 0
    else:
        strToTime(metaData['beginTimeStr'], True)
        beginTime = strToTime(beginTime)
        beginZeroTime = strToTime(metaData['beginTimeStr'][0:11]+'00:00:00')

    if len(endTime) == 0:
        endTime = metaData['endTime']
    else:
        strToTime(metaData['beginTimeStr'], True)
        endTime = strToTime(endTime)

    if beginTime >= endTime:
        res['code'] = 410

    # if res['code'] != 0:  # 传送的参数错误，直接返回
    #     return HttpResponse(json.dumps(res), content_type="application/json")

    res['lineData'] = restDataLine(fileName, deltaTime, targetType, selectedTargets, beginTime, endTime,beginZeroTime )
    # res['boxData'] = onlineAnalyseBox(fileName, deltaTime, targetType, selectedTargets, beginTime, endTime)

    return HttpResponse(json.dumps(res), content_type="application/json")

def diversitydata(request):
    fileName = request.POST.get('fileName')  # 获取解析文件名
    windowType = int(request.POST.get('windowType', 0))  # 获取窗口类型，默认为0(时间窗口)
    targetType = int(request.POST.get('targetType', 0))  # 获取观察对象，默认为0(ip)
    selectedTargets = request.POST.get('selectedTargets', []).split(',')  # 获取目标，默认为all(全部目标）
    beginTime = (request.POST.get('beginTime', ''))  # 开始时间，默认为0
    endTime = (request.POST.get('endTime', ''))  # 结束时间，默认为-1(最大时间值）
    windowSize = int(request.POST.get('windowSize', 200))  # 特征窗口大小，默认为200
    print(beginTime)
    print(endTime)
    res = {'code': 200}

    # 将beginTime和endTime转化为数值型
    baseDir = os.path.dirname(os.path.abspath(__name__))
    with open(os.path.join(baseDir, 'tmp', 'meta', fileName)) as f:
        metaData = json.load(f)
    if len(beginTime)==0:
        beginTime = 0
    else:
        strToTime(metaData['beginTimeStr'],True)
        beginTime = strToTime(beginTime)

    if len(endTime) == 0:
        endTime = metaData['endTime']
    else:
        strToTime(metaData['beginTimeStr'], True)
        endTime = strToTime(endTime)

    if beginTime >= endTime and endTime != -1:
        res['code'] = 410

    if res['code'] != 200:  # 传送的参数错误，直接返回
        return HttpResponse(json.dumps(res), content_type="application/json")
    
    res['lineData_number'] = diversityAnalyseLine(fileName, windowType, targetType, selectedTargets, beginTime, endTime, windowSize)
    return HttpResponse(json.dumps(res), content_type="application/json")

def periodismdata(request):
    fileName = request.POST.get('fileName')  # 获取解析文件名
    windowType = int(request.POST.get('windowType', 0))  # 获取窗口类型，默认为0(时间窗口)
    targetType = int(request.POST.get('targetType', 0))  # 获取观察对象，默认为0(ip)
    selectedTargets = request.POST.get('selectedTargets', []).split(',')  # 获取目标，默认为all(全部目标）
    beginTime = (request.POST.get('beginTime', ''))  # 开始时间，默认为0
    endTime = (request.POST.get('endTime', ''))  # 结束时间，默认为-1(最大时间值）
    windowSize = int(request.POST.get('windowSize', 200))  # 特征窗口大小，默认为200
    seqLength = int(request.POST.get('seqLength', 3))
    print(beginTime)
    print(endTime)
    res = {'code': 200}

    # 将beginTime和endTime转化为数值型
    baseDir = os.path.dirname(os.path.abspath(__name__))
    with open(os.path.join(baseDir, 'tmp', 'meta', fileName)) as f:
        metaData = json.load(f)
    if len(beginTime)==0:
        beginTime = 0
    else:
        strToTime(metaData['beginTimeStr'],True)
        beginTime = strToTime(beginTime)

    if len(endTime) == 0:
        endTime = metaData['endTime']
    else:
        strToTime(metaData['beginTimeStr'], True)
        endTime = strToTime(endTime)

    if beginTime >= endTime and endTime != -1:
        res['code'] = 410

    if res['code'] != 200:  # 传送的参数错误，直接返回
        return HttpResponse(json.dumps(res), content_type="application/json")
    
    res['lineData'] = periodismAnalyseLine(fileName, windowType, targetType, selectedTargets, beginTime, endTime, windowSize, seqLength)
    return HttpResponse(json.dumps(res), content_type="application/json")

def steplinedata(request):
    fileName = request.POST.get('fileName')  # 获取解析文件名
    time = int(request.POST.get('time'))
    res = getSteplineData(fileName, time)
    return HttpResponse(json.dumps(res), content_type="application/json")
