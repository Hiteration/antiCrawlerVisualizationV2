from django.http import HttpResponse
import json
import os
import pandas as pd

# 分析前端传过来的参数调用不同的分析函数
# 分析频率参数
from datagenerate.methods.freAnalyse import freAnalyseLine
# 分析间隔参数
from datagenerate.methods.intervalAnalyse import intervalAnalyseLine
# 分析休眠时长参数
from datagenerate.methods.restdata import restDataLine
# 分析多样性参数
from datagenerate.methods.diversityAnalyse import diversityAnalyseLine
from filemanager.utils import strToTime

AIM = 2
TIME_WIN_SIZE = [i for i in range(300, 5501, 300)]
NUMBER_WIN_SIZE = [i for i in range(50, 501, 50)]

# 自动获取频率参数
def fre_params(request):
    print('正在获取fre参数...')
    fileName = request.POST.get('fileName')  # 获取解析日志名
    targetType = int(request.POST.get('targetType', 0))  # 获取观察对象，默认为0(ip)
    selectedTargets = []  # 获取目标，空对应全部目标
    beginTime = 0  # 开始时间，默认为0
    endTime = -1  # 结束时间，默认为-1(最大时间值）

    timeW = {}  
    numberW = {}
    newParams = {}

    baseDir = os.path.dirname(os.path.abspath(__name__))
    with open(os.path.join(baseDir, 'tmp', 'meta', fileName)) as f:
        metaData = json.load(f)
    
    paraminfo_path = os.path.join(baseDir, 'tmp', 'param', fileName)
    with open(paraminfo_path) as f:
        paramsinfo = json.load(f)

    '''
    stage=0, 初始化
    stage=1, 无封禁 无怀疑
    stage=2, 无封禁 有怀疑
    stage=3, 有封禁
    '''
    # 日志中无封禁，无怀疑
    if paramsinfo['frequency']['stage'] == 1:
        newParams["stage"] = 1
        return HttpResponse(json.dumps(newParams), content_type="application/json")

    # 日志中无封禁，有怀疑
    if paramsinfo['frequency']['stage'] == 2:
        print('无封禁，有怀疑')
        newParams["stage"] = 2
        for windowType in [0, 1]:
            if(windowType == 0): # 时间窗口
                for windowsSize in TIME_WIN_SIZE:
                    dataset_time = []
                    line_data_origin = freAnalyseLine(fileName, windowType, targetType, selectedTargets, beginTime, endTime, windowsSize)
                    line_data = {} # 更好格式的line_data
                    for item in line_data_origin.keys():
                        if(item not in line_data.keys()):
                            line_data[item] = []
                        for subitem in line_data_origin[item]:
                            for subsubitem in subitem: # subsubitem是三元组
                                line_data[ip].append([subsubitem[0], float(subsubitem[1]), int(subsubitem[2])])
                    for item in line_data.keys():
                        for subitem in line_data[item]: # subitem是三元组
                            dataset_time.append(subitem)

                    dataset = pd.DataFrame(dataset_time, columns=['time', 'frequency', 'status'])

                    line_location = dataset[dataset['status'] == 2]['frequency'].min()
                    print('linelocation:', line_location)
                    dataset = dataset.dropna(subset=['frequency'])
                    df_up = dataset[dataset['frequency'] > line_location - 1]
                    timeW[windowsSize] = [(df_up['status'].groupby(df_up['status']).count().loc[2]) / len(df_up) , line_location]

            else: # 次数窗口
                for windowSize in NUMBER_WIN_SIZE:
                    print(windowSize)
                    dataset_number = []
                    line_data_origin = freAnalyseLine(fileName, windowType, targetType, selectedTargets, beginTime, endTime, windowSize)
                    line_data = {}
                    for ip in line_data_origin.keys():
                        if(ip not in line_data.keys()):
                            line_data[ip] = []
                        for item in line_data_origin[ip]:
                            for threes in item:
                                line_data[ip].append([threes[0], float(threes[1]), int(threes[2])])
                    for ip in line_data.keys():
                        for threes in line_data[ip]:
                            dataset_number.append(threes)
                    dataset = pd.DataFrame(dataset_number, columns=['time', 'frequency', 'status'])

                    line_location = dataset[dataset['status'] == 2]['frequency'].max()
                    print('linelocation:', line_location)

                    dataset = dataset.dropna(subset=['frequency'])
                    df_down = dataset[dataset['frequency'] < line_location + 1]
                    numberW[windowSize] = [df_down['status'].groupby(df_down['status']).count().loc[2] / len(df_down), line_location]

        print('timeW: ', timeW)
        print('numberW: ', numberW)
        # newParams = {}# {"时间窗口": [], "次数窗口":[]}
        temp = 0
        for idx in timeW.keys():
            if(timeW[idx][0] > temp): 
                temp = timeW[idx][0]
                # newParams['newWindowType'] = 0
                # 窗口大小， 封禁百分比， 推测的阈值
                newParams["newTimeWindow"] = int(idx)
                newParams['newTimeMix'] = (timeW[idx][0])
                newParams["newTimeBan"] = (timeW[idx][1])
        temp = 0
        for idx in numberW.keys():
            if(numberW[idx][0] > temp): 
                temp = numberW[idx][0]
                newParams["newNumberWindow"] = int(idx)
                newParams['newNumberMix'] = (numberW[idx][0])
                newParams["newNumberBan"] = (numberW[idx][1])
                # newParams = {'newWindowType': 1, 'newWindowSize': 500}
        return HttpResponse(json.dumps(newParams), content_type="application/json")

    # 日志中有封禁状态
    if paramsinfo['frequency']['stage'] == 3:
        newParams["stage"] = 3
        for windowType in [0, 1]: # 遍历windowType
            if(windowType == 0): # 时间窗口
                # 遍历windowSize
                for windowSize in TIME_WIN_SIZE:
                    print("windowSize:", windowSize)
                    # 把多ip/account的三元组汇总到一起
                    dataset_time = []
                    # 这里对每个windowType & windowSize
                    line_data_origin = freAnalyseLine(fileName, windowType, targetType, selectedTargets, beginTime, endTime, windowSize)
                    # line_data是缝合断开的三元组(字典)
                    line_data = {}
                    for item in line_data_origin.keys():
                        if(item not in line_data.keys()):
                            line_data[item] = []
                        for subitem in line_data_origin[item]:
                            for subsubitem in subitem: # subsubitem是三元组
                                line_data[item].append([subsubitem[0], float(subsubitem[1]), int(subsubitem[2])])
                    # item 是ip/account
                    for item in line_data.keys():
                        # subitem是三元组
                        for subitem in line_data[item]:
                            dataset_time.append(subitem)

                    dataset = pd.DataFrame(dataset_time, columns=['time', 'frequency', 'status'])
                    # 选取status为3时的frequency里的最小的值，作为line_location
                    line_location = dataset[dataset['status'] == 3]['frequency'].min()
                    # 去掉frequency字段有NaN的行
                    dataset = dataset.dropna(subset=['frequency'])
                    # 只保留frequency大于等于line_location的值
                    df_up = dataset[dataset['frequency'] > line_location - 1]
                    # 分别计算出每个status对应的数目，选择其中为3的数目，再除以总数，作为封禁的概率
                    timeW[windowSize] = [(df_up['status'].groupby(df_up['status']).count().loc[3]) / len(df_up) , line_location]

            else: # 次数窗口
                for windowSize in NUMBER_WIN_SIZE:
                    dataset_number = []
                    line_data_origin = freAnalyseLine(fileName, windowType, targetType, selectedTargets, beginTime, endTime, windowSize)
                    line_data = {}
                    for ip in line_data_origin.keys():
                        if(ip not in line_data.keys()):
                            line_data[ip] = []
                        for item in line_data_origin[ip]:
                            for threes in item:
                                line_data[ip].append([threes[0], float(threes[1]), int(threes[2])])
                    for ip in line_data.keys():
                        for threes in line_data[ip]:
                            dataset_number.append(threes)

                    dataset = pd.DataFrame(dataset_number, columns=['time', 'frequency', 'status'])
                    line_location = dataset[dataset['status'] == 3]['frequency'].max()
                    print('linelocation:', line_location)
                    dataset = dataset.dropna(subset=['frequency'])
                    df_down = dataset[dataset['frequency'] < line_location + 1]
                    numberW[windowSize] = [df_down['status'].groupby(df_down['status']).count().loc[3] / len(df_down), line_location]

        print('timeW: ', timeW)
        print('numberW: ', numberW)
        # newParams = {}# {"时间窗口": [], "次数窗口":[]}
        temp = 0
        for idx in timeW.keys():
            if timeW[idx][0] > temp:
                temp = timeW[idx][0]
                # newParams['newWindowType'] = 0
                # 窗口大小， 封禁百分比， 推测的阈值
                newParams["newTimeWindow"] = int(idx)
                newParams['newTimeMix'] = (timeW[idx][0])
                newParams["newTimeBan"] = (timeW[idx][1])
        temp = 0
        for idx in numberW.keys():
            if numberW[idx][0] > temp:
                temp = numberW[idx][0]
                newParams["newNumberWindow"] = int(idx)
                newParams['newNumberMix'] = (numberW[idx][0])
                newParams["newNumberBan"] = (numberW[idx][1])
                # newParams = {'newWindowType': 1, 'newWindowSize': 500}
        print(newParams)
        return HttpResponse(json.dumps(newParams), content_type="application/json")

