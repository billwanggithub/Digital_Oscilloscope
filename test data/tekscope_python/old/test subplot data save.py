# import numpy as np
# import matplotlib.pyplot as plt

# x = np.arange(0,5,0.1)
# y1 = np.sin(2*np.pi*x)
# y2 = np.cos(2*np.pi*x)
# plt.subplot(211)
# plt.plot(x,y1,'b-.')
# plt.subplot(212)
# plt.plot(x,y2,'r--')
# plt.show()

import matplotlib.pyplot as plt
print(plt.style.available)
plt.style.use('seaborn-poster')

lines = plt.plot([1,2,3],[4,5,6],[0,5],[9,10])
plt.show()
i = 0
l1 = []
for line in lines:
    l1.append(lines[i].get_data())
    i += 1
pass

