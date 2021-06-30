
import numpy as np
import csv 
from tqdm import tqdm
import tkinter as tk
#import sys
#from tkinter import filedialog
#import matplotlib.pyplot as plt


class TEKTONIX:
    def __init__(self):
        self.error = False
        self.data_bin =()
        self.header = {}
        self.xy = () 
        self.duty = ()
        self.period = ()
        self.digital = ()
        self.dt = 0
        #self.view_type = "WFM"   #waveform type to precess: {"WFM":"Waveform", "DUTY":"Duty", "FREQ":"Frequency", "PERD":"Period"


    def open_isf(self,fn):
        with open(fn, 'rb') as f:            
            data_bin = f.read()     
        if ":CURVE".encode() not in data_bin:
            self.error = True
            return False   
        return True

    
    #https://yoheie.sakura.ne.jp/isftoasc/isftoasc.c
    # decode(): bytes -> string 
    # encode(): string -> bytes
    def read_isf(self,fn):   
        print(fn) 
        # reaf file as bytes to avoid encoding error
        self.error =False
        with open(fn, 'rb') as f:
            data_bin = f.read()
        self.data_bin = data_bin
        if ":CURVE".encode() not in data_bin:
            self.error = True
            return
        #check if valid string exit
        # try:
        #     g = lambda x:  x in s
        #     if g(":CURVE".encode) == False: 
        #         # if not find, issue exception 
        #         print(n)               
        # except:
        #     print("Not a valid isffile!!")
        #     self.error = True
        #     return {}, {}

        current_pos = data_bin.find(":CURVE".encode(), 0, 1024)

        # read header string only except "":CURVE"
        hdr_string = data_bin[0:current_pos -1].decode()
        # split ti list 
        hdr_list = hdr_string.split(";")  
        header = {}      
        for x in hdr_list:
            if "WFID" in x :
                nx ="WFID " + "".join(x.strip("WFID").split(" ")) 
                hdr_list.remove(x) 
                hdr_list.append(nx) 
        # convert to dict
        header = dict(x.split(" ") for x in hdr_list)    
        # for x in header:
        #     print(x, header[x])

        # ":CURVE " is the last tag of the header, followed by
        # '#XYYY..Y' with X being the number of bytes of YYY.
        # YYY..Y is the length of the datastream following in bytes.        
        token = ":CURVE #".encode()
        current_pos = data_bin.find(token)
        leng = len(token)
        current_pos += leng 
        num = int(data_bin[current_pos:current_pos+1]) #read X
        current_pos +=1
        numofbytes = int(data_bin[current_pos: current_pos + num]) #read YYY
        #print("number of bytes =",numofbytes)

        # read data bytes
        current_pos += num
        end_pos = current_pos + numofbytes
        databytes = data_bin[current_pos:end_pos]
        # print(current_pos, end_pos)
        # print(databytes[0], databytes[1])
        # print(databytes[-2], databytes[-1])
        # print(len(databytes))

        # determine the datatype from header tags
        #RI:signed integer RP: positive integer FP:single-precision binary floating point
        #https://docs.scipy.org/doc/numpy/reference/generated/numpy.dtype.html#numpy.dtype
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

        # convert to integer    
        yint = np.frombuffer(databytes, datatype) #conver to interer
        y = (yint - float(header["YOFF"])) * float(header["YMULT"] ) + float(header["YZERO"])

        # generate time data
        start = float(header["XZERO"])
        dt = float(header["XINCR"])
        nr_pt = int(header["NR_PT"])
        end = start + nr_pt  * dt
        x = np.arange(start, end , dt)
   
        xy = (tuple(x), tuple(y))
        self.header = header
        self.xy = xy
        self.dt = dt
        return header, xy

    def hyst(self, x, th_lo, th_hi, initial = False):
    #https://stackoverflow.com/questions/23289976/how-to-find-zero-crossings-with-hysteresis
        """
        x : Numpy Array
            Series to apply hysteresis to.
        th_lo : float or int
            Below this threshold the value of hyst will be False (0).
        th_hi : float or int
            Above this threshold the value of hyst will be True (1).
        """        

        if th_lo > th_hi: # If thresholds are reversed, x must be reversed as well
            x = x[::-1]
            th_lo, th_hi = th_hi, th_lo
            rev = True
        else:
            rev = False

        hi = x >= th_hi
        lo_or_hi = (x <= th_lo) | hi

        ind = np.nonzero(lo_or_hi)[0]  # Index for everyone below or above
        if not ind.size:  # prevent index error if ind is empty
            x_hyst = np.zeros_like(x, dtype=bool) | initial
        else:
            cnt = np.cumsum(lo_or_hi)  # from 0 to len(x)
            x_hyst = np.where(cnt, hi[ind[cnt-1]], initial)

        if rev:
            x_hyst = x_hyst[::-1]

        return x_hyst

    def periods(self, t, y, threshold):
    #https://app.getpocket.com/read/2910127817        
        """
        Given the input signal `y` with samples at times `t`,
        find the time periods between the times at which the
        signal `y` increases through the value `threshold`.

        `t` and `y` must be 1-D numpy arrays.
        """
        transition_times = find_transition_times(t, y, threshold)
        deltas = np.diff(transition_times)
        return deltas
    
    # calculate duty of input analog waveform, tdig/ddig/tduty/dduty saved as value changed 
    def decode_duty(self, xy, thresholds, plimits) :
        timein, datain = xy
        sample_time = timein[1] - timein[0]
        tdig = []
        ddig = []
        tduty = []
        dduty = []
        dperiod = []
        
        thdl = thresholds[0]
        thdh = thresholds[1]
        threshold = (thdl + thdh) / 2
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
        

        #for val in  tqdm(datain) :            
        for val in  tqdm(datain) :         
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

            data01_old = data01   
            val_old = val                        
            data_cnt += 1
                      
        #save last duty
        tduty.append(time01 - sample_time)
        dduty.append(duty)    
        dperiod.append(period)
        tduty.append(time_now)
        dduty.append(duty) 
        dperiod.append(period)
        
        self.duty = (tuple(tduty), tuple(dduty))
        self.period = (tuple(tduty), tuple(dperiod))
        self.digital = (tuple(tdig), tuple(ddig))


    def save_csv(self, fn, xydata):
