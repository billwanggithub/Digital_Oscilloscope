#https://codereview.stackexchange.com/questions/91032/parsing-oscilloscope-data-follow-up
#https://tw.tek.com/support/faqs/what-format-isf-file
#https://www.mathworks.com/matlabcentral/mlc-downloads/downloads/submissions/24402/versions/1/previews/isfread.m/index.html?access_key=
import numpy as np
import os.path
import pandas as pd
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
from matplotlib.widgets import MultiCursor
import matplotlib.pyplot as plt

threshold = 6
period_max = 1./ 25000.0 

def parse_curve(isf_file):
    """
    Reads one tektronix .isf file and returns a dictionary containing
    all tags as keys. The actual data is stored in the key "data".
    """
    extensions = set([".isf"])
    if os.path.splitext(isf_file)[-1].lower() not in extensions:
        raise ValueError("File type unkown.")

    with open(isf_file, 'rb') as ifile:
        # read header
        header = {}
        while True:
            name = _read_chunk(ifile, " ")
            if name != ":CURVE":
                value = _read_chunk(ifile, ";")

                assert name not in header
                header[name] = value
            else:
                # ":CURVE " is the last tag of the header, followed by
                # '#XYYY' with X being the number of bytes of YYY.
                # YYY is the length of the datastream following in bytes.
                value = ifile.read(2).decode()
                y_str = ifile.read(int(value[-1])).decode()
                value += y_str
                # the number of bytes might be present with or without the
                # preceding header ":WFMPRE:"
                nobytes = header.get("BYT_NR",
                                     header.get(":WFMPRE:BYT_NR", "0")
                                     )

                assert int(y_str) == int(header["NR_PT"]) * int(nobytes)
                header[name] = value
                currentposition = ifile.tell()
                break

        assert header["ENCDG"] == "BINARY"

        # read data as numpy array
        header["xdata"],header["ydata"] = _read_data(ifile, currentposition, header)

    return header


def _read_chunk(headerfile, delimiter):
    """
    Reads one chunk of header data. Based on delimiter, this may be a tag
    (ended by " ") or the value of a tag (ended by ";").
    """
    prior_delimiter = None
    chunk = []
    c = ' '
    while True:
        c = headerfile.read(1).decode() # Python 3.x must add decode UTF8
        if c != delimiter:
            chunk.append(c)
            if c == '"':
                # switch delimiter to make sure to parse the whole string
                # enclosed in '"'.
                delimiter, prior_delimiter = c, delimiter
        elif prior_delimiter:
            # switch back delimiter
            chunk.append(c)
            delimiter, prior_delimiter = prior_delimiter, None
        else:
            return "".join(chunk)


def _read_data(bfile, position, header):
    """
    Reads in the binary data as numpy array.
    Apparently, there are only 1d-signals stored in .isf files, so a 1d-array
    is read.
    """
    # determine the datatype from header tags
    datatype = ">" if header["BYT_OR"] == "MSB" else "<"
    if header["BN_FMT"] == "RI":
        datatype += "i"
    else:
        datatype += "u"
    # BYT_NR might be present with preceding header ":WFMPRE:BYT_NR"
    nobytes = header.get("BYT_NR",
                         header.get(":WFMPRE:BYT_NR", "")
                         )
    datatype += nobytes
    assert len(datatype) >= 3

    bfile.seek(position)
    data = np.fromfile(bfile, datatype)
    assert data.size == int(header["NR_PT"])

    # calculate true values
    y_data = (data - float(header["YOFF"])) * float(header["YMULT"] ) + float(header["YZERO"])
    xzero = float(header["XZERO"])
    xincr = float(header["XINCR"])
    nr_pt = int(header["NR_PT"])
    xstop = xzero + nr_pt * xincr
    header["XSTOP"] = xstop
    x_data = np.arange(xzero, xstop , xincr).tolist()
    y_data = y_data.tolist()
    # xzero = float(header["XZERO"])
    # xinc = float(header["XINCR"])
    # numpt = int(header["NR_PT"])
    # x_data = []
    # for i in range(numpt):
    #     x_data.append(xzero + i * xinc )
    # for x in range()
    # x_data = range(float(head["XZERO"]), float(head["XINCR"]) * float(head["NR_PT"]), float(head["XINCR"])
    return x_data, y_data
