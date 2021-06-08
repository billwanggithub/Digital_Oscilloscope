#https://ithelp.ithome.com.tw/articles/10196167
#https://www.itread01.com/article/1533279784.html

import numpy as np
import timeit
import matplotlib.pyplot as plt
from pathlib import Path

ch = [[]] * 5
time = [[]] * 5
# open csv file and save to binary file
#ch = [[] for i in range(4)]
print(ch)
for i in range(4):
    start = timeit.default_timer()
    fn = 'ch%d.csv' % (i+1)
    #check if file exit
    if Path(fn).is_file(): 
        print(fn)
        ch[i]= np.loadtxt(fn, delimiter=',')
        stop = timeit.default_timer()
        print(ch[i])
        print('load Time: ', stop - start)
        start = timeit.default_timer()
        #save to *.npy
        np.save('ch%d' % (i+1), ch[i]) 
        stop = timeit.default_timer()
        print('save Time: ', stop - start) 

fig,ax = plt.subplots(4, 1, figsize=(15,8)) 


for i in range(4):
    start = timeit.default_timer()
    #load binary file
    fn = 'ch%d.npy' % (i+1)
    print(fn)
    myarr = np.load(fn)
    print(len(myarr))
    stop = timeit.default_timer()
    print('load Time: ', stop - start)
    #swap the row and column
    [time[i], ch[i]] = myarr.transpose()
    ax[i].plot(time[i], ch[i])

plt.show()
fig.show()


