#from pathlib import Path
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
import easygui as ezgui
import pandas as pd
import matplotlib.pyplot as plt
import MyFile as mf

btn = []
time = [[], [], [], []]
wave = [[], [], [], []]
fieldValues = ['0', '0', '0', '12', '0', '12', '0', '12', '0', '12' ]  # we start with defalut value
time_start = 0
time_end = 0
xlim_low = 0
xlim_high = 0
ylim_low = [0,0,0,0]
ylim_high = [0,0,0,0]

def set_limit_fit():
        # set xlimit, ylimit
        for ch in range(4):
            ax[ch].set_xlim([time_start , time_end])    
            # set_grid(ax)
            # ax[ch].set(xlabel='time (s)', ylabel='voltage (V)', title=tlt)
        
        print("Set X Axis from %fs to %fs" % (xlim_low, xlim_high)) 
        plt.tight_layout()             
        fig.show() 
        
def set_limit():
    # get X limit
    # datalines = len(time[0])
    # print('time len =',datalines)
    xlim_low = 0
    xlim_high = 0
    if len(time[0]) > 0:
        xlim_old = ax[0].get_xlim()
        #print("xlimit = %f ,%f" % (xlim_old[0], xlim_old[1]))
        for i in range(4):
            ylim = ax[i].get_ylim()
            ylim_low[i] = ylim[0]
            ylim_high[i] = ylim[1]
            #print("ylimit = %f ,%f" % (ylim_low[i], ylim_high[i]))            
        msg = "Enter the X/Y Axis Limits (X = %fs to %fs)" % (time_start, time_end)
        title = "Oscilloscope Waveform Viewer"
        fieldNames = ["X Start TIme","X End Time","CH1 Low","CH1 High","CH2 Low","CH2 High","CH3 Low","CH3 High","CH4 Low","CH4 High"]
        fieldValues = [xlim_old[0], xlim_old[1], ylim_low[0], ylim_high[0], ylim_low[1], ylim_high[1], ylim_low[2], ylim_high[2], ylim_low[3], ylim_high[3] ]
        fieldValues = ezgui.multenterbox(msg,title, fieldNames, fieldValues)
        #check xlimit input raege
        if float(fieldValues[1]) > float(fieldValues[0]) :
            xlim_low = float(fieldValues[0])
            xlim_high= float(fieldValues[1])  
        xlim_low = max(xlim_low , time_start)
        xlim_high= min(xlim_high, time_end)
        #print("xlimit = %f ,%f" % (xlim_low, xlim_high))
        # set xlimit, ylimit
        for ch in range(4):
            ylim_low[ch] = float(fieldValues[ch * 2 + 2])
            ylim_high[ch]= float(fieldValues[ch * 2 + 3])  
            ax[ch].set_ylim([ylim_low[ch] , ylim_high[ch]])  
            ax[ch].set_xlim([xlim_low , xlim_high])                
            set_grid(ax)
            tlt = 'CH'+str(ch)
            ax[ch].set(xlabel='time (s)', ylabel='voltage (V)', title=tlt)
        
        print("Set X Axis from %fs to %fs" % (xlim_low, xlim_high)) 
        plt.tight_layout()             
        fig.show()              

""" Set Grid ON/Off """
#https://riptutorial.com/matplotlib/example/14063/plot-with-gridlines
def set_grid(ax):         
    if chkValue.get() == True:
        for i in range(4):
            ax[i].minorticks_on()           
            ax[i].tick_params(labeltop=False, axis='both',width=2, colors='black',which='both')            
            ax[i].grid(b= True, axis='both', which='major', color='#666666', linestyle='-')            
            ax[i].grid(b= True, axis='both', which='minor', color='#999999', linestyle='-', alpha=0.2)    
    else:
        for i in range(4): 
            ax[i].grid(b= False, axis='both', which='major', color='#666666', linestyle='-')              
            ax[i].grid(b= False, axis='both', which='minor', color='#999999', linestyle='-', alpha=0.2)      
    fig.show()