#### 安全怀疑封禁参数待修改!!! ####
# 自动获取间隔参数
def interval_params(request):
    print('正在获取interval参数...')
    fileName = request.POST.get('fileName')  # 获取解析文件名
    # windowType = int(request.POST.get('windowType', 0))  # 获取窗口类型，默认为0(时间窗口)
    targetType = int(request.POST.get('targetType', 0))  # 获取观察对象，默认为0(ip)
    selectedTargets = []  # 获取目标，默认为all(全部目标）
    # print(selectedTargets)
    
    beginTime = 0 #int(request.POST.get('beginTime', 0))  # 开始时间，默认为0
    endTime = -1 #int(request.POST.get('endTime', -1))  # 结束时间，默认为-1(最大时间值）
    # windowSize = int(request.POST.get('windowSize', 200))  # 特征窗口大小，默认为200
    timeW = {}  
    numberW = {}

    baseDir = os.path.dirname(os.path.abspath(__name__))
    paraminfo_path = os.path.join(baseDir, 'tmp', 'param', fileName)
    with open(paraminfo_path) as f:
      paramsinfo = json.load(f)
    newParams = {}
    # 日志中无封禁，无怀疑
    if(paramsinfo['interval']['stage'] == 1):
      newParams["newNumberWindow"] = 1
      return HttpResponse(json.dumps(newParams), content_type="application/json")

    # 日志中有封禁
    if(paramsinfo['frequency']['stage'] == 2):
      print('有封禁')
      newParams["stage"] = 2
      for windowType in [0, 1]:
          if(windowType == 0):#时间窗口
              for windowSize in TIME_WIN_SIZE:
                  print(windowSize)
                  dataset_time = []
                  line_data_origin = intervalAnalyseLine(fileName, windowType, targetType, selectedTargets, beginTime, endTime, windowSize)
                  line_data = {}
                  for ip in line_data_origin.keys():
                      if(ip not in line_data.keys()):
                          line_data[ip] = []
                      for item in line_data_origin[ip]:
                          for threes in item:
                              line_data[ip].append([threes[0], float(threes[1]), int(threes[2])])
                  # print(line_data)
                  # quit()

                  for ip in line_data.keys():
                      for threes in line_data[ip]:
                          dataset_time.append(threes)
                  # print(dataset_time[:10])
                  dataset = pd.DataFrame(dataset_time, columns=['time', 'frequency', 'status'])
                  
                  line_location = dataset[dataset['status'] == 2]['frequency'].max()
                  # print('linelocation', line_location)
                  dataset = dataset.dropna(subset=['frequency'])
                  df_down = dataset[dataset['frequency'] < line_location + 1]
                  # print(df_up['status'].groupby(df_up['status']).count())
                  # timeW[windowSize] = [len(df_up) - df_up['status'].groupby(df_up['status']).count().loc[1] , line_location]
                  timeW[windowSize] = [(df_down['status'].groupby(df_down['status']).count().loc[2]) / len(df_down) , line_location]
          else:
              for windowSize in NUMBER_WIN_SIZE:
                  print(windowSize)
                  dataset_number = []
                  line_data_origin = intervalAnalyseLine(fileName, windowType, targetType, selectedTargets, beginTime, endTime, windowSize)
                  line_data = {}
                  for ip in line_data_origin.keys():
                      if(ip not in line_data.keys()):
                          line_data[ip] = []
                      for item in line_data_origin[ip]:
                          for threes in item:
                              line_data[ip].append([threes[0], float(threes[1]), int(threes[2])])
                  for ip in line_data.keys():
                      for threes in line_data[ip]:
                          dataset_number.append(threes)
                  dataset = pd.DataFrame(dataset_number, columns=['time', 'frequency', 'status'])
                  # print(dataset[:10])

                  # tmp = dataset[dataset['status'] == 2]
                  # print(tmp[:10])
                  # print(tmp[-10:])

                  line_location = dataset[dataset['status'] == 2]['frequency'].max()
                  # print(line_location)
                  # quit()
                  dataset = dataset.dropna(subset=['frequency'])
                  df_down = dataset[dataset['frequency'] < line_location + 1]
                  # print(df_down['status'].groupby(df_down['status']).count())
                  # quit()
                  # numberW[windowSize] = [len(df_down) - df_down['status'].groupby(df_down['status']).count().loc[1] , line_location]
                  numberW[windowSize] = [df_down['status'].groupby(df_down['status']).count().loc[2] / len(df_down), line_location]

      print('timeW:', timeW)
      print('numberW', numberW)
      # newParams = {}# {"时间窗口": [], "次数窗口":[]}
      temp = 0
      for idx in timeW.keys():
          if(timeW[idx][0] > temp): 
              temp = timeW[idx][0]
              # newParams['newWindowType'] = 0
              # 窗口大小， 封禁百分比， 推测的阈值
              newParams["newTimeWindow"] = int(idx)
              newParams['newTimeMix'] = (timeW[idx][0])
              newParams["newTimeBan"] = (timeW[idx][1])
      temp = 0
      for idx in numberW.keys():
          if(numberW[idx][0] > temp): 
              temp = numberW[idx][0]
              newParams["newNumberWindow"] = int(idx)
              newParams['newNumberMix'] = (numberW[idx][0])
              newParams["newNumberBan"] = (numberW[idx][1])
              # newParams = {'newWindowType': 1, 'newWindowSize': 500}
      return HttpResponse(json.dumps(newParams), content_type="application/json")

    # 日志中无封禁，有怀疑
    if(paramsinfo['frequency']['stage'] == 3):
      print('无封禁，有怀疑')
      newParams["stage"] = 3
      for windowType in [0, 1]:
          if(windowType == 0):#时间窗口
              for windowSize in TIME_WIN_SIZE:
                  dataset_time = []
                  line_data_origin = intervalAnalyseLine(fileName, windowType, targetType, selectedTargets, beginTime, endTime, windowSize)
                  line_data = {}
                  for ip in line_data_origin.keys():
                      if(ip not in line_data.keys()):
                          line_data[ip] = []
                      for item in line_data_origin[ip]:
                          for threes in item:
                              line_data[ip].append([threes[0], float(threes[1]), int(threes[2])])
                  # print(line_data)
                  # quit()

                  for ip in line_data.keys():
                      for threes in line_data[ip]:
                          dataset_time.append(threes)
                  # print(dataset_time[:10])
                  dataset = pd.DataFrame(dataset_time, columns=['time', 'frequency', 'status'])
                  
                  line_location = dataset[dataset['status'] == 1]['frequency'].max()
                  # print('linelocation', line_location)
                  dataset = dataset.dropna(subset=['frequency'])
                  df_down = dataset[dataset['frequency'] < line_location + 1]
                  # print(df_up['status'].groupby(df_up['status']).count())
                  # timeW[windowSize] = [len(df_up) - df_up['status'].groupby(df_up['status']).count().loc[1] , line_location]
                  timeW[windowSize] = [(df_down['status'].groupby(df_down['status']).count().loc[1]) / len(df_down) , line_location]
          else:
              for windowSize in NUMBER_WIN_SIZE:
                  print(windowSize)
                  dataset_number = []
                  line_data_origin = intervalAnalyseLine(fileName, windowType, targetType, selectedTargets, beginTime, endTime, windowSize)
                  line_data = {}
                  for ip in line_data_origin.keys():
                      if(ip not in line_data.keys()):
                          line_data[ip] = []
                      for item in line_data_origin[ip]:
                          for threes in item:
                              line_data[ip].append([threes[0], float(threes[1]), int(threes[2])])
                  for ip in line_data.keys():
                      for threes in line_data[ip]:
                          dataset_number.append(threes)
                  dataset = pd.DataFrame(dataset_number, columns=['time', 'frequency', 'status'])
                  # print(dataset[:10])

                  # tmp = dataset[dataset['status'] == 2]
                  # print(tmp[:10])
                  # print(tmp[-10:])

                  line_location = dataset[dataset['status'] == 1]['frequency'].max()
                  # print(line_location)
                  # quit()
                  dataset = dataset.dropna(subset=['frequency'])
                  df_down = dataset[dataset['frequency'] < line_location + 1]
                  # print(df_down['status'].groupby(df_down['status']).count())
                  # quit()
                  # numberW[windowSize] = [len(df_down) - df_down['status'].groupby(df_down['status']).count().loc[1] , line_location]
                  numberW[windowSize] = [df_down['status'].groupby(df_down['status']).count().loc[1] / len(df_down), line_location]

      print('timeW:', timeW)
      print('numberW', numberW)
      # newParams = {}# {"时间窗口": [], "次数窗口":[]}
      temp = 0
      for idx in timeW.keys():
          if(timeW[idx][0] > temp): 
              temp = timeW[idx][0]
              # newParams['newWindowType'] = 0
              # 窗口大小， 封禁百分比， 推测的阈值
              newParams["newTimeWindow"] = int(idx)
              newParams['newTimeMix'] = (timeW[idx][0])
              newParams["newTimeBan"] = (timeW[idx][1])
      temp = 0
      for idx in numberW.keys():
          if(numberW[idx][0] > temp): 
              temp = numberW[idx][0]
              newParams["newNumberWindow"] = int(idx)
              newParams['newNumberMix'] = (numberW[idx][0])
              newParams["newNumberBan"] = (numberW[idx][1])
              # newParams = {'newWindowType': 1, 'newWindowSize': 500}
      return HttpResponse(json.dumps(newParams), content_type="application/json")

