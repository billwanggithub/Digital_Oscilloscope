import easygui as g
import csv
import matplotlib.pyplot as plt
import numpy as np

CH1 = 1
CH2 = 2
CH3 = 4
CH4 = 8 

class Waveform:
    def __init__(self, fn):
        # self.CH1 = 1
        # self.CH2 = 2
        # self.CH3 = 4
        # self.CH4 = 8        
        self.filename = fn
        self.opencorrect = False
        self.sample_time = 0
        self.time_start = 0
        self.time_end = 0
        self.time = []
        self.ch = [[],[],[],[]]
        self.get_info()

    def get_info(self):
        line_count = 0
        with open(self.filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')  
            for row in csv_reader:
                if line_count == 0:
                    if row[0] != "Model" and row[1]!="MDO4034C":
                        print("Not Corrent Model,MDO4034C waveform file!!")
                        break
                    else:
                        self.opencorrect = True
                if line_count > 30:
                    break
                if (len(row) != 0):
                    if row[0] == "Sample Interval":
                        self.sample_time = float(row[1]) 
                    if row[0] == "Record Length":
                        record_cnt = float(row[1])
                        self.total_time = record_cnt * self.sample_time                         
                    if row[0] == "TIME": 
                        #read next line
                        data = next(csv_reader)
                        self.time_start = float(data[0])
                        self.time_end = self.time_start + self.total_time - self.sample_time                        
                line_count += 1 

        print("sampling time=", self.sample_time)  
        print("total time=", self.total_time) 
        print("Start Time= %2.8f End Time =  %2.8f" % (self.time_start, self.time_end))

    def get_ch(self, start_time, end_time, chnum):
        data_cnt = 0
        time_now = 0
        time_start = max(start_time, self.time_start)
        time_end = min(end_time, self.time_end)
        print("Porcess from %2.8f To %2.8f" % (time_start, time_end))

        #f1 = open('ch1.csv', 'w')
        with open(self.filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')  
            for row in csv_reader:  
                if (len(row)> 0):
                    # if data_cnt >= 100:
                    #     break    
                    if time_now > time_end:
                        break   
                    if data_cnt >= 1:
                        time_now = float(row[0])
                        if (time_now >= time_start):
                            self.time.append(time_now)
                            if (chnum & 1) == 1 :
                                self.ch[0].append(float(row[1]))
                            if (chnum & 2) == 2 :
                                self.ch[1].append(float(row[2]))
                            if (chnum & 4) == 4 :
                                self.ch[2].append(float(row[3]))
                            if (chnum & 8) == 8 :
                                self.ch[3].append(float(row[4]))

                        data_cnt += 1
                    if (data_cnt > 0) and (data_cnt % 100000) == 0:
                        print("data number read = %d time = %f" % (data_cnt, time_now))                            
                    if row[0] == "TIME" :
                        data_cnt = 1                                                                         
        print("%d data processd" % (len(self.time)))

    # def __str__(self):
    #     return 'Account({0}, {1}, {2})'.format(
    #         self.name, self.number, self.balance)    

    # digital the analog waveform
    def convert_digital(self, threshold, timein, datain , dataout) :
        data01 = 0
        for val in datain :
            if val >= threshold:
                data01 = 1
            else:
                data01 = 0            
            dataout.append(data01)

    # calculate duty of input analog waveform, timeout and dataout is saved as value changed list
    def decode_duty(self, sample_time, threshold, timein, datain , timeout, dataout) :
        data_cnt = 0 # input list number
        data_old = 0 # old value
        period = 0.0
        time_now = 0    
        time01 = 0.0
        time10 = 0.0
        duty = 0.0
        data01 = 0
        l2hcnt = 0 #number of transition from low to high
        for val in datain :
            time_now = timein[data_cnt] 
            if val >= threshold:
                data01 = 1
            else:
                data01 = 0

            if data_cnt > 0 :           
                # 0 -> 1, calculate period value
                if data01 > data_old:                                
                    if time01 == 0  : 
                        time01 = time_now 
                        #first transition detected
                        if l2hcnt == 0 : 
                            timeout.append(timein[0])
                            dataout.append(0)
                        timeout.append(time01 - sample_time)
                        dataout.append(duty)                                                                      
                    else :
                        period = time_now - time01
                        duty = (time10 - time01) / period 
                        #save old value
                        timeout.append(time01)
                        dataout.append(duty)                   
                        #save old value before dt
                        timeout.append(time_now-sample_time)
                        dataout.append(duty)      
                        #update time01 and time10     
                        time01 = time_now 
                        time10 = time_now
                    l2hcnt += 1
                # 1 -> 0, latch the time from high to low
                elif data01 < data_old :
                    time10 = time_now 

                # if (check_zero== 1) and (period > 0) and ((time_now - time01) >= (period *2)):
                #     #print("check_zero time =", time_now)
                #     duty = (time10 - time01) / period
                #     timeout.append(time01)
                #     dataout.append(duty) 
                #     timeout.append(time01 + period)
                #     dataout.append(duty)     
                #     timeout.append(time01 + period + sample_time)
                #     dataout.append(0)                     
                #     duty = 0    
                #     time01 = 0
                #     time10 = 0             
                #     check_zero = 0   

                data_old = data01               
            data_cnt += 1

# https://matplotlib.org/3.1.3/gallery/misc/cursor_demo_sgskip.html
class Cursor(object):
    def __init__(self, ax):
        self.ax = ax
        self.lx = ax.axhline(color='k')  # the horiz line
        self.ly = ax.axvline(color='k')  # the vert line

        # text location in axes coords
        self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)

    def mouse_move(self, event):
        if not event.inaxes:
            return

        x, y = event.xdata, event.ydata
        # update the line positions
        self.lx.set_ydata(y)
        self.ly.set_xdata(x)

        self.txt.set_text('x=%1.2f, y=%1.2f' % (x, y))
        self.ax.figure.canvas.draw()

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
        self.txt.set_text('x=%1.8f, y=%1.8f' % (x, y))
        self.txt.set_position((x,y))
        self.ax.figure.canvas.draw_idle()

def get_filename():
    fn= g.fileopenbox(default="*.csv")
    return fn


##########################################################################
#         Test Program
##########################################################################
t_duty = []
duty = []
digital_data = []
filename = get_filename()
print("filename = ",filename)

wfm =Waveform(filename)

# Select channels
msg = "Select Channels"
title = "Oscilloscope Waveform Viewer"
listOfOptions = ["CH1", "CH2", "CH3" , "CH4"]
ch_choice = g.multchoicebox(msg , title, listOfOptions)
ch_map = {'CH1':CH1, 'CH2':CH2, 'CH3':CH3, 'CH4':CH4}
ch_sel = 0
print("Channels selected:")
for ch in ch_choice:
    ch_sel |= ch_map[ch]
    print("%s " % (ch))

# Select time range
msg = "Enter the Waveform Start/TIme to Show"
title = "Oscilloscope Waveform Viewer"
fieldNames = ["Start TIme","End Time"]
fieldValues = [str(wfm.time_start), str(wfm.time_end)]  # we start with defalut values
fieldValues = g.multenterbox(msg,title, fieldNames, fieldValues)
time_start = float(fieldValues[0])
time_end = float(fieldValues[1])

time_start = max(time_start, wfm.time_start)
time_end = min(time_end, wfm.time_end)
g.msgbox("Process waveform from %fs to %fs" % (time_start, time_end))

# extract selected channels
wfm.get_ch(time_start, time_end, ch_sel)

# calculate the duty cycles
# wfm.convert_digital(10,wfm.time, wfm.ch[0], digital_data)
# wfm.decode_duty(wfm.sample_time, 10, wfm.time, wfm.ch[0], t_duty, duty)
print("Done!!")

# get X limit
msg = "Enter the X/Y Axis Limits (X = %fs to %fs)" % (time_start, time_end)
title = "Oscilloscope Waveform Viewer"
fieldNames = ["X Start TIme","X End Time","CH1 Low","CH1 High","CH2 Low","CH2 High","CH3 Low","CH3 High","CH4 Low","CH4 High"]
fieldValues = [str(time_start), str(time_end), 0, 12, 0, 12, 0, 12, 0, 12 ]  # we start with defalut values
fieldValues = g.multenterbox(msg,title, fieldNames, fieldValues)
#check input raege
ylim_low = [0,0,0,0]
ylim_high = [0,0,0,0]
if float(fieldValues[1]) > float(fieldValues[0]) :
    xlim_low = float(fieldValues[0])
    xlim_high= float(fieldValues[1])  
xlim_low = max(xlim_low, time_start)
xlim_high= min(xlim_high, time_end)
for ch in [0,1,2,3]:
    ylim_low[ch] = float(fieldValues[ch * 2 + 2])
    ylim_high[ch]= float(fieldValues[ch * 2 + 3])  
print("Set X Axis from %fs to %fs" % (xlim_low, xlim_high))

fig,ax = plt.subplots(4, 1, figsize=(15,8)) 
#plot analog waveform
for ch in [0,1,2,3]:
    if len(wfm.ch[ch]) > 0:
        ax[ch].plot(wfm.time,wfm.ch[ch])  

# ax[0].plot(wfm.time, digital_data)
# ax[1].plot(wfm.time, digital_data)
# ax[1].plot(t_duty, duty)     

# Set Axis Limits

cursor_snap = [0,0,0,0]
for ch in [0,1,2,3]:
    ax[ch].set_xlim([xlim_low , xlim_high])  
    ax[ch].set_ylim([ylim_low[ch] , ylim_high[ch]]) 
    cursor_snap[ch] = SnaptoCursor(ax[ch],wfm.time,wfm.ch[ch])
    fig.canvas.mpl_connect('motion_notify_event', cursor_snap[ch].mouse_move)
# Snap Cursor
# cursor0 = SnaptoCursor(ax[0],wfm.time,wfm.ch[0])
# fig.canvas.mpl_connect('motion_notify_event', cursor0.mouse_move)
# cursor1 = SnaptoCursor(ax[1],wfm.time,wfm.ch[1])
# fig.canvas.mpl_connect('motion_notify_event', cursor1.mouse_move)
# cursor2 = SnaptoCursor(ax[2],wfm.time,wfm.ch[2])
# fig.canvas.mpl_connect('motion_notify_event', cursor2.mouse_move)
# cursor3 = SnaptoCursor(ax[3],wfm.time,wfm.ch[3])
# fig.canvas.mpl_connect('motion_notify_event', cursor3.mouse_move)            
# print("type:",type(cursor1))

plt.tight_layout()

while True:
    fig.show()
    fieldValues = [str(xlim_low ), str(xlim_high), 
        ylim_low[0], ylim_high[0], ylim_low[1], ylim_high[1], ylim_low[2], ylim_high[2], ylim_low[3], ylim_high[3]]  # we start with defalut values
    fieldValues = g.multenterbox(msg,title, fieldNames, fieldValues)
    #check input raege    
    if float(fieldValues[1]) > float(fieldValues[0]) :
        xlim_low = float(fieldValues[0])
        xlim_high= float(fieldValues[1])  
    xlim_low = max(xlim_low, time_start)
    xlim_high= min(xlim_high, time_end)
    for ch in [0,1,2,3]:
        ylim_low[ch] = float(fieldValues[ch * 2 + 2])
        ylim_high[ch]= float(fieldValues[ch * 2 + 3])     

    for ch in [0,1,2,3]:
        ax[ch].set_xlim([xlim_low , xlim_high])  
        ax[ch].set_ylim([ylim_low[ch] , ylim_high[ch]]) 

    print("Set X Axis from %fs to %fs" % (xlim_low, xlim_high))
