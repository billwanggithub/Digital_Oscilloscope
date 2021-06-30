import tkinter as tk
from tkinter.ttk import *
import easygui as g
import matplotlib.pyplot as plt
#import numpy as np
import cursor as cur

def get_timerange(wfm):
    msg = "Enter the Waveform Start/TIme to Show"
    title = "Oscilloscope Waveform Viewer"
    fieldNames = ["Start TIme","End Time"]
    fieldValues = [str(wfm.time_start), str(wfm.time_end)]  # we start with defalut values
    fieldValues = g.multenterbox(msg,title, fieldNames, fieldValues)    
    return fieldValues

class CheckBoxChSel:
    top = tk.Tk()
    title = "Select Channels"
    ch_map = {0:'CH1', 1:'CH2', 2:'CH3', 3:'CH4'}
    ch_choice = []
    chchkbox = []  
    value = 0  

    def __init__(self):    
        print("creat channel check box")
        self.top.title(self.title)
        self.top.minsize(200,30)
        for ch in [0,1,2,3]:
            self.ch_choice.append(tk.IntVar())
            self.chchkbox.append(tk.Checkbutton(self.top, text = self.ch_map[ch] , variable = self.ch_choice[ch], command=self.set_chsel))
            self.chchkbox[ch].grid(column = ch, row = 1)         

    def go(self):
        self.top.mainloop()
    
    def dismiss(self):
        self.top.quit()

    def set_chsel(self,event = None):
        for ch in [0,1,2,3]:
            temp = ~(0x1 << ch) & 0xff
            self.value &= temp
            if self.ch_choice[ch].get() == 1:
                temp = (0x01) << ch
                self.value |= temp
        print("ch chebox =", self.value)

class progress_bar:
    def __init__(self, max, value):  
        # creating tkinter window 
        self.value = value
        self.max = max
        root = tk.Tk()     
        # Progress bar widget 
        self.progress = Progressbar(root,  
              length = self.max, mode = 'determinate') 
        self.progress.pack(pady = 10) 
        self.progress['value'] =  self.value
    
    def update(self, value):
        self.value = value
        self.progress['value'] = value




