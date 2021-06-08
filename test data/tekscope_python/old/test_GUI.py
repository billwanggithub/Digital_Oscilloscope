from tkinter import filedialog
from tkinter import ttk
import tkinter as tk
import waveform as wfm

# creating tkinter window 
top = tk.Tk() 
top.title("Tektronic Waveform Process")
#top.minsize(400,30)

class GUI:
    ch_map = {0:'CH1', 1:'CH2', 2:'CH3', 3:'CH4'}
    ch_choice = []
    chchkbox = []  
    value = 0
    
    ch_sel = 0

    def __init__(self, root):   
        self.root = root 
        self.fn = ''  

    def get_filename(self):        
        self.fn =  filedialog.askopenfilename(initialdir='.', title="Select csv file", filetypes = (("excel files","*.csv"),("all files","*.*")))
        print(self.fn)

    def layout(self):
        # Progress bar widget 
        pb = ttk.Progressbar(self.root,  maximum = 100, length = 200 , orient = 'horizontal', mode = 'determinate' )
        pb.grid(column = 0, row = 1, columnspan=4, sticky=tk.W+tk.E+tk.N+tk.S)  

        tk.Button(self.root, text = 'Select File', command =lambda : self.get_filename()).grid(column = 0, row = 2, sticky=tk.W) 
        tk.Button(self.root, text = 'Go').grid(column = 1, row = 2, sticky=tk.W)         
        tk.Label(self.root, text="Channel").grid(column = 0, row=0, sticky = tk.W)
        for ch in [0,1,2,3]:
            self.ch_choice.append(tk.IntVar())
            self.chchkbox.append(tk.Checkbutton(self.root, text = self.ch_map[ch] , variable = self.ch_choice[ch], command=self.set_chsel).grid(column = ch + 1, row = 0)) 

        self.root.mainloop()

    def set_chsel(self,event = None):
        for ch in [0,1,2,3]:
            temp = ~(0x1 << ch) & 0xff
            ch_sel &= temp
            if self.ch_choice[ch].get() == 1:
                temp = (0x01) << ch
                ch_sel |= temp
        print("ch chebox =", ch_sel)

    # def bar(self): 
    #     import time 
    #     pb['value'] = 20
    #     self.root.update_idletasks() 
    #     time.sleep(1) 
    
    #     pb['value'] = 40
    #     self.root.update_idletasks() 
    #     time.sleep(1) 
    
    #     pb['value'] = 50
    #     self.root.update_idletasks() 
    #     time.sleep(1) 
    
    #     pb['value'] = 60
    #     self.root.update_idletasks() 
    #     time.sleep(1) 
    
    #     pb['value'] = 80
    #     self.root.update_idletasks() 
    #     time.sleep(1) 
    #     pb['value'] = 100

    def get_file_length(self, fn):
        print("Calculate data length")
        with open(fn) as f:
            numline = len(f.readlines())
        print("length=", numline)
        return numline

        

gui =GUI(top).layout()

# This button will initialize 
# the progress bar 

# infinite loop      