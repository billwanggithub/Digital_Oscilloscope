#/usr/bin/python3
def import_or_install(package):
    try:
        __import__(package)
    except ImportError:
        os.system("pip install "+ package)        
        #pip.main(['install', package]) 

import os.path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.colorchooser import askcolor
#import_or_install("matplotlib")
import matplotlib.pyplot as plt
import_or_install("pylab")
import numpy as np
import_or_install("scipy")
from scipy.signal import butter, lfilter, freqz
import_or_install("addcopyfighandler")
import_or_install("mplcursors")
import mplcursors
from tqdm import tqdm
import scipy.fftpack
import warnings
import TEKTRONIX as tek

#for clipboard
#https://gist.github.com/i-namekawa/5742922e80ece213897e
# import_or_install("win32clipboard")  
# import_or_install("PIL")  
# from PIL import Image
# import_or_install("pylab")
# from pylab import *
# try:
#     import_or_install("io")
#     from io import StringIO ## for Python 3    
# except ImportError:
#     import_or_install("StringIO")
#     from StringIO import StringIO ## for Python 2
# from time import sleep


#import_or_install("addcopyfighandler") 

# from matplotlib.backend_bases import cursors
#import matplotlib.backends.backend_tkagg as tkagg
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


#https://mplcursors.readthedocs.io/en/stable/examples/nondraggable.html
#https://xbuba.com/questions/57111356
#from mpldatacursor import datacursor
#https://pypi.org/project/mpldatacursor/


