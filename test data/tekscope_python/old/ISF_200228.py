import numpy as np
import os.path  
import easygui as eg  
import sys
try:
    import Tkinter as tk
    import ttk
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    
if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg    

# from tqdm import tqdm


class ISF:    
    def __init__(self, fn, f_duty, thd_vals, period_max): 
        self.isf_file = fn
        self.header , self.xydata = self.parse_curve(fn)
        if f_duty == True:
            self.sampling_time = float(self.header["XINCR"])
            data_duty = self.decode_duty(self.sampling_time, thd_vals, period_max, self.xydata["X_DATA"], self.xydata["Y_DATA"])
            self.xydata.update(data_duty)

    # def merge_two_dicts(self, x, y):
    # """Given two dicts, merge them into a new dict as a shallow copy."""
    #     z = x.copy()
    #     z.update(y)
    #     return z
        
    # def __call__(self):
    #     return self.header     
    
    def parse_curve(self, isf_file):
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
            xydata = {}
            while True:
                name = self.read_chunk(ifile, " ")
                if name != ":CURVE":
                    value = self.read_chunk(ifile, ";")

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
                    nobytes = header.get("BYT_NR",header.get(":WFMPRE:BYT_NR", "0"))

                    assert int(y_str) == int(header["NR_PT"]) * int(nobytes)
                    header[name] = value
                    currentposition = ifile.tell()
                    break

            assert header["ENCDG"] == "BINARY"

            # read data as numpy array
            xydata["X_DATA"],xydata["Y_DATA"] = self.read_data(ifile, currentposition, header)

        return header, xydata


    def read_chunk(self, headerfile, delimiter):
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


    def read_data(self, bfile, position, header):
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

    # calculate duty of input analog waveform, tdig/ddig/tduty/dduty saved as value changed 
    def decode_duty(self,sample_time, thd_vals, period_max, timein, datain ) :
        data = {}
        tdig = []
        ddig = []
        tduty = []
        dduty = []
        dperiod = []
        cnt_d100 = 0
        cnt_d0 = 0
        
        thdl = thd_vals["LOW"]
        thdh = thd_vals["HIGH"]
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
        for val in  datain :            
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
                # if pb:
                #     pb['value'] = data_cnt                             
                #     top.update()        
            if (data_cnt > 0) and (data_cnt % 5000000) == 0:
                print('\n')
            
        #save last duty
        tduty.append(time01 - sample_time)
        dduty.append(duty)    
        dperiod.append(period)
        tduty.append(time_now)
        dduty.append(duty) 
        dperiod.append(period)
        data["T_DIG"] = tdig          
        data["D_DIG"] = ddig
        data["T_DUTY"] = tduty        
        data["D_DUTY"] = dduty     
        data["D_PERIOD"] = dperiod       
        return data    
