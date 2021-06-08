from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
import numpy as np
import os.path
import matplotlib.pyplot as plt
# from matplotlib.backend_bases import cursors
#import matplotlib.backends.backend_tkagg as tkagg
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors 
#https://mplcursors.readthedocs.io/en/stable/examples/nondraggable.html
#https://xbuba.com/questions/57111356
from mpldatacursor import datacursor
#https://pypi.org/project/mpldatacursor/
import TEKTRONIX as tek

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
        self.txt = ax.text(0.7, 1, '', transform=ax.transAxes)

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

        self.txt.set_text('x=%1.9f, y=%1.3f' % (x, y))
        #print('x=%1.9f, y=%1.3f' % (x, y))
        self.ax.figure.canvas.draw()

class MENU:       
    def __init__(self): 
        self.thdvals_default = {"LOW": 2.1, "HIGH":2.9}
        self.val = 0             
        self.dutyckbox = [] 
        self.duty_choice = []
        self.duty_sel = 0

        self.thd_strs = {} # threshold value for duty calculation
        self.thd_entrys = {}
        self.thd_vals = {}

        self.lim_strs = {} # 
        self.lim_entrys = {}
        self.lim_vals = {}   
        self.limits = {}     

        self.snapckbox = [] 
        self.snap_choice = {}
        self.snap_sel = 0
        self.snap_cid = [0]*4
        self.snap_cursor = {}

        self.lb = []
        #self.lim_val = []
        self.enty = []
        
        self.lines = {}
        #self.ch_map = {0:1, 1:2, 2:4, 3:8}
        #self.ch_map = {1:'CH1', 2:'CH2', 3:'CH3', 4:'CH4'}
        self.ax_map = {"CH1" : 0, "CH2" : 1, "CH3" : 2, "CH4" : 3}
        self.type_map={"WFM":"Waveform", "DUTY":"Duty", "FREQ":"Frequency", "PERD":"Period"}

        #self.top.geometry('200x200')                            
        #self.top.title("Tektronic Waveform Process")

        self.wfm_type = {} #waveform type to precess: voltage, duty, period, frequency

        self.xdata = {} # x,y data to plot
        self.ydata = {} # x,y data to plot
        self.xylimit = {} # axis limit
        self.xyfit = {} # max, min of x, y, data
        self.period_max = 1./ 25000.0 #maximum period 
        self.wfm = tek.TEKTONIX()

    def print_widget(self, name, wgt):
        self.top.update()
        print("%s:width = %d height = %d" % (name, wgt.winfo_width(), wgt.winfo_height()))

    def gui(self):
        #self.fig,self.ax = plt.subplots(4, 1, figsize=(16,8), sharex=True) 
        self.top = tk.Tk()        
        #self.top.geometry("640x480")            
        self.top.title("Tektronic Waveform Processor V1.0.200228")
        self.fig,self.ax = plt.subplots(4, 1, figsize=(16,8), sharex=True)
        for line in self.ax:
            self.set_grid_format(line)        

        # file selection 
        # bug fixed referenced 
        #https://www.reddit.com/r/learnpython/comments/98j433/tkinter_buttonarray_problem/
        row  = 0
        col = 0
        self.btn= {}
        for i in range(4):
            str_ch ="CH%d" % (i+1) 
            self.btn[str_ch] = tk.Button(self.top, text = str_ch)
            self.btn[str_ch].config(command =lambda str_ch = i + 1: self.process_file(str_ch))
            self.btn[str_ch].grid(column = col, row = row + i, columnspan = 2, sticky=tk.E + tk.W )  
            self.print_widget(str_ch ,self.btn[str_ch])          

        # CLear command
        #https://morvanzhou.github.io/tutorials/python-basic/tkinter/2-04-radiobutton/             
        row = 0
        col = 2
        btn_clr= {}
        btn_clr["CH1"]= tk.Button(self.top, text = "CLR" , command =lambda : self.clr_plt(self.lines, "CH1"))
        btn_clr["CH2"]= tk.Button(self.top, text = "CLR" , command =lambda : self.clr_plt(self.lines, "CH2"))
        btn_clr["CH3"]= tk.Button(self.top, text = "CLR" , command =lambda : self.clr_plt(self.lines, "CH3"))
        btn_clr["CH4"]= tk.Button(self.top, text = "CLR" , command =lambda : self.clr_plt(self.lines, "CH4"))
        str_chs = ["CH1", "CH2", "CH3", "CH4"]
        for str_ch in str_chs:
            i = str_chs.index(str_ch)
            btn_clr[str_ch].grid(column = col, row = row + i, sticky=tk.E + tk.W )
            #btn_clr[str_ch].place(x=40 , y = 4 + i * 20, heigh = 20)
        
        # Cursor snap check buttom
        row  = 0
        col = 3
        for i in range(4):
            str_ch = "CH%d" % (i + 1)
            self.snap_choice[str_ch] = tk.IntVar()
            self.snapckbox.append(tk.Checkbutton(self.top, text = "SNAP" , variable = self.snap_choice[str_ch], 
                command =lambda : self.set_cur_snap(self.snap_choice, self.lines)).grid(column =col, row =row)) 
            row += 1

        # waveform selection
        row = 0
        col = 4
        for i in range(4):
            str_ch ="CH%d" % (i+1)            
            self.wfm_type[str_ch] = tk.StringVar() 
            tk.Radiobutton(self.top, text='Waveform',variable=self.wfm_type[str_ch] , value='WFM',
                command=lambda :self.sel_view(self.wfm_type)).grid(column = col, row = row + i, sticky=tk.W)
            tk.Radiobutton(self.top, text='Duty',variable=self.wfm_type[str_ch], value='DUTY',
                command=lambda :self.sel_view(self.wfm_type)).grid(column = col + 1, row = row + i, sticky=tk.W)
            tk.Radiobutton(self.top, text='Frequency',variable=self.wfm_type[str_ch] , value='FREQ',
                command=lambda :self.sel_view(self.wfm_type)).grid(column = col + 2, row = row + i, sticky=tk.W)
            tk.Radiobutton(self.top, text='Period',variable=self.wfm_type[str_ch] , value='PERD',
                command=lambda :self.sel_view(self.wfm_type)).grid(column = col + 3, row = row + i, sticky=tk.W)
            self.wfm_type[str_ch].set("WFM")         

        # add seperator
        row = 5
        sp = ttk.Separator(orient="horizontal")
        sp.grid(row=row, column=0, columnspan=99, sticky="we")

        # add seperator
        row += 1
        sp = ttk.Separator(orient="horizontal")
        sp.grid(row=row, column=0, columnspan=99, sticky="we")
        # threshold entry
        # row = 6
        # col = 0
        # tk.Label(self.top, text="Threshold Low(V)").grid(column = col, row = row, sticky=tk.N+tk.E+tk.S+tk.W)                 
        # self.thd_strs["LOW"]= tk.StringVar                
        # self.thd_entrys["LOW"] = tk.Entry(self.top, textvariable = self.thd_strs["LOW"], width = 6, bd =5)
        # self.thd_entrys["LOW"].grid(column = col + 1, row = row, sticky=tk.E)

        # tk.Label(self.top, text="Threshold High(V)").grid(column = col + 2, row = row, sticky=tk.N+tk.E+tk.S+tk.W)                 
        # self.thd_strs["HIGH"]= tk.StringVar                
        # self.thd_entrys["HIGH"] = tk.Entry(self.top, textvariable = self.thd_strs["HIGH"], width = 6, bd =5)
        # self.thd_entrys["HIGH"].grid(column = col + 3, row = row, sticky=tk.E)
        # self.set_thdvals(self.thd_entrys, self.thdvals_default)

        # # add seperator
        # row = 7
        # sp = ttk.Separator(orient="horizontal")
        # sp.grid(row=row, column=0, columnspan=99, sticky=tk.N+tk.E+tk.S+tk.W)
        
        row = row + 1
        col = 1
        tk.Label(self.top, text="LOW").grid(column = col, row = row, sticky=tk.E + tk.W)  
        tk.Label(self.top, text="HIGH").grid(column = col + 1, row = row, sticky=tk.E + tk.W)  

        row += 1
        col = 0
        # Threshold Entry
        self.lb.append(tk.Label(self.top, text="Thrd" ).grid(column = col, row = row , sticky=tk.E))  
        # low value entry    
        self.thd_strs["LOW"]= tk.StringVar               
        self.thd_entrys["LOW"] = tk.Entry(self.top, textvariable = self.thd_strs["LOW"], width = 12, bd =5)
        self.thd_entrys["LOW"].grid(column = col + 1, row = row, sticky=tk.E) 
        # high value entry
        self.thd_strs["HIGH"]= tk.StringVar             
        self.thd_entrys["HIGH"] = tk.Entry(self.top, textvariable = self.thd_strs["HIGH"], width = 12, bd =5)
        self.thd_entrys["HIGH"].grid(column = col + 2, row = row, sticky=tk.E) 
        self.set_thdvals(self.thd_entrys, self.thdvals_default)

        row += 1
        # TIme range Entry
        self.lb.append(tk.Label(self.top, text="TIme" ).grid(column = col, row = row , sticky=tk.E))  
        # low value entry    
        self.lim_strs["XLOW"]= tk.StringVar               
        self.lim_entrys["XLOW"] = tk.Entry(self.top, textvariable = self.lim_strs["XLOW"], width = 12, bd =5)
        self.lim_entrys["XLOW"].grid(column = col + 1, row = row, sticky=tk.E) 
        # high value entry
        self.lim_strs["XHIGH"]= tk.StringVar             
        self.lim_entrys["XHIGH"] = tk.Entry(self.top, textvariable = self.lim_strs["XHIGH"], width = 12, bd =5)
        self.lim_entrys["XHIGH"].grid(column = col + 2, row = row, sticky=tk.E) 


        row += 1
        col = 0
        lim_map = {0:"CH1", 1:"CH2", 2:"CH3", 3:"CH4"}
        for i in range(4):
            #label 
            self.lb.append(tk.Label(self.top, text=lim_map[i] ).grid(column = col, row = row, sticky=tk.E))  
            # low value entry                
            self.lim_strs[lim_map[i] + "LOW"]= tk.StringVar               
            self.lim_entrys[lim_map[i] + "LOW"] = tk.Entry(self.top, textvariable = self.lim_strs[lim_map[i] + "LOW"], width = 12, bd =5)
            self.lim_entrys[lim_map[i] + "LOW"].grid(column = col + 1, row = row , sticky=tk.E) 

            # high value entry
            self.lim_strs[lim_map[i] + "HIGH"]= tk.StringVar             
            self.lim_entrys[lim_map[i] + "HIGH"] = tk.Entry(self.top, textvariable = self.lim_strs[lim_map[i] + "HIGH"], width = 12, bd =5)
            self.lim_entrys[lim_map[i] + "HIGH"].grid(column = col + 2, row = row, sticky=tk.E) 
            row += 1
        
        self.set_limit_entry(self.lim_entrys, 
            {'XLOW': 0, 'XHIGH': 1, 'CH1LOW': 0, 'CH1HIGH': 1, 'CH2LOW': 0, 'CH2HIGH': 1, 'CH3LOW': 0, 'CH3HIGH': 1, 'CH4LOW': 0, 'CH4HIGH': 1})

        # axis range command
        col = 0
        tk.Button(self.top, text = "SET AXIS" , command =lambda : self.set_axis(self.lines, self.lim_entrys)).grid(column = col, row =  row, sticky=tk.W)
        tk.Button(self.top, text = "GET AXIS" , command =lambda : self.get_axis(self.lines, self.lim_entrys)).grid(column = col + 1, row =  row, sticky=tk.W)
        tk.Button(self.top, text = "FIT AXIS" , command =lambda : self.set_axis_fit()).grid(column = col +2, row =  row, sticky=tk.W)

        # row = 15
        # self.pb = ttk.Progressbar(self.top,  maximum = 100, length = 200 , orient = 'horizontal', mode = 'determinate' )
        # self.pb.grid(column = 0, row = row, columnspan=99, sticky=tk.W+tk.E+tk.N+tk.S)  
        
        self.top.update()
        self.top.mainloop() 
    
    def process_file(self, ch): 
        #   ask file input
        fn =  filedialog.askopenfilename(initialdir='.', title="Select isf file to open", filetypes = (("isffiles","*.isf"),("all files","*.*")))
        if fn == "":
            print("No file select!!")
            return
        print(fn)

        # read the threshold value for duty processing
        line = "CH%d" % (ch)  
        # check which type of data to view
        view_type = self.wfm_type[line].get()
        thd_vals = self.get_thdvals(self.thd_entrys)
        
        # check is isf file 
        self.wfm.read_isf(fn)
        if self.wfm.error == True:
            self.wfm.error = False
            return         

        if view_type == "DUTY": 
            self.wfm.decode_duty(thd_vals ,self.period_max, self.wfm)        
            x = self.wfm.duty["T_DUTY"]
            y= self.wfm.duty["D_DUTY"]            
        elif view_type == "PERD":      
            self.wfm.decode_duty(thd_vals ,self.period_max, self.wfm)        
            x = self.wfm.duty["T_DUTY"]
            y= self.wfm.duty["D_PERIOD"]     
        elif view_type == "FREQ":
            self.wfm.read_isf(fn)   
            self.wfm.decode_duty(thd_vals ,self.period_max, self.wfm)        
            x = self.wfm.duty["T_DUTY"]
            y = []
            for p in self.wfm.duty["D_PERIOD"] :
                if p == 0:
                    y.append(0)
                else:
                    y.append(1.0 / p)
        else: 
            self.wfm.read_isf(fn)      
            x = self.wfm.xydata["XDATA"]
            y= self.wfm.xydata["YDATA"]  

        
        #save processed data to xydata
        # x_str = "x%d" % (ch )
        # y_str = "y%d" % (ch )
        # self.xydata[x_str] = x
        # self.xydata[y_str] = y
        self.xdata[line] = x
        self.ydata[line] = y

        self.limits["XLOW"] = min(self.xdata[line] )
        self.limits["XHIGH"] = max(self.xdata[line] )
        self.limits[line + "LOW"] = min(self.ydata[line] )
        self.limits[line + "HIGH"] = max(self.ydata[line] )

        #plot the waveform    
        ax_ch = self.ax_map[line]    
        self.lines[line] =  self.ax[ax_ch]
        self.plotxy(self.lines[line], self.xdata[line], self.ydata[line], 'b')     

        # datacursor(self.lines[line], display='multiple', draggable=True, )

        

        # self.snap_cursor[line] = SnaptoCursor(self.ax[ax_ch], self.xdata[line], self.ydata[line])
        # self.fig.canvas.mpl_connect('motion_notify_event', self.snap_cursor[line].mouse_move)            

    def plotxy(self, line, x, y, c) :
        # ax_ch = self.ax_map[line] 
        #line.cla()
        line.plot(x, y, c)   
        mplcursors.cursor(line , hover = False, multiple = True)      
        # snap_cursor =SnaptoCursor(line, x, y)
        # fig.canvas.mpl_connect('motion_notify_event', line.mouse_move)   
        self.set_grid_format(line)
        plt.tight_layout()     
        plt.show()    
        self.fig.show()          

    def set_grid_format(self, line):
        # set grid format
            #self.ax[i].format_coord = lambda x, y: "({:.9f}, ".format(self.x[i]) +  "{:.9f})".format(self.y[i])
        line.minorticks_on()           
        line.tick_params(labeltop=False, axis='both',width=2, colors='black',which='both')            
        line.grid(b= True, axis='both', which='major', color='#666666', linestyle='-')            
        line.grid(b= True, axis='both', which='minor', color='#999999', linestyle='-', alpha=0.2)         

    def sel_view(self, wfm_types):        
        print("==== Set waveform Type ====")
        for wfm_type in wfm_types:
            print("%s = %s" % (wfm_type, self.type_map[wfm_types[wfm_type].get()]))

    def set_chsel(self, choice):
        for i in range(4):
            if choice[i].get() == 1:
                print("set ch%d duty" % i)
            else:
                print("disable ch%d duty" % i)
   

    def set_cur_snap(self, choice, lines):    
        pass    
        # for line in lines:            
        #     if choice[line].get() == 1:
        #         ax_ch = self.ax_map[line] 
        #         self.ax[ax_ch].cla()
        #         self.lines[line] = self.ax[ax_ch].plot(self.xdata[line], self.ydata[line] ,'b') 
        #         self.snap_cursor[line] = SnaptoCursor(self.ax[ax_ch], self.xdata[line], self.xdata[line])
        #         self.fig.canvas.mpl_connect('motion_notify_event', self.snap_cursor[line].mouse_move)  
        #         #mplcursors.cursor(lines[line] , hover = False,  multiple = True)
        #         print("set %s cursor snap" % line)
        #     else:
        #         self.fig.canvas.mpl_dicconnect(self.snap_cursor[line].mouse_move)
        #         #mplcursors.cursor(lines[line] , hover = True, multiple = False)
        #         print("set %s cursor hover" % line)           
        #     self.fig.tight_layout()                
        #     plt.show()    
        #     self.fig.show() 
     
        # for ch in choice:
        #     if choice[ch].get() == 1:
        #             mplcursors.cursor(lines[ch] , hover = True, multiple = False)
        #         print("set ch%d cursor hover" % i)
        #     else:
        #         mplcursors.cursor(lines[i] , hover = False,  multiple = True)
        #         print("disable ch%d cursor hover" % i)     

        # for i in range(4):
        #     if  lines[i]:
        #         if choice[i].get() == 1: 
        #             mplcursors.cursor(lines[i] , hover = True, multiple = False)
        #             print("set ch%d cursor hover" % i)
        #         else:
        #             mplcursors.cursor(lines[i] , hover = False,  multiple = True)
        #             print("disable ch%d cursor hover" % i)
        plt.show()

    def get_axis(self, lines, entrys):
        limits = {}         
        for line in lines:
            limits["XLOW"], limits["XHIGH"] = lines[line].get_xlim()
            limits[line + "LOW"], limits[line + "HIGH"] = lines[line].get_ylim() 
        self.set_limit_entry(entrys, limits)
        print(limits)
        return limits
        
    def set_axis(self, lines, entrys):
        limits = self.get_limit_entry(entrys)
        for line in lines:
            lines[line].set_xlim(limits["XLOW"], limits["XHIGH"])
            lines[line].set_ylim(limits[line + "LOW"], limits[line + "HIGH"])
        self.fig.show()
        # self.fig.show()  
        #  for i in range(5):
        #     if i == 0:
        #         item = "xlim" 
        #     else:
        #         item = "ylim%d" % (i + 1)

        #     self.xylimit[item] = [float(self.enty[i * 2].get()) , float(self.enty[i * 2 + 1].get())]

        #     if i == 0:
        #         self.ax[i].set_xlim(self.xylimit[item])  
        #     else:
        #         self.ax[i - 1].set_ylim(self.xylimit[item])  

        #     print("set ch%d limit= %f, %f" % (i, self.xylimit[item][0], self.xylimit[item][1]))     
        #     self.fig.show()  

    def set_axis_fit(self):
        self.set_limit_entry(self.lim_entrys, self.limits)
        self.set_axis(self.lines, self.lim_entrys)

    def get_limit_entry(self,entrys):
        limits = {}
        for entry in entrys:
            if entrys[entry].get() == "":
                limits[entry] = 0
            else:
                limits[entry] = float(entrys[entry].get())
        print(limits)
        return limits

    def set_limit_entry(self, entrys, limits):
        for entry in entrys:
            if entry in limits:
                entrys[entry].delete(0,tk.END)
                fmt = "%.9f" % limits[entry]
                entrys[entry].insert(0,fmt) 
            else:
                entrys[entry].delete(0,tk.END)
                fmt = "0" 
                entrys[entry].insert(0,fmt)                         


        # if ch == 0:
        #     item = "xlim"          
        # else:
        #     item = "ylim%d" % (ch + 1)

        # self.xylimit[item] = limit           
        # print("set %s limit= %f, %f" % (item, self.xylimit[item][0], self.xylimit[item][1]))
        

    def set_thdvals(self, entrys, thd_vals):
        # fill the entry
        for entry in entrys:
            entrys[entry].delete(0,tk.END)
            entrys[entry].insert(0,str(thd_vals[entry])) 
        # confirm the entry    
        vals = self.get_thdvals(entrys)
        print("Threshold Low=%f V High=%f V " % (vals["LOW"], vals["HIGH"]))
            
    def get_thdvals(self, entrys):        
        err = False
        vals = {}
        for entry in entrys:
            if entrys[entry].get() == "":
                err = True
                vals[entry] = self.thdvals_default[entry]
            else:
                vals[entry] = float(entrys[entry].get())
                
        if err == True:
            messagebox.showwarning("Warning", "Threshold/Hystersis is empty, set to Default")  
        print("Threshold Low=%f V High=%f V " % (vals["LOW"], vals["HIGH"]))                              
        return vals   
    
    def clr_plt(self, lines, str_ch):
        # limits = {'XLOW': 1.0, 'XHIGH': 2.0, 'CH1LOW': 3.0, 'CH1HIGH': 4.0, 'CH2LOW': 5.0, 'CH2HIGH': 6.0, 'CH3LOW': 7, 'CH3HIGH': 8, 'CH4LOW': 9, 'CH4HIGH': 10}
        # self.set_limit_entry(self.lim_entrys, limits)
        # self.get_limit_entry(self.lim_entrys, self.lim_vals)
        # limits =self.get_axis(self.lines)
        # self.set_limit_entry(self.lim_entrys, limits)
        print(str_ch)
        if str_ch in lines:
            print("CLear " + str_ch)     
            self.get_axis(lines, self.lim_entrys)              
            lines[str_ch].cla()     
            self.set_axis(lines, self.lim_entrys)
            self.set_grid_format(lines[str_ch])                     
            self.fig.show()                 



MENU().gui()