# 自动获取休眠时长参数
def rest_params(request):
    print('正在获取rest参数...')
    fileName = request.POST.get('fileName')  # 获取解析文件名
    targetType = int(request.POST.get('targetType', 0))  # 获取观察对象，默认为0(ip)
    selectedTargets = ['195.221.68.34', '195.221.22.21', '92.168.1.5', '225.168.2.5', '192.168.1.5', '195.221.56.8', '229.21.36.85', '19.168.89.5', '225.168.6.8', '225.168.9.52', '225.168.1.6'] # 获取目标，默认为all(全部目标）
    beginTime = (request.POST.get('beginTime', ''))  # 开始时间，默认为0
    endTime = (request.POST.get('endTime', ''))  # 结束时间，默认为-1(最大时间值）
    
    # 将beginTime和endTime转化为数值型
    baseDir = os.path.dirname(os.path.abspath(__name__))

    paraminfo_path = os.path.join(baseDir, 'tmp', 'param', fileName)
    with open(paraminfo_path) as f:
      paramsinfo = json.load(f)
    newParams = {}
    if(paramsinfo['rest']['stage'] == 1):
      newParams["deltaTime"] = 1
      return HttpResponse(json.dumps(newParams), content_type="application/json")

    if(paramsinfo['frequency']['stage'] == 3):
      print('无封禁，有怀疑')
      newParams["stage"] = 3
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

      deltaTimeW = {}
      for deltaTime in range(7200, 36000, 3600):
          dataset_time = []
          line_data_origin = restDataLine(fileName, deltaTime, targetType, selectedTargets, beginTime, endTime,beginZeroTime)
          line_data = {}
          for ip in line_data_origin.keys():
              if(ip not in line_data.keys()):
                  line_data[ip] = []
              for threes in line_data_origin[ip]:
                  # for threes in item:
                  line_data[ip].append([threes[0], float(threes[1]), int(threes[2])])
          # print(line_data)
          # quit()

          for ip in line_data.keys():
              for threes in line_data[ip]:
                  dataset_time.append(threes)
          dataset = pd.DataFrame(dataset_time, columns=['time', 'rest', 'status'])
          # print(dataset[:10])
          # quit()
          line_location = dataset[dataset['status'] == 1]['rest'].min()
          # print('linelocation', line_location)
          dataset = dataset.dropna(subset=['rest'])
          df_up = dataset[dataset['rest'] > line_location - 1]
          # print(df_up['status'].groupby(df_up['status']).count())
          # quit()
          deltaTimeW[deltaTime] = [(df_up['status'].groupby(df_up['status']).count().loc[1]) / len(df_up) , line_location]

      print('deltaTimeW:', deltaTimeW)
      # newParams = {}# {"时长窗口": []}
      temp = 0
      for idx in deltaTimeW.keys():
          if(deltaTimeW[idx][0] > temp): 
              temp = deltaTimeW[idx][0]
              # newParams['newWindowType'] = 0
              # 窗口大小， 封禁百分比， 推测的阈值
              newParams["newDeltaTimeWindow"] = int(idx)
              newParams['newDeltaTimeMix'] = (deltaTimeW[idx][0])
              newParams["newDeltaTimeBan"] = (deltaTimeW[idx][1])
              # newParams = {'newWindowType': 1, 'newWindowSize': 500}
      return HttpResponse(json.dumps(newParams), content_type="application/json")

