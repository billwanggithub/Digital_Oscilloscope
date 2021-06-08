import csv
import tkinter as tk
#from matplotlib import pyplot
#from matplotlib.widgets import Cursor
import matplotlib.widgets as widgets
import matplotlib.pyplot as plt
import numpy as np

class SnaptoCursor(object):
    def __init__(self, ax, x, y):
        self.ax = ax
        self.ly = ax.axvline(color='k', alpha=0.2)  # the vert line
        self.marker, = ax.plot([0],[0], marker="o", color="crimson", zorder=3) 
        self.x = x
        self.y = y
        self.txt = ax.text(0.7, 0.9, '')

    def mouse_move(self, event):
        if not event.inaxes: return
        x, y = event.xdata, event.ydata
        indx = np.searchsorted(self.x, [x])[0]
        x = self.x[indx]
        y = self.y[indx]
        self.ly.set_xdata(x)
        self.marker.set_data([x],[y])
        self.txt.set_text('x=%1.6f, y=%1.6f' % (x, y))
        self.txt.set_position((x,y))
        self.ax.figure.canvas.draw_idle()

def calc_duty(tinlist, inlist , toutlist, outlist) :
    list_cnt = 0 # input list number
    list_old = 0 # old value
    period = 0.0
    time01 = 0.0
    time10 = 0.0
    duty = 0.0
    for val in inlist :
        if list_cnt > 0 :
            # 0 -> 1, latch period value
            if val > list_old:
                period = tinlist[list_cnt] - time01
                duty = (time10 - time01) / period
                toutlist.append(time01)
                outlist.append(duty)       
                #refresh tim01         
                time01 = tinlist[list_cnt] 
            # 1 -> 0, latch the time from high to low
            elif val < list_old :
                time10 = tinlist[list_cnt] 
            list_old = val               
        list_cnt += 1
    return outlist

def show_entry_fields():
    global time_start
    global time_end
    arg1 = e1.get()
    arg2 = e2.get()
    print("Start time: %s\nEnd time: %s" % (arg1, arg2))
    print("Press Commit to continue")
    if arg1 == '':
        time_start = 0
    else:
        time_start = float(arg1)
    if arg2 == '':
        time_start = 0
    else:
        time_end = float(arg2)    

# start time , end time input box
master = tk.Tk()
entry = tk.Entry(master)
tk.Label(master, 
         text="Start Time").grid(row=0)
tk.Label(master, 
         text="End Time").grid(row=1)

e1 = tk.Entry(master)
e2 = tk.Entry(master)

e1.grid(row=0, column=1)
e2.grid(row=1, column=1)
e1.insert(tk.END, '0')
e2.insert(tk.END, '0')

tk.Button(master, text='Commit', command=master.destroy).grid(row=3, column=0, sticky=tk.W, pady=4)
tk.Button(master, text='Set', command=show_entry_fields).grid(row=3, column=1, sticky=tk.W, pady=4)
master.mainloop()


fname='tek0000ALL.csv'
tsample = 0
time_xlow = 0.0
time_xhigh =0.0
cursor1 = 0

time_now = 0.0
threshold = 10.0 #threshold voltage for logic analyzer
data_cnt = 0
dt = tsample * 0.01
v1scale = 0
temp0 = 0.0
temp1 = 0
time = []
va = []
vb = []
vc = []
va_dig = []
vb_dig = []
vc_dig = []
va_duty = []
vb_duty = []
current = []
tduty = []