""" % If ENV format (envelope), separate into max and min
if pointformat == 'ENV'
    disp('Envelope format: voltage output = [vmax vmin]');
    npts = round(npts/2);
    vmin = yzero + ymult*(data(1:2:end) - yoff);
    vmax = yzero + ymult*(data(2:2:end) - yoff);
    t = xzero + xincr*(0:npts-1)'*2;  % 2 data points per increment
    t = t - min(t);
    v = [vmax vmin];
else
    v = yzero + ymult*(data - yoff);
    t = xzero + xincr*(0:npts-1)';
    t = t - min(t);
end; """

# calculate duty of input analog waveform, tdig/ddig/tduty/dduty saved as value changed 
def decode_duty(sample_time, threshold, duty_max, timein, datain ) :
    data = {}
    tdig = []
    ddig = []
    tduty = []
    dduty = []
    dperiod = []
    cnt_d100 = 0
    cnt_d0 = 0
    
    thdl = threshold * 0.8
    thdh = threshold * 1.2
    data_cnt = 0 # input list number
    data01 = 0 #digital data
    data01_old = 0 # old value of digital data
    period = 0.0
    duty = 0.0  
    period_old = 0
    duty_old = 0  
    time_now = 0    
    time01 = 0.0 #time @ 0 --> 1
    time10 = 0.0 #time @ 1 --> 0  
    cnt_01= 0 #number of transition from low to high
    val_old = 0
    
    # print("input waveform time cnt = %d" % (len(timein)))
    # print("input waveform data cnt = %d" % (len(datain)))
    for val in datain :
        time_now = timein[data_cnt] 
        #deal first sample
        if data_cnt == 0 : 
            if val >= threshold:
                data01 = 1
            else:
                data01 = 0
        else:
            # set hsystersis 
            # at rising, must greater then thdh
            if val > val_old: 
                if val >= thdh:
                    data01 = 1
                    # save at rising/falling edge
                    tdig.append(time_now - (sample_time * 0.001))
                    ddig.append(data01_old)                                      
                    tdig.append(time_now)
                    ddig.append(data01)                     
            # at falling, must less then thdl
            elif val < val_old:
                if val <= thdl:
                    data01 = 0  
                    #save at rising/falling edge
                    tdig.append(time_now -(sample_time * 0.001))
                    ddig.append(data01_old)                                      
                    tdig.append(time_now)
                    ddig.append(data01)                           
                     
            # 0 -> 1, calculate period value
            if data01 > data01_old:                            
                #if first transition detected, set first number of duty =0
                if cnt_01== 0 : 
                    time01 = time_now
                    time10 = time_now
                    tduty.append(timein[0])
                    dduty.append(0)
                    dperiod.append(0)
                    duty = 0                                                                    
                else :
                    period = time_now - time01
                    duty = (time10 - time01) / period   
                    #if period < period_max: 
                        #save old duty before dt    
                    tduty.append(time01 - sample_time)
                    dduty.append(duty_old)
                    dperiod.append(period_old) 
                    #save new value                                                       
                    tduty.append(time01)
                    dduty.append(duty)
                    dperiod.append(period)               
                    #update time01 and time10     
                    time01 = time_now 
                    time10 = time_now
                    period_old = period
                    duty_old = duty
                cnt_01+= 1
            # 1 -> 0, latch the time from high to low
            elif data01 < data01_old :
                time10 = time_now 

            # # detect 100% and 0% duty
            # if data01 > data01_old:     
            #     cnt_d100 = 0 
            # else:
            #     cnt_d100 += sample_time

            # if data01 < data01_old:     
            #     cnt_d0 = 0 
            # else:
            #     cnt_d0 += sample_time                         

            # if (cnt_d100 > period_max):
            #     if (data01 == 1):
            #         tduty.append(time_now)
            #         dduty.append(1)   
            #     cnt_d100 = 0

            # if (cnt_d0 > period_max):
            #     if (data01 == 0):
            #         tduty.append(time_now)
            #         dduty.append(0)   
            #     cnt_d0 = 0                                     

        data01_old = data01   
        val_old = val                        
        data_cnt += 1
        if (data_cnt > 0) and (data_cnt % 100000) == 0:
            print(".",end = '',flush = True)
        if (data_cnt > 0) and (data_cnt % 5000000) == 0:
            print('\n')
        
    #save last duty
    tduty.append(time01 - sample_time)
    dduty.append(duty)    
    dperiod.append(period)
    tduty.append(time_now)
    dduty.append(duty) 
    dperiod.append(period)
    data["tdig"] = tdig          
    data["ddig"] = ddig
    data["tduty"] = tduty        
    data["dduty"] = dduty     
    data["dperiod"] = dperiod       
    return data

