from django.http import HttpResponse
import os
import json
import pandas as pd

from datagenerate.methods.freAnalyse import freAnalyseLine, freAnalyseBox
from datagenerate.methods.intervalAnalyse import intervalAnalyseLine
from datagenerate.methods.restdata import restDataLine
from datagenerate.methods.diversityAnalyse import diversityAnalyseLine
from filemanager.utils import strToTime


def paramsdata(request):
    name = request.POST.get('fileName')  # 获取解析文件名
    baseDir = os.path.dirname(os.path.abspath(__name__))
    file_name = name.split('.')[0] + '_best_params.json'
    rst = {}
    with open(os.path.join(baseDir, 'tmp', file_name)) as f:
        rst = json.load(f)

    return HttpResponse(json.dumps(rst), content_type="application/json")

def fre_points(request):
    print("获取数据中...")
    name = request.POST.get('fileName')  # 获取解析文件名
    viewObject = int(request.POST.get('viewObject', 0))  # 获取观察对象，默认为0(ip)
    # beginTime = (request.POST.get('beginTime', ''))  # 开始时间，默认为0
    # endTime = (request.POST.get('endTime', ''))  # 结束时间，默认为-1(最大时间值）
    beginTime = 0
    endTime = -1
    baseDir = os.path.dirname(os.path.abspath(__name__))
    file_name = name.split('.')[0] + '_best_params.json'
    with open(os.path.join(baseDir, 'tmp', file_name)) as f:
        infos = json.load(f)
        windowsType = infos['frequency']['windowType']
        windowsSize = infos['frequency']['windowSize']

    line_data_origin = freAnalyseLine(name, windowsType, viewObject, [], beginTime, endTime, windowsSize)
    line_data = {}
    for ip in line_data_origin.keys():
        if(ip not in line_data.keys()):
            line_data[ip] = []
        for item in line_data_origin[ip]:
            for threes in item:
                line_data[ip].append([threes[0], float(threes[1]), str(threes[2])])
    # print(line_data)
    # quit()
    dataset_time = []
    for ip in line_data.keys():
        for threes in line_data[ip]:
            dataset_time.append([ip, threes[0], float(threes[1]), str(threes[2])])
    # print(dataset_time[:10])
    rst = {}
    dataset = pd.DataFrame(dataset_time, columns=['ip','time', 'frequency', 'status'])
    for name, group in dataset.groupby('ip'):
        if(name not in rst.keys()):
            rst[name] = []
        # group['status'] = str(group['status'])
        if('2' in list(group['status'])):
            #3 print(group[group['status'] == '2']['frequency'])
            if(windowsType == 0):
                rst[name] = [group[group['status'] == '2']['frequency'].min(), 2]
            else:
                rst[name] = [group[group['status'] == '2']['frequency'].max(), 2]
        else:
            if(windowsType == 0):
                rst[name] = [group[group['status'] == '0']['frequency'].max(), 0]
            else:
                rst[name] = [group[group['status'] == '0']['frequency'].min(), 0]
    print(rst)
    return HttpResponse(json.dumps(rst), content_type="application/json")

def interval_points(request):
    print("获取数据中...")
    name = request.POST.get('fileName')  # 获取解析文件名
    viewObject = int(request.POST.get('viewObject', 0))  # 获取观察对象，默认为0(ip)
    # beginTime = (request.POST.get('beginTime', ''))  # 开始时间，默认为0
    # endTime = (request.POST.get('endTime', ''))  # 结束时间，默认为-1(最大时间值）
    beginTime = 0
    endTime = -1
    baseDir = os.path.dirname(os.path.abspath(__name__))
    file_name = name.split('.')[0] + '_best_params.json'
    with open(os.path.join(baseDir, 'tmp', file_name)) as f:
        infos = json.load(f)
        windowsType = infos['frequency']['windowType']
        windowsSize = infos['frequency']['windowSize']
    
    line_data_origin = intervalAnalyseLine(name, windowsType, viewObject, [], beginTime, endTime, windowsSize)
    line_data = {}
    for ip in line_data_origin.keys():
        if(ip not in line_data.keys()):
            line_data[ip] = []
        for item in line_data_origin[ip]:
            for threes in item:
                line_data[ip].append([threes[0], float(threes[1]), str(threes[2])])
    # print(line_data)
    # quit()
    dataset_time = []
    for ip in line_data.keys():
        for threes in line_data[ip]:
            dataset_time.append([ip, threes[0], float(threes[1]), str(threes[2])])
    # print(dataset_time[:10])
    rst = {}
    dataset = pd.DataFrame(dataset_time, columns=['ip','time', 'interval', 'status'])
    for name, group in dataset.groupby('ip'):
        if(name not in rst.keys()):
            rst[name] = []
        # group['status'] = str(group['status'])
        if('2' in list(group['status'])):
            rst[name] = [group[group['status'] == '2']['interval'].max(), 2]
        else:
            rst[name] = [group[group['status'] == '0']['interval'].min(), 0]
    print(rst)
    return HttpResponse(json.dumps(rst), content_type="application/json")

