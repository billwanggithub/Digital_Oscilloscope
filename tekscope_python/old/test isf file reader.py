from tkinter import filedialog
import matplotlib.pyplot as plt
import sys
import  TEKTRONIX as tek

fn =  filedialog.askopenfilename(initialdir='.', title="Select isf file to open", filetypes = (("isf files","*.isf"),("all files","*.*")))
#fn = "D:\\Temp\\python\\G2072\\FAN_01_V12_DUTY99_startup\\tek0004CH1.isf"
#fn = "D:\\Temp\\python\\G2071\\tek0000CH3.isf"
wfm = tek.TEKTONIX()

#header, xydata = wfm.read_isf(fn)
wfm.read_isf(fn)
if (wfm.error == True):
    sys. exit()

# fn =  filedialog.asksaveasfilename(initialdir='.', title="Select csv file to save", filetypes = (("csv files","*.csv"),("all files","*.*")))   
# print(fn)
# if fn is None:  # ask saveasfile return `None` if dialog closed with "cancel".
#     print("Not select file")
#     sys. exit()
# wfm.save_csv(fn, wfm.xydata)   

fig, ax = plt.subplots()
x = wfm.xydata["XDATA"]
y = wfm.xydata["YDATA"]
ax.plot(x,y)
plt.show()