#wfm = [[],[],[],[],[]]


fn =  filedialog.askopenfilename(initialdir='.', title="Select isf file to open", filetypes = (("isffiles","*.isf"),("all files","*.*")))
wfm = parse_curve(fn)
sampling_time = float(wfm["XINCR"])
print("sampling time = %.9f s" % (sampling_time))
len = len(wfm["xdata"])
print("from = %.9f s to %.9f s" % (wfm["xdata"][0], wfm["xdata"][len-1]))
print("processing duty")
data_duty = decode_duty(sampling_time, threshold, period_max, wfm["xdata"], wfm["ydata"])


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
    """
    Like Cursor but the crosshair snaps to the nearest x, y point.
    For simplicity, this assumes that *x* is sorted.
    """

    def __init__(self, ax, x, y):
        self.ax = ax
        self.lx = ax.axhline(color='k')  # the horiz line
        self.ly = ax.axvline(color='k')  # the vert line
        self.x = x
        self.y = y
        # text location in axes coords
        self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)

    def mouse_move(self, event):
        if not event.inaxes:
            return

        x, y = event.xdata, event.ydata
        indx = min(np.searchsorted(self.x, x), len(self.x) - 1)
        x = self.x[indx]
        y = self.y[indx]
        # update the line positions
        self.lx.set_ydata(y)
        self.ly.set_xdata(x)

        self.txt.set_text('x=%1.2f, y=%1.2f' % (x, y))
        print('x=%1.2f, y=%1.2f' % (x, y))
        self.ax.figure.canvas.draw()

fig,ax = plt.subplots(4, 1, figsize=(15,8), sharex=True)
plt.tight_layout()

x = [[],[],[],[]]
y = [[],[],[],[]]

x[0] = wfm["xdata"]
y[0] = wfm["ydata"]
x[1] = data_duty["tdig"]
y[1] = data_duty["ddig"]
x[2] = data_duty["tduty"]
y[2] = data_duty["dduty"]
x[3] = data_duty["tduty"]
y[3] = data_duty["dperiod"]


for ch in [0,1,2,3]:
    ax[ch].plot(x[ch], y[ch])
    print("plot ax[%d]" % (ch))
    # ax[ch].format_coord = lambda x, y: "({:.9f}, ".format(x[ch]) +  "{:.9f})".format(y[ch])
    # set grid format
    ax[ch].minorticks_on()           
    ax[ch].tick_params(labeltop=False, axis='both',width=2, colors='black',which='both')            
    ax[ch].grid(b= True, axis='both', which='major', color='#666666', linestyle='-')            
    ax[ch].grid(b= True, axis='both', which='minor', color='#999999', linestyle='-', alpha=0.2)      

snap_cursor0 = SnaptoCursor(ax[0], x[0], y[0])
print(type(snap_cursor0))
# fig.canvas.mpl_connect('motion_notify_event', snap_cursor0.mouse_move)  
# snap_cursor1 = SnaptoCursor(ax[1], x[1], y[1])
# fig.canvas.mpl_connect('motion_notify_event', snap_cursor1.mouse_move)  
# snap_cursor2 = SnaptoCursor(ax[2], x[2], y[2])
# fig.canvas.mpl_connect('motion_notify_event', snap_cursor2.mouse_move)  
# snap_cursor3 = SnaptoCursor(ax[3], x[3], y[3])
# fig.canvas.mpl_connect('motion_notify_event', snap_cursor3.mouse_move)  
print(type(snap_cursor0))

plt.show()    
fig.show()



