import tkinter as tk
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1,2)
x = [1,2,3,4]
y = [1,4,9,16]

a = [1,2,3,4]
b = [11, 20, 9, 15]

c= [1,2,3, 3.5,4]
d = [20, 1, 6,9, 10]

ax[0].plot(x,y)
ax[0].plot(a,b)
plt.show()

ax[0].plot(c,d)
plt.show()
