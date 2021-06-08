sr_2 = pd.Series(f, pd.date_range(start='2018-05-01', end='2018-05-9'))# importing pandas as pd
import pandas as pd
 # importing numpy as np
import numpy as np

import matplotlib.pyplot as plt
from timeit import default_timer as timer

dict = {'First Score':[100, 90, np.nan, 95],
        'Second Score': [30, 45, 56, np.nan],
        'Third Score':[np.nan, 40, 80, 98]}

#df = pd.read_csv('ch1.csv')

# numbers = [9, 23, 33, 91, 13]
# players = ["Ron Harper", "Michael Jordan", "Scottie Pippen", "Dennis Rodman", "Luc Longley"]
# df = pd.DataFrame()
# df["number"] = numbers
# df["player"] = players
# df.index = ["PG", "SG", "SF", "PF", "C"]
# print(df.loc[["SG", "SF", "PF"], ["number", "player"]]) # 以索引為準
# print(df.iloc[[1, 2, 3], [0, 1]])                    # 以位置為準

csv_url = "https://storage.googleapis.com/learn_pd_like_tidyverse/gapminder.csv"
csv_file = 'ch1.csv'
print("begin")
# print(df.shape)
# print("=============查看前五列觀測值====================")
# print(df.head())     # 查看前五列觀測值
# print("=============查看末五列觀測值====================")
# print(df.tail())     # 查看末五列觀測值
# print("=============查看資料框的複合資訊====================")
# print(df.info())     # 查看資料框的複合資訊
# print("=============查看數值變數的描述性統計====================")
# print(df.describe()) # 查看數值變數的描述性統計
# print("=============查看資料框的外觀====================")
# print(df.shape)      # 查看資料框的外觀
# print("=================================")
# print(df.index)
# print("=================================")
# print(df.columns)

def read_data(fn, tout, dout): 
    df = pd.read_csv(fn)    
    tout = df["time"].astype(float)
    dout = df["ch1"].astype(float)
    
df = pd.read_csv(csv_file)    
to = df["time"].astype(float)
do = df["ch1"].astype(float)

start = timer()
leng = len(to)
end = timer()
print(to[leng-1] - to[0])
# time_range= df.iloc[[0 leng-1],[0]].values
# print(time_range)
#print(time_start[1] - time_start[0])
plt.plot(to,do)
plt.show()

