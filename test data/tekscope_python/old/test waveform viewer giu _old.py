from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
import numpy as np
import os.path
import matplotlib.pyplot as plt
from matplotlib.backend_bases import cursors
import matplotlib.backends.backend_tkagg as tkagg
import mplcursors #https://mplcursors.readthedocs.io/en/stable/examples/nondraggable.html
        
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

# calculate duty of input analog waveform, tdig/ddig/tduty/dduty saved as value changed 
def decode_duty(top, pb, sample_time, threshold, duty_max, timein, datain ) :
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
    if pb :
        pb['maximum'] = len(timein)
        pb['value'] = 0
        
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
            if pb:
                pb['value'] = data_cnt                             
                top.update()        
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

class GUI:       
    def __init__(self):    
        self.val = 0
        self.top = tk.Tk() 
        
        self.dutyckbox = [] 
        self.duty_choice = []
        self.duty_sel = 0
        
        self.snapckbox = [] 
        self.snap_choice = []
        self.snap_sel = 0
        self.snap_cid = [0]*4
        self.snap_cursor = [0]*4

        self.lines = [] * 4
        
        self.lb = []
        self.lim_val = []
        self.enty = []
        
        self.axlimit = [[]]* 5
        self.axmaxmin = {}
        
        self.ch_map = {0:1, 1:2, 2:4, 3:8}
        self.ch_map1 = {0:'CH1', 1:'CH2', 2:'CH3', 3:'CH4'}
        
        self.thd_val = 0                 
        self.top.title("Tektronic Waveform Process")
        self.fig_isset = 0
        
        self.fig,self.ax = plt.subplots(4, 1, figsize=(16,8), sharex=True) 

        
        self.x = [[]] * 4
        self.y = [[]] * 4

        # pb = ttk.Progressbar(top,  maximum = 100, length = 200 , orient = 'horizontal', mode = 'determinate' )
        # pb.grid(column = 0, row = 1, columnspan=4, sticky=tk.W+tk.E+tk.N+tk.S)  

        # tk.Button(top, text = 'Process File', command =lambda : process_file()).grid(column = 0, row = 2, sticky=tk.W) 
        # tk.Button(top, text = 'View duty').grid(column = 1, row = 2, sticky=tk.W)         
        # tk.Label(top, text="Channel").grid(column = 0, row=0, sticky = tk.W)
        gui_row = 0

        tk.Button(self.top, text = "CH1" , command =lambda : self.process_file(0)).grid(column = 0, row = 0, sticky=tk.W)
        tk.Button(self.top, text = "CH2" , command =lambda : self.process_file(1)).grid(column = 0, row = 1, sticky=tk.W)
        tk.Button(self.top, text = "CH3" , command =lambda : self.process_file(2)).grid(column = 0, row = 2, sticky=tk.W)
        tk.Button(self.top, text = "CH4" , command =lambda : self.process_file(3)).grid(column = 0, row = 3, sticky=tk.W) 
        
        tk.Button(self.top, text = "CLR" , command =lambda : self.clr_plt(0)).grid(column = 1, row = 0, sticky=tk.W)
        tk.Button(self.top, text = "CLR" , command =lambda : self.clr_plt(1)).grid(column = 1, row = 1, sticky=tk.W)
        tk.Button(self.top, text = "CLR" , command =lambda : self.clr_plt(2)).grid(column = 1, row = 2, sticky=tk.W)
        tk.Button(self.top, text = "CLR" , command =lambda : self.clr_plt(3)).grid(column = 1, row = 3, sticky=tk.W)
        
        for i in range(4):
            #txt_str = "CH%s" % (i)
            #self.btn.append(tk.Button(self.top, text = txt_str , command =lambda : self.process_file(i)).grid(column = 0, row = gui_row, sticky=tk.W) )
            self.duty_choice.append(tk.IntVar())
            self.dutyckbox.append(tk.Checkbutton(self.top, text = "DUTY" , variable = self.duty_choice[i], command =lambda : self.set_chsel()).grid(column =2, row = gui_row)) 
            self.snap_choice.append(tk.IntVar())
            self.snapckbox.append(tk.Checkbutton(self.top, text = "SNAP" , variable = self.snap_choice[i], command =lambda : self.set_snapsel()).grid(column =3, row = gui_row)) 
            gui_row += 1

        tk.Label(self.top, text="Threshold(V)").grid(column = 0, row = gui_row, sticky=tk.E)      
        self.thd_val = tk.StringVar                
        self.enty1 = tk.Entry(self.top, textvariable = self.thd_val, width = 6, bd =5)
        self.enty1.grid(column = 1, row = gui_row, sticky=tk.E) 
        self.set_thdval(2.5)
        gui_row += 1
 
        tk.Label(self.top, text="LOW").grid(column = 1, row = gui_row, sticky=tk.E + tk.W)  
        tk.Label(self.top, text="HIGH").grid(column = 2, row = gui_row, sticky=tk.E + tk.W)  
        gui_row += 1
        lim_str = {0:"X", 1:"CH1 LIM", 2:"CH2 LIM", 3:"CH3 LIM", 4:"CH4 LIM"}
        for i in range(5):
            self.lb.append(tk.Label(self.top, text=lim_str[i] ).grid(column = 0, row = gui_row, sticky=tk.E))      
            self.lim_val.append(tk.StringVar)              
            self.enty.append(tk.Entry(self.top, textvariable = self.lim_val[i * 2], width = 6, bd =5))
            self.enty[i * 2].grid(column = 1, row = gui_row, sticky=tk.E) 
            self.lim_val.append(tk.StringVar)              
            self.enty.append(tk.Entry(self.top, textvariable = self.lim_val[i * 2 + 1], width = 6, bd =5))
            self.enty[i * 2 + 1].grid(column = 2, row = gui_row, sticky=tk.E) 
            self.set_limitval(i, [ 0, 0])
            gui_row += 1  
        
        
        tk.Button(self.top, text = "SET AXIS" , command =lambda : self.set_axis()).grid(column = 0, row =  gui_row, sticky=tk.W)
        tk.Button(self.top, text = "GET AXIS" , command =lambda : self.get_axis()).grid(column = 1, row =  gui_row, sticky=tk.W)
        gui_row += 1
        
        self.pb = ttk.Progressbar(self.top,  maximum = 100, length = 200 , orient = 'horizontal', mode = 'determinate' )
        self.pb.grid(column = 0, row = gui_row, columnspan=4, sticky=tk.W+tk.E+tk.N+tk.S)  
        gui_row += 1
        
        self.top.mainloop() 
        
    def process_file(self, ch):
        period_max = 1./ 25000.0 
        len_data = 0
        threshold = self.get_thdval()
        if self.duty_choice[ch].get() == 1:
            duty_sel = 1
        else :
            duty_sel = 0
        print("CH%d duty sel = %d" % (ch + 1, duty_sel))          
        fn =  filedialog.askopenfilename(initialdir='.', title="Select isf file to open", filetypes = (("isffiles","*.isf"),("all files","*.*")))
        if fn == "":
            print("No file select!!")
            return
        wfm = parse_curve(fn)
        sampling_time = float(wfm["XINCR"])
        print("sampling time = %.9f s" % (sampling_time))
        len_data = len(wfm["xdata"])
        print("from = %.9f s to %.9f s" % (wfm["xdata"][0], wfm["xdata"][len_data-1]))        
        
        if self.duty_choice[ch].get() == 1:     
            if threshold == 0:
                messagebox.showwarning("Warnning","Threshhold voltage is 0V")
            data_duty = decode_duty(self.top, self.pb, sampling_time, threshold, period_max, wfm["xdata"], wfm["ydata"])
            self.x[ch] = data_duty["tduty"]
            self.y[ch] = data_duty["dduty"]            
        else:
            self.x[ch] = wfm["xdata"]
            self.y[ch] = wfm["ydata"] 
        
        # if self.fig_isset == 0:
        #     self.fig,self.ax = plt.subplots(4, 1, figsize=(15,8), sharex=True) 
      
            plt.tight_layout()           
            self.fig_isset = 1
        #self.ax[ch].cla()            
        line = self.ax[ch].plot(self.x[ch], self.y[ch]) 
        #mplcursors.cursor(line, multiple=True) 
        mplcursors.cursor(line, multiple=True).connect("add", lambda sel: sel.annotation.draggable(True))   
       
        for i in [0,1,2,3]:
            #self.ax[i].format_coord = lambda x, y: "({:.9f}, ".format(self.x[i]) +  "{:.9f})".format(self.y[i])
            # set grid format
            self.ax[i].minorticks_on()           
            self.ax[i].tick_params(labeltop=False, axis='both',width=2, colors='black',which='both')            
            self.ax[i].grid(b= True, axis='both', which='major', color='#666666', linestyle='-')            
            self.ax[i].grid(b= True, axis='both', which='minor', color='#999999', linestyle='-', alpha=0.2)  

        # snap_cursor = SnaptoCursor(self.ax[0], x, y)  
        # self.fig.canvas.mpl_connect('motion_notify_event', snap_cursor.mouse_move)  
               
        plt.show()    
        self.fig.show()             
        # print("CH%d selected" % ch)  
        # duty_sel = self.duty_choice[ch].get()
        # print("CH%d duty sel = %d" % (ch, duty_sel))
              
    def set_chsel(self):
        for i in range(4):
            temp = ~(0x1 << i) & 0xff
            self.duty_sel &= temp
            if self.duty_choice[i].get() == 1:
                temp = (0x01) << i
                self.duty_sel |= temp
        print("duty_sel =%x" %self.duty_sel)  
  
    # def set_snapsel(self):
    #     for i in range(4):
    #         temp = ~(0x1 << i) & 0xff
    #         self.snap_sel &= temp
    #         if self.snap_choice[i].get() == 1:
    #             temp = (0x01) << i
    #             self.snap_sel |= temp
    #             self.snap_cursor[i] = SnaptoCursor(self.ax[i], self.x[i], self.y[i])
    #             self.snap_cid[i] = self.fig.canvas.mpl_connect('motion_notify_event', self.snap_cursor[i].mouse_move)
    #         else:
    #             if self.snap_cid[i] != 0:
    #                 self.fig.canvas.mpl_disconnect(self.snap_cid[i])
    #     print("snap_sel =%x" %self.snap_sel) 

    def get_axis(self):
        for i in range(5):
            if i == 0:
                self.axlimit[i] = self.ax[0].get_xlim()
            else:
                self.axlimit[i] = self.ax[i - 1].get_ylim()     
            self.set_limitval(i, self.axlimit[i])          
            print("ch %d  limit= %f, %f" % (i, self.axlimit[i][0], self.axlimit[i][1]))

    def set_axis(self):
         for i in range(5):
            if i == 0:
                self.enty[i].get()
                self.ax[0].set_xlim([float(self.enty[i * 2].get()) , float(self.enty[i * 2 + 1].get())])
            else:
                self.ax[i - 1].set_ylim([float(self.enty[i * 2].get()) , float(self.enty[i * 2 + 1].get())])           
            print("set ch%d limit= %f, %f" % (i, self.axlimit[i][0], self.axlimit[i][1]))     
            self.fig.show()  
             
    def set_limitval(self, ch, limit):
        self.enty[ch * 2].delete(0,tk.END)
        self.enty[ch * 2].insert(0,str(limit[0])) 
        self.enty[ch * 2 + 1].delete(0,tk.END)
        self.enty[ch * 2 + 1].insert(0,str(limit[1])) 
        self.axlimit[ch] = limit
        print("set ch%d limit= %f, %f" % (ch, self.axlimit[ch][0], self.axlimit[ch][1]))

    def set_thdval(self, thd):
        self.enty1.delete(0,tk.END)
        self.enty1.insert(0,str(thd)) 
        self.thd = thd

            
    def get_thdval(self):
        thd = 0
        if self.enty1.get() != "":
            thd = float(self.enty1.get()) 
        else:
            self.set_thdval(0)
            
        print("set thd =%f" % thd)               
        return thd      
    
    def clr_plt(self, ch):
        self.ax[ch].cla()   
        plt.show()    
        self.fig.show()     

gui=GUI()