def load_file(ch):
    global fieldValues
    global time_start
    global time_end
    print("ch=",ch)
    #print("btn=",btn[ch])
    fn =  filedialog.askopenfilename(initialdir='.', title="Select csv file to open", filetypes = (("excel files","*.csv"),("all files","*.*")))
    if fn == '':
        messagebox.showwarning("Waveform","No File Selected")    
        return
    if mf.get_file_size(fn) == 0:
        messagebox.showwarning('Read Data',"file length is zero!!")
        return        
    datalines = mf.read_csv_data(top, pb, fn, time[ch], wave[ch])      
    ax[ch].plot(time[ch],wave[ch],linewidth=1.0) 
    # 計算Y axix limits, auto scale
    ylim_low[ch] = min(wave[ch])
    ylim_high[ch] = max(wave[ch])
    # 計算X axix limits
    time_start = time[ch][0]
    time_end = time[ch][datalines - 1]  
    # Set X/Y limits
    ax[ch].set_ylim([ylim_low[ch] , ylim_high[ch]])  
    ax[ch].set_xlim([time_start , time_end]) 
    set_limit()
    set_grid(ax)
    fig.show() 

    
 

def clear_subplot(): 
    x1 = 0
    root= tk.Tk()

    label1 = tk.Label(root, text='Get channel number to clear')
    label1.config(font=('helvetica', 14))
    label1.pack()

    label2 = tk.Label(root, text='Type your Number(1~4):')
    label2.config(font=('helvetica', 10))
    label2.pack()

    entry1 = tk.Entry (root) 
    entry1.pack()

    def get_ch():     
        if entry1.get() == '':
            return
        if int(entry1.get()) == 0:
            return       
        x1 = int(entry1.get()) - 1
        root.destroy()
        print("ch=" + str(x1))
        ax[x1].clear()
        fig.show()        
        
    button1 = tk.Button(root, text='OK', command= lambda: get_ch(),bg='brown', fg='white', font=('helvetica', 9, 'bold'))
    button1.pack()
    root.mainloop() 


""" GUI Layout """   
top = tk.Tk() 
top.title("Tektronic Waveform Viewer")
#top.geometry('200x120')

chkValue = tk.BooleanVar() 
chkValue.set(True)
tk.Checkbutton(top, text = 'grid' , var = chkValue, command=lambda : set_grid(ax)).grid(column =0, row = 0)

tk.Button(top, text = 'CH1', command =lambda : load_file(0)).grid(column = 0, row = 1, sticky=tk.W) 
tk.Button(top, text = 'CH2', command =lambda : load_file(1)).grid(column = 1, row = 1, sticky=tk.W) 
tk.Button(top, text = 'CH3', command =lambda : load_file(2)).grid(column = 2, row = 1, sticky=tk.W) 
tk.Button(top, text = 'CH4', command =lambda : load_file(3)).grid(column = 3, row = 1, sticky=tk.W)
tk.Button(top, text = 'FITX', command =lambda : set_limit_fit()).grid(column =0, row = 2, sticky=tk.W)
tk.Button(top, text = 'ZOOM', command =lambda : set_limit()).grid(column =1, row = 2, sticky=tk.W)
tk.Button(top, text = 'Clear', command =lambda : clear_subplot()).grid(column =2, row = 2, sticky=tk.W)

pb = ttk.Progressbar(top,  maximum = 100, length = 200 , orient = 'horizontal', mode = 'determinate' )
pb.grid(column = 0, row = 3, columnspan=5, sticky=(tk.W,tk.E,tk.N,tk.S))  

""" the plot command must be place after tk command , otherwise the check button get() will not work """
fig,ax = plt.subplots(4, 1, figsize=(15,8))     
set_grid(ax)
plt.tight_layout() 
fig.show()           
top.mainloop()