with open(fname) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    #rows = len(list(csv_reader))
    #print("rows =")
    line_count = 0
    
    f1 = open('ch1.csv', 'w')
    f2 = open('ch2.csv', 'w')
    f3 = open('ch3.csv', 'w')
    f4 = open('ch4.csv', 'w')

    for row in csv_reader:
  
        if (len(row) != 0):
            if row[0] == "Sample Interval":
                tsample = float(row[1]) 
                print("sampling time=", tsample)   
            if row[0] == "Vertical Scale":
                v1scale = float(row[1]) 
                print("ch1 scale=", v1scale)                 
            if data_cnt >= 1:
                if (data_cnt % 500000) == 0:
                    print("data porcessed = ", data_cnt,  " time = ", float(row[0]))    

                time_now = row[0]
                # stop after time_end
                if (float(time_now) > time_end) :
                    break

                if (float(time_now) >= time_start) :        
                    time.append(float(time_now))

                temp0 = float(row[1])
                if temp0 >= threshold :
                    temp1 = 1
                else:
                    temp1 = 0
                if (float(time_now) >= time_start):   
                    va.append(temp0)
                    va_dig.append(temp1)
                    f1.write(time_now + ',' + str(temp0) + ',' + str(temp1) + '\n')

                temp0 = float(row[2])
                if temp0 >= threshold :
                    temp1 = 1
                else:
                    temp1 = 0
                if (float(time_now) >= time_start):   
                    vb.append(temp0)
                    vb_dig.append(temp1)
                    f2.write(time_now + ',' + str(temp0) + ',' + str(temp1) + '\n') 

                data_cnt += 1
            #check if data line begins
            if row[0] == "TIME": 
                data_cnt = 1

        line_count += 1

    calc_duty(time , vb_dig, tduty, vb_duty)
    print('tduty=%1.6f, vb_duty=%1.6f' % (len(tduty), len(vb_duty)))

    print("samples number =", data_cnt - 1)
    f1.close
    f2.close
    f3.close
    f4.close
    print("write data file successfull !!")

    time_xlow = time_start
    time_xhigh = time_end

    fig,ax = plt.subplots(2, 1) 
    ax[0].plot(time,vb )    
    ax[0].plot(time, vb_dig )   
    ax[0].set_xlim([time_xlow , time_xhigh])  

    ax[1].plot(tduty, vb_duty)    
    ax[1].set_xlim([time_xlow , time_xhigh])  
    plt.tight_layout()
    fig.show()

    # cursor = SnaptoCursor(ax[0], time, va)
    # cid =  plt.connect('motion_notify_event', cursor.mouse_move)

    # input box for graph x axis limit
    # change currsor index
    def set_cursor():
        global cursor1
        if cursor1 < 2:
            cursor1 = cursor1 + 1
        else:
            cursor1 = 0
        print("cursor = ", cursor1)

        if cursor1 == 0:
            cursor = SnaptoCursor(ax[0], time, vb) 
        elif cursor1 == 1:
            cursor = SnaptoCursor(ax[0], time, vb_dig)       
        elif cursor1 == 2:
            cursor = SnaptoCursor(ax[1], tduty, vb_duty) 
        cid =  plt.connect('motion_notify_event', cursor.mouse_move)
        plt.show()

    def set_xfit() :
        e21.delete(0, tk.END)
        e22.delete(0, tk.END)
        e21.insert(tk.END, str(time_start))
        e22.insert(tk.END, str(time_end))        
        set_xlimit()

    def set_xlimit() :
        arg1 = e21.get()
        arg2 = e22.get()
        if arg1 == '':
            time_xlow = time_start
        else:
            time_xlow  = float(arg1)
        if arg2 == '':
            time_xhigh  = time_end
        else:
            time_xhigh = float(arg2)       
        print("X Axis Start time: %f\nX End time: %f" % (time_xlow, time_xhigh))            
        ax[0].set_xlim([time_xlow , time_xhigh])
        ax[1].set_xlim([time_xlow , time_xhigh])
        plt.show()

    master2 = tk.Tk()
    master2.title("X Limit")
    tk.Label(master2, 
            text="View Start Time").grid(row=0, column=0)
    tk.Label(master2, 
            text="View End Time").grid(row=1, column=0)

    e21 = tk.Entry(master2)
    e22 = tk.Entry(master2)
    e21.insert(tk.END, str(time_start))
    e22.insert(tk.END, str(time_end))
    e21.grid(row=0, column=1)
    e22.grid(row=1, column=1)

    tk.Button(master2, text='Quit', command=master.quit).grid(row=3, column=0) #, sticky=tk.W, pady=4)
    tk.Button(master2, text='Set', command=set_xlimit).grid(row=3, column=1) #, sticky=tk.W, pady=4)
    tk.Button(master2, text='Fit', command=set_xfit).grid(row=3, column=2) #, sticky=tk.W, pady=4)
    tk.Button(master2, text='Cursor Change', command=set_cursor).grid(row=3, column=3)

    master2.mainloop()
    master2.destroy()