# """         fn: filename to save
#         xydata : dict with key "XDATA" and "YDATA" """
        #https://machinelearningmastery.com/how-to-save-a-numpy-array-to-file-for-machine-learning/   
        with open(fn, 'w+', newline='') as csvfile:
            #Transpose row and column
            arr = np.array([xydata["XDATA"], xydata["YDATA"]]).T
            print("writing csv file...")
            writer = csv.writer(csvfile)
            writer.writerow(["TIme","Data"])
            writer.writerows(arr)
            print("csv file done!!")

    def save_pwl(self, fn, xydata):
    # """         fn: filename to save
#         xydata : dict with key "XDATA" and "YDATA" """
        #https://machinelearningmastery.com/how-to-save-a-numpy-array-to-file-for-machine-learning/   
        with open(fn, 'w+', newline='') as csvfile:
            #Transpose row and column
            arr = np.array([xydata["XDATA"], xydata["YDATA"]]).T
            print("writing spice pwl file...")
            writer = csv.writer(csvfile, delimiter=' ')
            writer.writerows(arr)
            print("spice csv file done!!")

# fn =  filedialog.askopenfilename(initialdir='.', title="Select isf file to open", filetypes = (("isf files","*.isf"),("all files","*.*")))
# #fn = "D:\\Temp\\python\\G2072\\FAN_01_V12_DUTY99_startup\\tek0004CH1.isf"
# #fn = "D:\\Temp\\python\\G2071\\tek0000CH2.isf"
# wfm = TEKTONIX()

# #header, xydata = wfm.read_isf(fn)
# wfm.read_isf(fn)
# if (wfm.error == True):
#     sys. exit()

# # fn =  filedialog.asksaveasfilename(initialdir='.', title="Select csv file to save", filetypes = (("csv files","*.csv"),("all files","*.*")))   
# # print(fn)
# # if fn is None:  # ask saveasfile return `None` if dialog closed with "cancel".
# #     print("Not select file")
# #     sys. exit()
# # wfm.save_csv(fn, wfm.xydata)   

# fig, ax = plt.subplots()
# x = wfm.xydata["XDATA"]
# y = wfm.xydata["YDATA"]
# ax.plot(x,y)
# plt.show()