# 自动获取多样性参数
def diversity_params(request):
    print('正在获取diversity参数...')
    fileName = request.POST.get('fileName')  # 获取解析文件名
    # windowType = int(request.POST.get('windowType', 0))  # 获取窗口类型，默认为0(时间窗口)
    targetType = int(request.POST.get('targetType', 0))  # 获取观察对象，默认为0(ip)
    selectedTargets = []  # 获取目标，默认为all(全部目标）
    # print(selectedTargets)
    
    beginTime = 0 #int(request.POST.get('beginTime', 0))  # 开始时间，默认为0
    endTime = -1 #int(request.POST.get('endTime', -1))  # 结束时间，默认为-1(最大时间值）
    # windowSize = int(request.POST.get('windowSize', 200))  # 特征窗口大小，默认为200
    
    baseDir = os.path.dirname(os.path.abspath(__name__))
    paraminfo_path = os.path.join(baseDir, 'tmp', 'param', fileName)
    with open(paraminfo_path) as f:
      paramsinfo = json.load(f)
    newParams = {}
    if(paramsinfo['diversity']['stage'] == 1):
      newParams["windowType"] = 1
      return HttpResponse(json.dumps(newParams), content_type="application/json")

    timeW = {}  
    numberW = {}
    for windowType in [0, 1]:
        if(windowType == 0):#时间窗口
            for windowSize in TIME_WIN_SIZE:
                dataset_time = []
                line_data_origin = diversityAnalyseLine(fileName, windowType, targetType, selectedTargets, beginTime, endTime, windowSize)
                line_data = {}
                for ip in line_data_origin.keys():
                    if(ip not in line_data.keys()):
                        line_data[ip] = []
                    for item in line_data_origin[ip]:
                        for threes in item:
                            line_data[ip].append([threes[0], float(threes[1]), int(threes[2])])
                # print(line_data)
                # quit()

                for ip in line_data.keys():
                    for threes in line_data[ip]:
                        dataset_time.append(threes)
                # print(dataset_time[:10])
                dataset = pd.DataFrame(dataset_time, columns=['time', 'diversity', 'status'])
                
                line_location = dataset[dataset['status'] == 2]['diversity'].max()
                # print('linelocation', line_location)
                dataset = dataset.dropna(subset=['diversity'])
                df_down = dataset[dataset['diversity'] < line_location + 1]
                # print(df_down['status'].groupby(df_down['status']).count())
                # timeW[windowSize] = [len(df_down) - df_down['status'].groupby(df_down['status']).count().loc[1] , line_location]
                timeW[windowSize] = [(df_down['status'].groupby(df_down['status']).count().loc[2]) / len(df_down) , line_location]
        else:
            for windowSize in NUMBER_WIN_SIZE:
                print(windowSize)
                dataset_number = []
                line_data_origin = diversityAnalyseLine(fileName, windowType, targetType, selectedTargets, beginTime, endTime, windowSize)
                line_data = {}
                for ip in line_data_origin.keys():
                    if(ip not in line_data.keys()):
                        line_data[ip] = []
                    for item in line_data_origin[ip]:
                        for threes in item:
                            line_data[ip].append([threes[0], float(threes[1]), int(threes[2])])
                for ip in line_data.keys():
                    for threes in line_data[ip]:
                        dataset_number.append(threes)
                dataset = pd.DataFrame(dataset_number, columns=['time', 'diversity', 'status'])
                # print(dataset[:10])

                # tmp = dataset[dataset['status'] == 2]
                # print(tmp[:10])
                # print(tmp[-10:])

                line_location = dataset[dataset['status'] == 2]['diversity'].max()
                # print(line_location)
                # quit()
                dataset = dataset.dropna(subset=['diversity'])
                df_down = dataset[dataset['diversity'] < line_location + 1]
                # print(df_down['status'].groupby(df_down['status']).count())
                # quit()
                # numberW[windowSize] = [len(df_down) - df_down['status'].groupby(df_down['status']).count().loc[1] , line_location]
                numberW[windowSize] = [df_down['status'].groupby(df_down['status']).count().loc[2] / len(df_down), line_location]

    print('timeW:', timeW)
    print('numberW', numberW)
    # newParams = {}# {"时间窗口": [], "次数窗口":[]}
    temp = 0
    for idx in timeW.keys():
        if(timeW[idx][0] > temp): 
            temp = timeW[idx][0]
            # newParams['newWindowType'] = 0
            # 窗口大小， 封禁百分比， 推测的阈值
            newParams["newTimeWindow"] = int(idx)
            newParams['newTimeMix'] = (timeW[idx][0])
            newParams["newTimeBan"] = (timeW[idx][1])
    temp = 0
    for idx in numberW.keys():
        if(numberW[idx][0] > temp): 
            temp = numberW[idx][0]
            newParams["newNumberWindow"] = int(idx)
            newParams['newNumberMix'] = (numberW[idx][0])
            newParams["newNumberBan"] = (numberW[idx][1])
            # newParams = {'newWindowType': 1, 'newWindowSize': 500}
    return HttpResponse(json.dumps(newParams), content_type="application/json")