def rest_points(request):
    print('正在获取restPoints...')
    name = request.POST.get('fileName')  # 获取解析文件名
    viewObject = int(request.POST.get('viewObject', 0))  # 获取观察对象，默认为0(ip)
    # viewTarget = ['195.221.68.34', '195.221.22.21', '92.168.1.5', '225.168.2.5', '192.168.1.5', '195.221.56.8', '229.21.36.85', '19.168.89.5', '225.168.6.8', '225.168.9.52', '225.168.1.6'] # 获取目标，默认为all(全部目标）
    beginTime = ""
    endTime = ""
    # 将beginTime和endTime转化为数值型
    baseDir = os.path.dirname(os.path.abspath(__name__))
    with open(os.path.join(baseDir, 'tmp', 'meta', name)) as f:
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

    file_name = name.split('.')[0] + '_best_params.json'
    with open(os.path.join(baseDir, 'tmp', file_name)) as f:
        infos = json.load(f)
        deltaTime = infos['rest']['deltaTime']
    line_data_origin = restDataLine(name, deltaTime, viewObject, [], beginTime, endTime,beginZeroTime)
    line_data = {}
    for ip in line_data_origin.keys():
        if(ip not in line_data.keys()):
            line_data[ip] = []
        for threes in line_data_origin[ip]:
            # for threes in item:
            line_data[ip].append([threes[0], float(threes[1]), str(threes[2])])
    # print(line_data)
    # quit()
    dataset_time = []
    for ip in line_data.keys():
        for threes in line_data[ip]:
            dataset_time.append([ip, threes[0], float(threes[1]), str(threes[2])])
    # print(dataset_time[:10])
    rst = {}
    dataset = pd.DataFrame(dataset_time, columns=['ip','time', 'rest', 'status'])
    for name, group in dataset.groupby('ip'):
        if(name not in rst.keys()):
            rst[name] = []
        # group['status'] = str(group['status'])
        if('2' in list(group['status'])):
            #3 print(group[group['status'] == '2']['frequency'])
            rst[name] = [group[group['status'] == '2']['rest'].max(), 2]
        else:
            rst[name] = [group[group['status'] == '0']['rest'].max(), 0]
    print(rst)
    return HttpResponse(json.dumps(rst), content_type="application/json")

def diversity_points(request):
    print('正在获取参数...')
    name = request.POST.get('fileName')  # 获取解析文件名
    # windowsType = int(request.POST.get('windowsType', 0))  # 获取窗口类型，默认为0(时间窗口)
    viewObject = int(request.POST.get('viewObject', 0))  # 获取观察对象，默认为0(ip)
    beginTime = 0 #int(request.POST.get('beginTime', 0))  # 开始时间，默认为0
    endTime = -1
    baseDir = os.path.dirname(os.path.abspath(__name__))
    file_name = name.split('.')[0] + '_best_params.json'
    with open(os.path.join(baseDir, 'tmp', file_name)) as f:
        infos = json.load(f)
        windowsType = infos['diversity']['windowType']
        windowsSize = infos['diversity']['windowSize']
    line_data_origin = diversityAnalyseLine(name, windowsType, viewObject, [], beginTime, endTime, windowsSize)
    line_data = {}
    for ip in line_data_origin.keys():
        if(ip not in line_data.keys()):
            line_data[ip] = []
        for item in line_data_origin[ip]:
            for threes in item:
                line_data[ip].append([threes[0], float(threes[1]), str(threes[2])])
    # print(line_data)
    # quit()
    dataset_time = []
    for ip in line_data.keys():
        for threes in line_data[ip]:
            dataset_time.append([ip, threes[0], float(threes[1]), str(threes[2])])
    # print(dataset_time[:10])
    rst = {}
    dataset = pd.DataFrame(dataset_time, columns=['ip','time', 'frequency', 'status'])
    for name, group in dataset.groupby('ip'):
        if(name not in rst.keys()):
            rst[name] = []
        # group['status'] = str(group['status'])
        if('2' in list(group['status'])):
            #3 print(group[group['status'] == '2']['frequency'])
            rst[name] = [group[group['status'] == '2']['frequency'].max(), 2]
        else:
            rst[name] = [group[group['status'] == '0']['frequency'].max(), 0]
    print(rst)
    return HttpResponse(json.dumps(rst), content_type="application/json")