ver = "V1.0.200307"
plot_list = ["CH1", "CH2", "CH3", "CH4"]

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

        self.helptext =["low pass filter:",
                        "     - cutoff = 0 : disable the filter",                        
                        "vertical scaling:",
                         "    - scaling = 0: disable scaling",
                         "max period:",
                         "    - used for duty calculation to filter out glitch"]
        
        self.ax_map = {"CH1" : 0, "CH2" : 1, "CH3" : 2, "CH4" : 3}
        self.type_map={"WFM":"Waveform", "DUTY":"Duty", "FREQ":"Frequency", "PERD":"Period"}
        self.entrys_default = {"THDLOW": 2.1, "THDHIGH" :2.9, "LPFREQ" : 0, "LPORDER" : 0, 
            'CH1XLOW': 0, 'CH1XHIGH': 99, 'CH1YLOW': 0, 'CH1YHIGH': 10, 
            'CH2XLOW': 0, 'CH2XHIGH': 99, 'CH2YLOW': 0, 'CH2YHIGH': 10,
            'CH3XLOW': 0, 'CH3XHIGH': 99, 'CH3YLOW': 0, 'CH3YHIGH': 10,
            'CH4XLOW': 0, 'CH4XHIGH': 99, 'CH4YLOW': 0, 'CH4YHIGH': 10,
            "MULT": 0, "OFFSET": 0, "PERMIN" : 1 / 100e3, "PERMAX" : 1}      
            
        self.plot_color = "#004080"  
         
        self.dutyckbox = [] 
        self.duty_choice = []
        self.duty_sel = 0

        self.entrys ={}
        self.entrys_str = {}
        self.entrys_value = {}

        self.clips = 0
        self.links = 0x0f

        self.view_type = 0
        self.xdata = {} # x,y data to plot
        self.ydata = {} # x,y data to plot
        self.limits = {} # axis limit
        self.waveforms = {}
        for plot in plot_list:
            self.waveforms[plot] = tek.TEKTONIX()        

        self.top = tk.Tk()                 
        self.top.title("Tektronic Waveform Processor " + ver)
        self.fig = {}
        self.fig["wave"]= plt.figure(figsize=(10,7.5)) # 800 X 600
        self.plots = {}

    def print_widget(self, name, wgt):
        self.top.update()
        print("%s:width = %d height = %d" % (name, wgt.winfo_width(), wgt.winfo_height()))

    def gui(self):        
        # file selection 
        # bug fixed referenced 
        #https://www.reddit.com/r/learnpython/comments/98j433/tkinter_buttonarray_problem/
        row  = 0
        col = 0
        self.buttons= {}
        for plot in plot_list:
            i = plot_list.index(plot)
            self.buttons["plot "+plot]  = tk.Button(self.top, text = plot)
            #self.btn[ch].config(command =lambda ch = i + 1: self.process_file(self.waveforms, ch))
            self.buttons["plot "+plot].config(command =lambda ch = plot: self.process_file(self.waveforms, ch))
            self.buttons["plot "+plot].grid(column = col, row = row + i, columnspan = 2, sticky=tk.E + tk.W )  
            if i == 0:
                self.buttons["plot "+plot].configure(bg = 'green')
            else:
                self.buttons["plot "+plot].configure(bg = '#ff0080') 

        # CLear command
        #https://morvanzhou.github.io/tutorials/python-basic/tkinter/2-04-radiobutton/             
        row = 0
        col = 2
        btn_clr= {}
        for plot in plot_list:
            i = plot_list.index(plot)        
            btn_clr[plot]= tk.Button(self.top, text = "CLR" , command =lambda ch = plot : self.clr_plt(ch))
            btn_clr[plot].grid(column = col, row = row + i, sticky=tk.E + tk.W )


        # waveform cliipping check buttom
        self.chkboxs_clip = []
        self.checks_clip = {}
        self.choices_clip = {}
        row  = 0
        col += 1
        for plot in plot_list:
            i = plot_list.index(plot)
            self.choices_clip[plot] = tk.IntVar()
            self.chkboxs_clip.append(tk.Checkbutton(self.top, text = "CLIP" , variable = self.choices_clip[plot], 
                command =lambda ch = plot : self.set_checks(ch)).grid(column =col, row =row)) 
            self.choices_clip[plot].set(0)
            row += 1

        # Cursor link check buttom
        self.chkboxs_link = []
        self.checks_link = {}
        self.choices_link = {}
        row  = 0
        col += 1
        for plot in plot_list:
            i = plot_list.index(plot)
            self.choices_link[plot] = tk.IntVar()
            self.chkboxs_link.append(tk.Checkbutton(self.top, text = "LINK" , variable = self.choices_link[plot], 
                command =lambda ch = plot : self.set_checks(ch)).grid(column =col, row =row)) 
            self.choices_link[plot].set(1)
            row += 1

        # waveform selection
        row = 0       
        type_maps = [("WFM", "Waveform"), ("DUTY", "Duty"), ("FREQ", "Frequency"), ("PERD", "Period")]
        self.view_types_str = {}
        for ch in plot_list:     
            i = plot_list.index(ch)      
            self.view_types_str[ch]= tk.StringVar() 
            col = 5
            for value, text in type_maps:
                tk.Radiobutton(self.top, text=text,variable=self.view_types_str[ch] , value=value,
                    command=lambda :self.set_view_type()).grid(column = col, row = row + i, sticky=tk.W)
                col += 1
            self.view_types_str[ch].set("WFM")

        # add seperator
        row = 5
        col = 0
        sp = ttk.Separator(orient="horizontal")
        sp.grid(row=row, column=col, columnspan=99, sticky="we" ,ipady = 5)

        row += 1
        col =0
        self.lb = []
        self.lb.append(tk.Label(self.top, text="Lowpass Filter" ).grid(column = col, row = row , sticky=tk.W))  
        col += 1
        item = "LPFREQ"
        self.lb.append(tk.Label(self.top, text="Cutoff(Hz)" ).grid(column = col, row = row , sticky=tk.E))     
        self.entrys_str[item]= tk.StringVar               
        self.entrys[item] = tk.Entry(self.top, textvariable =  self.entrys_str[item], width = 12, bd =5)
        self.entrys[item].grid(column = col + 1, row = row, sticky=tk.E)  
    
        col = 2
        item = "LPORDER"
        self.lb.append(tk.Label(self.top, text="Order" ).grid(column = col, row = row , sticky=tk.E))   
        self.entrys_str[item]= tk.StringVar               
        self.entrys[item] = tk.Entry(self.top, textvariable =  self.entrys_str[item], width = 12, bd =5)
        self.entrys[item].grid(column = col + 1, row = row, sticky=tk.E)  
  
        # add seperator
        row += 1
        col = 0
        sp = ttk.Separator(orient="horizontal")
        sp.grid(row=row, column=col, columnspan=99, sticky="we" ,ipady = 5)

        row += 1
        col =0
        self.lb.append(tk.Label(self.top, text="Vertical Scaling" ).grid(column = col, row = row , sticky=tk.W))          
        col += 1
        item = "MULT"
        self.lb.append(tk.Label(self.top, text="Scaling" ).grid(column = col, row = row , sticky=tk.E))     
        self.entrys_str[item]= tk.StringVar               
        self.entrys[item] = tk.Entry(self.top, textvariable =  self.entrys_str[item], width = 12, bd =5)
        self.entrys[item].grid(column = col + 1, row = row, sticky=tk.E)  
    
        col = 2
        item = "OFFSET"
        self.lb.append(tk.Label(self.top, text="Offset" ).grid(column = col, row = row , sticky=tk.E))   
        self.entrys_str[item]= tk.StringVar               
        self.entrys[item] = tk.Entry(self.top, textvariable =  self.entrys_str[item], width = 12, bd =5)
        self.entrys[item].grid(column = col + 1, row = row, sticky=tk.E)  

        # add seperator
        row += 1
        col = 0
        sp = ttk.Separator(orient="horizontal")
        sp.grid(row=row, column=col, columnspan=99, sticky="we" ,ipady = 5)
        
        row = row + 1
        col = 1
        tk.Label(self.top, text="LOW").grid(column = col, row = row, sticky=tk.E + tk.W)  
        tk.Label(self.top, text="HIGH").grid(column = col + 1, row = row, sticky=tk.E + tk.W)  

        row += 1
        col = 0
        # Threshold Entry
        self.lb.append(tk.Label(self.top, text="Threshold" ).grid(column = col, row = row , sticky=tk.E))  
        # low value entry    
        item = "THDLOW"
        self.entrys_str[item]= tk.StringVar               
        self.entrys[item] = tk.Entry(self.top, textvariable = self.entrys_str[item], width = 12, bd =5)
        self.entrys[item].grid(column = col + 1, row = row, sticky=tk.E) 
        # high value entry
        item = "THDHIGH"
        self.entrys_str[item]= tk.StringVar             
        self.entrys[item] = tk.Entry(self.top, textvariable = self.entrys_str[item], width = 12, bd =5)
        self.entrys[item].grid(column = col + 2, row = row, sticky=tk.E) 
 
        row += 1
        col = 0
        self.lb.append(tk.Label(self.top, text="Period" ).grid(column = col, row = row , sticky=tk.E))  
        # low value entry    
        item = "PERMIN"
        self.entrys_str[item]= tk.StringVar               
        self.entrys[item] = tk.Entry(self.top, textvariable = self.entrys_str[item], width = 12, bd =5)
        self.entrys[item].grid(column = col + 1, row = row, sticky=tk.E) 
        # high value entry
        item = "PERMAX"
        self.entrys_str[item]= tk.StringVar             
        self.entrys[item] = tk.Entry(self.top, textvariable = self.entrys_str[item], width = 12, bd =5)
        self.entrys[item].grid(column = col + 2, row = row, sticky=tk.E)    

        row += 1
        col = 0
        # TIme range Entry
        self.lb.append(tk.Label(self.top, text="TIme" ).grid(column = col, row = row , sticky=tk.E))  
        # low value entry   
        for plot in plot_list:     
            i = plot_list.index(ch) 
            item = plot + "XLOW" 
            self.entrys_str[item]= tk.StringVar               
            self.entrys[item] = tk.Entry(self.top, textvariable = self.entrys_str[item], width = 12, bd =5)
            if plot == "CH1":
                self.entrys[item].grid(column = col + 1, row = row, sticky=tk.E) 
            # high value entry
            item = plot + "XHIGH"
            self.entrys_str[item]= tk.StringVar             
            self.entrys[item] = tk.Entry(self.top, textvariable = self.entrys_str[item], width = 12, bd =5)
            if plot == "CH1":
                self.entrys[item].grid(column = col + 2, row = row, sticky=tk.E) 
            row += 1

        #scaling entry
        # self.entrys_str["XLOW"]= tk.StringVar               
        # self.entrys["XLOW"] = tk.Entry(self.top, textvariable = self.entrys_str["XLOW"], width = 12, bd =5)
        # self.entrys["XLOW"].grid(column = col + 1, row = row, sticky=tk.E) 

        row += 1
        col = 0
        for ch in plot_list:     
            i = plot_list.index(ch) 
            #label 
            self.lb.append(tk.Label(self.top, text=ch ).grid(column = col, row = row, sticky=tk.E))  
            # low value entry                
            self.entrys_str[ch + "YLOW"]= tk.StringVar               
            self.entrys[ch + "YLOW"] = tk.Entry(self.top, textvariable = self.entrys_str[ch + "YLOW"], width = 12, bd =5)
            self.entrys[ch + "YLOW"].grid(column = col + 1, row = row , sticky=tk.E) 

            # high value entry
            self.entrys_str[ch + "YHIGH"]= tk.StringVar             
            self.entrys[ch + "YHIGH"] = tk.Entry(self.top, textvariable = self.entrys_str[ch + "YHIGH"], width = 12, bd =5)
            self.entrys[ch + "YHIGH"].grid(column = col + 2, row = row, sticky=tk.E) 
            row += 1


        # add seperator
        row += 1
        col = 0
        sp = ttk.Separator(orient="horizontal")
        sp.grid(row=row, column=col, columnspan=99, sticky="we" ,ipady = 5)

        # axis range command  
        row += 1    
        col = 0        
        tk.Button(self.top, text = "SET AXIS" , command =lambda : self.set_axis(self.plots, self.entrys)).grid(column = col, row =  row, sticky=tk.W)
        col += 1
        tk.Button(self.top, text = "GET AXIS" , command =lambda : self.get_axis(self.plots, self.entrys)).grid(column = col, row =  row, sticky=tk.W)
        col += 1
        tk.Button(self.top, text = "FIT AXIS" , command =lambda : self.set_axis_fit()).grid(column = col, row =  row, sticky=tk.W)
        # col += 1        
        # cmd = lambda : self.cut_data("CH1")
        # tk.Button(self.top, text = "SPLIT" , command = cmd).grid(column = col, row =  row, sticky=tk.W)

        # add seperator
        row += 1
        col = 0
        sp = ttk.Separator(orient="horizontal")
        sp.grid(row=row, column=col, columnspan=99, sticky="we" ,ipady = 5)

        row += 1
        col = 0        
        self.buttons["set color"] = tk.Button(self.top, text = "COLOR" , command =lambda : self.select_color())
        self.buttons["set color"].grid(column = col, row =  row, sticky=tk.W )        
        self.buttons["set color"].configure(bg = self.plot_color)  

        col += 1
        tk.Button(self.top, text = "To CSV" , command =lambda : self.save_to_csv()).grid(column = col, row =  row, sticky=tk.W)
        col += 1
        tk.Button(self.top, text = "To NPY" , command =lambda : self.save_to_npy()).grid(column = col, row =  row, sticky=tk.W)        
        col += 1
        tk.Button(self.top, text = "XY PLOT" , command =lambda : self.xy_plot()).grid(column = col, row =  row, sticky=tk.W)
        col += 1
        tk.Button(self.top, text = "FFT" , command =lambda : self.do_fft()).grid(column = col, row =  row, sticky=tk.W)        

        self.set_entrys(self.entrys, self.entrys_default)
        self.top.update()
        self.top.mainloop() 
    
    def process_file(self, waveforms, plot): #plot = "CH1" ...
        # channel = plot_list.index(plot)
        if self.check_add_plot_order(plot) == False:
            return
        #   ask file input
        fn =  filedialog.askopenfilename(initialdir='.', title="Select isf/npz file to open", 
            filetypes = (("isf files","*.isf"), ("npz files","*.npz"), ("all files","*.*")))
        if fn == "":
            print("No file select!!")
            return
        print("%s = %s" % (plot, fn))

        fn_path = os.path.splitext(fn)

        # check is isf file  an read file to waveform
        waveform = waveforms[plot] 
        print("Read oscilliscope data")     
        if fn_path[1] == ".isf"   :
            waveform.read_isf(fn)
            if waveform.error == True:
                print("Not a valid isffile!!")            
                waveform.error = False
                return                 
            xy = waveform.xy
            dt= waveform.dt
        elif fn_path[1] == ".npz" :
            arr =np.load(fn, allow_pickle= True)
            xy = arr["xy"]
            waveform.xy = xy
            #convert list to dict
            header_arr = arr["header"]            
            for item in header_arr:
                waveform.header[item[0]] = item[1]  
            dt = float(waveform.header["XINCR"])           
            waveform.dt =dt
        else:
            print("not valid file type")          
            return
        print ("header =", waveform.header)
        print ("sampling time = %.10f" % waveform.dt)
        print("done")
        # # check which type of data to view
        # view_type = waveform.view_type
        view_type =self.view_types_str[plot].get()
        print(view_type)

        # read all entrys
        val_strs = self.get_entrys(self.entrys)
        #  threshold value for duty and frequency processing        
        thresholds = (float(val_strs["THDLOW"]), float(val_strs["THDHIGH"])) 
        xlimits = (float(val_strs["CH1XLOW"]), float(val_strs["CH1XHIGH"])) 
        plimits = float(val_strs["PERMIN"]), float(val_strs["PERMAX"])

        # check if clip data 
        if (self.choices_clip[plot].get()) == 1:
            print("Cliping data")
            print("%f to %f"% xlimits[0:2])
            x, y = self.cut_data(xy, dt, xlimits)
            xy = (x, y)
            print("Done")

        # ckeck view type       
        # Duty
        if view_type == "DUTY": 
            print("Process Duty Calculation.......")
            waveform.decode_duty(xy, thresholds, plimits)       
            x, y = waveform.duty 
        # Period         
        elif view_type == "PERD":      
            print("Process Period Calculation.......")
            waveform.decode_duty(xy, thresholds, plimits)       
            x, y = waveform.period
            
        # Frequency   
        elif view_type == "FREQ":
            print("Process period Calculation.......")
            waveform.decode_duty(xy, thresholds, plimits)    
            x, period =  waveform.period 

            # filter glich
            print("Process Frequency Calculation.......")
            yarr = np.asarray(period)
            yarr_clip = np.clip(yarr, a_min = plimits[0], a_max = plimits[1])
            y  = tuple(1.0 / yarr_clip)       

        # Waveform                         
        else: 
            print("Load Waveform data")
            x, y = xy 
        print("done")
        # get the filter cutoff frequency and order
        
        if "LPORDER" in val_strs:
            order = int(val_strs["LPORDER"])
        else:
            order = 0
        if "LPFREQ" in val_strs:
            cutoff = float(val_strs["LPFREQ"])
        else:
            cutoff =0 
        fs = 1.0 / dt # sample rate, Hz
        # check if filter on
        if order != 0 and cutoff != 0:       
            print("low pass filter")          
            y_filter= self.butter_lowpass_filter(y, cutoff , fs, order = order)  
            print("done")
            y = y_filter    
       
        # plot the waveform    
        mult = float(val_strs["MULT"])
        offset = float(val_strs["OFFSET"])
        
        # process vertical scaling   
        print("Check scaling and offset")     
        if mult != 0 and offset != 0:
            print("Process Wavefom Scaling an Offset.......")
            ny = [(val + offset)* mult for val in tqdm(y)]
            y = ny            
        elif  offset != 0:
            print("Process Wavefom Offset.......")
            ny = [(val + offset) for val in tqdm(y)]    
            y = ny    
        elif  mult != 0:
            print("Process Wavefom Scaling.......")
            ny = [val * mult for val in tqdm(y)]
            y = ny              
        print("done")

        limit = [min(x), max(x), min(y), max(y)]


        # assign the ax to plots dictionary
        if limit[2] >= limit[3]:
            limit[3] = limit[2] + 0.1
            print("Warning!! min = max")   

        self.limits[plot] = limit
        # update max and min to entry box
        val_strs[plot + "XLOW"],val_strs[plot + "XHIGH"],val_strs[plot + "YLOW"] ,val_strs[plot + "YHIGH"] = limit
        self.set_entrys(self.entrys, val_strs) 

        self.plot_line(plot, x, y, self.plot_color, limit)         

    def check_add_plot_order(self, plot):
        plots = self.plots        
        if plot not in plots:
            if plot_list.index(plot) == len(plots) :
                return True
            else:
                messagebox.showerror("Plot Error","Please Add Lines by order(CH1 -> CH2 -> CH3 -> CH4 -> .....")        
                return False

    def plot_line(self, plot, x, y, c, limit) :  # plot :"CH1" ... 
        # self.top.update_idletasks()
        fig = self.fig["wave"]
        plots = self.plots
        if plot not in plots:
            if self.check_add_plot_order:
                # add the new axis
                n = len(fig.axes)
                if n == 0:
                    ax = fig.add_subplot(1, 1, 1)
                else:
                    for i in range(n):
                        fig.axes[i].change_geometry(n+1, 1, i+1)
                    ax = fig.add_subplot(n+1, 1, n+1)
                    #share the same Xaxis
                    plots["CH1"].get_shared_x_axes().join(ax,plots["CH1"]) 

                plots[plot] = ax

                self.buttons["plot "+plot].configure(bg = 'green') 
        # if plot not in self.fig["wave"].axes:
        #     self.fig["wave"].add_axes(plot)
        #     plt.tight_layout()
        line = plots[plot].plot(x, y, c)
        #ylimit = limit[2] * 0.9, limit["3] * 1.1
        # ylimit = limit[2], limit[3]
        # print("Set Y axis ", ylimit)
        # self.plots[plot].set_ylim(ylimit)           
        self.set_grid_format(self.plots[plot])
        mplcursors.cursor(plots[plot] , hover = False, multiple = True)      
        # snap_cursor =SnaptoCursor(plot, x, y)
        # fig.canvas.mpl_connect('motion_notify_event', plot.mouse_move)   
        plt.tight_layout()  
        plt.draw()   
        plt.show()            
        return line     
  

    def clr_plt(self,plot):
        fig = self.fig["wave"]
        plots = self.plots   
        if plot in plots:
            if len(plots[plot].lines) ==  0:
                if plot != "CH1":
                    if plot_list.index(plot) == (len(plots) - 1):
                        fig.delaxes(plots[plot])
                        del plots[plot]
                        self.buttons["plot "+plot].configure(bg = '#ff0080') 
                        n = len(plots)
                        for plot in plots:
                            index = plot_list.index(plot)
                            plots[plot].change_geometry(n,1, index + 1)                        
            else:
                del plots[plot].lines[-1]              

        fig.subplots_adjust()
        plt.tight_layout()
        plt.show()                  
        # if plot in plots:
        #     print("CLear " + plot)     
        #     #self.get_axis(plots, self.entrys)              
        #     #plots[ch].cla()     
        #     plots[plot].lines.delete[-1]
        #     #self.set_axis(plots, self.entrys)
        #     self.set_grid_format(plots[plot])                     
        #     self.fig["wave"].show()  

    def cut_data(self, xy , sample_time, xlimit):
        # values = self.get_entrys(self.entrys)
        # start_time , end_time = float(values["CH1XLOW"]), float(values["CH1XHIGH"])  
        x, y = xy       
        dt = x[1] - x[0]
        dt = sample_time
        start_time , end_time = xlimit
        #print("sampling rate = %.10f" %  (1./dt ))
        filter = (x >= start_time) & (x <= (end_time + dt))
        nx = np.extract(filter, x)
        ny = np.extract(filter, y)
        return nx,ny

    def save_plots(self, plots):        
        plots_bak = {}
        for plot in plots:
            lines_bak = {}
            i = 0
            for line in plots[plot].lines:
                #lines_bak.append(plots[plot].lines[i].get_data())
                lines_bak[i] =line.get_data()
                i += 1
            plots_bak[plot] = lines_bak  
        self.plots_bak = plots_bak 
        print("backup plots data OK")

        values = self.get_entrys(entrys)
        start_time = float(values["CH1XLOW"]), float(values["CH1XHIGH"])
        end_time = float(values[plot + "YLOW"]), float(values[plot +"YHIGH"])

        return plots_bak                 


    def set_checks(self, ch):
        # https://stackoverflow.com/questions/42973223/how-share-x-axis-of-two-subplots-after-they-are-created
        # use ax2.autoscale() to unlink axes
        i = 0
        self.clips = 0        
        for plot in self.choices_clip:
            if self.choices_clip[plot].get() == 1:
                self.clips |= (0x01 << i)
            i += 1
        print("clips = 0X0%X" % self.clips)

        i = 0
        self.links = 0        
        for plot in self.choices_link:
            if self.choices_link[plot].get() == 1:
                self.links |= (0x01 << i)
            i += 1

        print("links = 0X0%X" % self.links)


    def select_color(self):
        (triple, hexstr) = askcolor()
        if hexstr:
            print("set color = %s " % hexstr)
            print("(r,g,b)= % s" % str(triple))
            self.plot_color = hexstr
            self.buttons["set color"].configure(bg = self.plot_color)
        return hexstr


    def set_grid_format(self, plot):
        # set grid format
        #self.ax[i].format_coord = lambda x, y: "({:.9f}, ".format(self.x[i]) +  "{:.9f})".format(self.y[i])
        plot.minorticks_on()              
        plot.tick_params(labeltop=False, axis='both',width=2, colors='black',which='both')            
        plot.grid(b= True, axis='both', which='major', color='#666666', linestyle='-')            
        plot.grid(b= True, axis='both', which='minor', color='#999999', linestyle='-', alpha=0.2)         

    def set_view_type(self):        
        print("==== Set waveform view Type ====")
        for ch in self.waveforms:  
            self.view_type = self.view_types_str[ch].get()
            print("%s = %s" % (ch, self.view_type))


    def get_axis(self, plots, entrys):
        values = {}
        xlow, xhigh = plots["CH1"].get_xlim()
        values["CH1XLOW"], values["CH1XHIGH"] = ("%.10f" % xlow),  ("%.10f" % xhigh)
        for plot in plots:
            ylow, yhigh = plots[plot].get_ylim()
            values[plot + "YLOW"], values[plot +"YHIGH"] = ("%.4f" % ylow),  ("%.4f" % yhigh)
        
        self.set_entrys(entrys, values)
        
    def set_axis(self, plots, entrys):
        values = self.get_entrys(entrys)
        for plot in plots:
            xlimit = float(values["CH1XLOW"]), float(values["CH1XHIGH"])
            ylimit = float(values[plot + "YLOW"]), float(values[plot +"YHIGH"])
            print("%s :" % plot)
            print("xlim =")  
            print (xlimit)      
            print("ylim =")  
            print (ylimit)                      
            plots[plot].set_xlim(xlimit)
            plots[plot].set_ylim(ylimit)
            # self.set_grid_format(plots[plot])
            # plt.tight_layout()     
            # plt.show()    
            self.fig["wave"].show() 

    def set_axis_fit(self):        
        for plot in self.waveforms:
            if plot in self.limits:
                limit = self.limits[plot]
                limit_dic = {plot + "XLOW" : limit[0] , plot + "XHIGH" : limit[1], plot + "YLOW" : limit[2], plot + "YHIGH" : limit[3]}
                self.set_entrys(self.entrys, limit_dic)
                self.set_axis(self.plots, self.entrys)
                      
    
    def get_entrys(self, entrys):
        values = {}
        for entry in entrys:
            if entrys[entry].get() != "":
                values[entry] = entrys[entry].get()
                #print("%s = %s" % (entry, values[entry]))
        return values


    def set_entrys(self, entrys, values): 
        # fill the entry
        for value in values:
            entrys[value].delete(0,tk.END)            
            if value in ["CH1XLOW", "CH1XHIGH" , "CH2XLOW", "CH2XHIGH", "CH3XLOW", "CH3XHIGH", "CH4XLOW", "CH4XHIGH"]:
                float_value = float(values[value])
                entrys[value].insert(0,"%.4f" % float_value)  # limit y axix to 0.1mV
            elif value in ["CH1YLOW", "CH1YHIGH" , "CH2YLOW", "CH2YHIGH", "CH3YLOW", "CH3YHIGH", "CH4YLOW", "CH4YHIGH"]:
                float_value = float(values[value])
                entrys[value].insert(0,"%.10f" % float_value)  # limit x axix to 0.1ns
            else:
                val_str = str(values[value])
                entrys[value].insert(0, val_str)             
        #self.get_entrys(entrys)
                          
    def save_to_csv(self):
        fn =  filedialog.askopenfilename(initialdir='.', title="Select isf file to open", filetypes = (("isffiles","*.isf"),("all files","*.*")))
        if fn == "":
            print("No file select!!")
            return
        print(fn)
        wfm = tek.TEKTONIX() 
        wfm.read_isf(fn)        
        fn =  filedialog.asksaveasfilename(initialdir='.', title="Select csv file to save", filetypes = (("csv files","*.csv"),("all files","*.*")))    
        wfm.save_csv(fn, wfm.xydata)  

    def save_to_npy(self):
        fn =  filedialog.askopenfilename(initialdir='.', title="Select isf file to open", filetypes = (("isffiles","*.isf"),("all files","*.*")))
        print("read file = " + fn )  
        waveform = tek.TEKTONIX()       
        waveform.read_isf(fn)
        #fn =  filedialog.asksaveasfilename(initialdir='.', title="Select npy file to save", filetypes = (("npy files","*.npy"),("all files","*.*")))    
        #save to *.npy
        fn_path = os.path.splitext(fn)
        fn_npz = fn_path[0]+'.npz'
        print("save file = " + fn_npz )     
        header = list(waveform.header. items())
        header_array = np.array(header)
        np.savez(fn_npz, header = header_array, xy =waveform.xy, allow_pickle= True)     
        # arr = np.load(fn_npz, allow_pickle= True)
        # header =arr['header']
        # headern = {}
        # for item in header:
        #     headern[item[0]] = item[1]
        print("Done")
 
    def fftPlot(self, sig, dt=None, block=False, plot=True):
        # here it's assumes analytic signal (real signal...)- so only half of the axis is required

        if dt is None:
            dt = 1
            t = np.arange(0, sig.shape[-1])
            xLabel = 'samples'
        else:
            t = np.arange(0, sig.shape[-1]) * dt
            xLabel = 'freq [Hz]'

        if sig.shape[0] % 2 != 0:
            warnings.warn("signal prefered to be even in size, autoFixing it...")
            t = t[0:-1]
            sig = sig[0:-1]

        sigFFT = np.fft.fft(sig) / t.shape[0]  # divided by size t for coherent magnitude

        freq = np.fft.fftfreq(t.shape[0], d=dt)

        # plot analytic signal - right half of freq axis needed only...
        firstNegInd = np.argmax(freq < 0)
        freqAxisPos = freq[0:firstNegInd]
        sigFFTPos = 2 * sigFFT[0:firstNegInd]  # *2 because of magnitude of analytic signal

        if plot:
            fig_fft, ax_fft  = plt.subplots()     
            #fig_fft.suptitle('FFT Plot', fontsize=16)        
            ax_fft.plot(freqAxisPos, np.abs(sigFFTPos))
            ax_fft.set_xlabel(xLabel)
            ax_fft.set_ylabel('mag')
            ax_fft.set_title('Analytic FFT plot')
            self.set_grid_format(ax_fft)   
            mplcursors.cursor(ax_fft , hover = True)              
            plt.tight_layout()                         
            fig_fft.show()
            
        return sigFFTPos, freqAxisPos

    def do_fft(self):
        fn =  filedialog.askopenfilename(initialdir='.', title="Select isf/npz file to open", 
            filetypes = (("isf files","*.isf"), ("npz files","*.npz"), ("all files","*.*")))
        if fn == "":
            print("No file select!!")
            return

        fn_path = os.path.splitext(fn)

        # check is isf file  an read file to waveform
        waveform =  tek.TEKTONIX() 
        print("Read oscilliscope data")     
        if fn_path[1] == ".isf"   :
            waveform.read_isf(fn)
            if waveform.error == True:
                print("Not a valid isffile!!")            
                waveform.error = False
                return                 
            xy = waveform.xy
            dt= waveform.dt
        elif fn_path[1] == ".npz" :
            arr =np.load(fn, allow_pickle= True)
            xy = arr["xy"]
            waveform.xy = xy
            #convert list to dict
            header_arr = arr["header"]            
            for item in header_arr:
                waveform.header[item[0]] = item[1]  
            dt = float(waveform.header["XINCR"])           
            waveform.dt =dt
        else:
            print("not valid file type")          
            return
        print ("header =", waveform.header)
        print ("sampling time = %.10f" % waveform.dt)
        print("done")        
        x, y = xy
        #N = int(len(x))
        #yf = scipy.fftpack.fft(y)
        #https://stackoverflow.com/questions/25735153/plotting-a-fast-fourier-transform-in-python 
        ## https://stackoverflow.com/questions/28269157/plotting-in-a-non-blocking-way-with-matplotlib       
        self.fftPlot(np.asarray(y), dt= dt)
        # yf = np.fft.fft(y)
        # xf = np.fft.fftfreq(len(y), dt)
        # filter = (xf >= 0)
        # xfft = np.extract(filter, xf)
        # yfft = np.extract(filter, yf)
        # fig_fft, ax_fft  = plt.subplots()
        # ax_fft.plot(xfft, np.abs(yfft) , color ='b')
        # set_grid_format(ax_fft)
        # #ax_phase = ax_fft.twinx()
        # #ax_phase.plot(xfft, np.angle(yfft) , color = 'r')
        # fig_fft.show()


    def xy_plot(self):
        #pip install scipy
  
        fnx =  filedialog.askopenfilename(initialdir='.', title="Select isf file to open", filetypes = (("isffiles","*.isf"),("all files","*.*")))
        if fnx == "":
            print("No file select!!")
            return
        print("x axis file =" + fnx)
        fny =  filedialog.askopenfilename(initialdir='.', title="Select isf file to open", filetypes = (("isffiles","*.isf"),("all files","*.*")))
        if fny == "":
            print("No file select!!")
            return
        print("y axis file =" + fny)      
        wfmx = tek.TEKTONIX()
        wfmx.read_isf(fnx)  
        wfmy = tek.TEKTONIX()
        wfmy.read_isf(fny)    
        order = 2
        fs = 1.0 / wfmx.xydata["XINCR"] # sample rate, Hz
        cufoff = 100000 # desired cutoff frequency of the filter, Hz
        t = wfmx.xydata["XDATA"]
        x = wfmx.xydata["YDATA"]
        y = wfmy.xydata["YDATA"]
        x_filter= self.butter_lowpass_filter(x, cufoff, fs, order)                               
        y_filter= self.butter_lowpass_filter(y, cufoff, fs, order)   

        self.fig["time_y"],ax_td = plt.subplots(2, 1, figsize=(16,8), sharex=True) 
        line = ax_td
        line[0].plot(t, x, 'b')
        line[0].plot(t, x_filter, 'r')
        mplcursors.cursor(line[0] , hover = False, multiple = True)
        self.set_grid_format(line[0]) 

        line[1].plot(t, y, 'b')
        line[1].plot(t, y_filter, 'r')
        mplcursors.cursor(line[1] , hover = False, multiple = True)
        self.set_grid_format(line[1])  

        self.fig["xy"],ax_xy = plt.subplots(1, 1, figsize=(16,8), sharex=True)
        line_xy = ax_xy
        line_xy.plot(x, y, 'b')
        line_xy.plot(x_filter, y_filter, 'r')
        mplcursors.cursor(line_xy , hover = False, multiple = True) 
        self.set_grid_format(line_xy)             
     
        plt.tight_layout()     
        plt.show()    
        self.fig["time_y"].show()  
        self.fig["xy"].show()  

    def butter_lowpass(self,cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def butter_lowpass_filter(self,data, cutoff, fs, order=5):
        b, a = self.butter_lowpass(cutoff, fs, order=order)
        y = lfilter(b, a, data)
        return y     

    def fft(self):
        print("Not Available now!! Please Stay Tuned")
       
MENU().gui()
