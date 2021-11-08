import numpy as np
import pandas as pd

# res = {'ip1':{'time':["2021.05.10", "2021.05.12", "2021.05.13"], 'count':[399, 400, 402],'state':[0, 1, 1]},
#        'ip2':{'time':["2022.05.10", "2022.05.12", "2022.05.13"], 'count':[599, 600, 602],'state':[2, 0, 1]}}
# for key in ['ip1', 'ip2']:
#     tmp_time = np.array(res[key]['time']).reshape(-1, 1) # 取出时间列表[1, 2, 3] 然后二维化[[1][2][3]]
#     print(tmp_time)
#     tmp_count = np.array(res[key]['count']).reshape(-1, 1)
#     tmp_state = np.array(res[key]['state']).reshape(-1, 1)
#     tmp = np.concatenate( (tmp_time, tmp_count, tmp_state), axis=1).tolist() # 按行相接
#     print(tmp)

li = [1, 2, 3, 4, 5, 6]
# subLi = li[1 : 2+3]
del li[0]
del li[0]
print(li)


dataset_time = [['2020-12-17 19:41:52', 700, 0], ['2020-12-17 19:42:40', 778, 0], ['2020-12-17 19:43:40', 770, 1],
       ['2020-12-17 19:42:40', 771, 2], ['2020-12-17 19:42:40', 788, 0], ['2020-12-17 19:42:40', 777, 2]]
dataset = pd.DataFrame(dataset_time, columns=['time', 'frequency', 'status'])
print(dataset)
# print(dataset['status'].groupby(dataset['status']).count())
# print(dataset[dataset['status'] == 2]['frequency'].min())
print(dataset.dropna(subset=['frequency']))

