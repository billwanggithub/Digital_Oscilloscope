import numpy as np, datetime
# # array of zeros and ones interleaved
# x = np.arange(1,3,0.1)
# y = np.arange(3, 1, -0.1)
# condition = ((x >= 1.3) & (x <=2.2))
# yn = np.extract(condition, y)
# print(x)
# print(y)
# print(yn)

a = ()
b = 'z'
c= 'x'
d = (*a, b)
e = (*d , c)
print(e)