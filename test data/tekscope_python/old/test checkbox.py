import os
# from tkinter import ttk
# from tkinter import filedialog
# from tkinter import messagebox
import tkinter as tk
#import easygui as ezgui
#import pandas as pd
import csv
import matplotlib.pyplot as plt
 
def callBackFunc():
    print(chkValue.get())
    print("Oh. I'm clicked")
    


top = tk.Tk() 
top.title("Tektronic Waveform Viewer")

chkValue = tk.BooleanVar() 
chkValue.set(True)
#tk.Checkbutton(top, text = 'grid' , var = chkValue, command=lambda : set_grid(ax)).grid(column =0, row = 0)
chkExample = tk.Checkbutton(top, text='Check Box', 
                            var=chkValue, command=callBackFunc) 
chkExample.grid(column=0, row=0)

# tk.Button(top, text = 'CH1', command =lambda : load_file(0)).grid(column = 0, row = 1, sticky=tk.W) 
# tk.Button(top, text = 'CH2', command =lambda : load_file(1)).grid(column = 1, row = 1, sticky=tk.W) 
# tk.Button(top, text = 'CH3', command =lambda : load_file(2)).grid(column = 2, row = 1, sticky=tk.W) 
# tk.Button(top, text = 'CH4', command =lambda : load_file(3)).grid(column = 3, row = 1, sticky=tk.W)

# tk.Button(top, text = 'ZOOM', command =lambda : set_limit()).grid(column =0, row = 2, sticky=tk.W) 
# pb = ttk.Progressbar(top,  maximum = 100, length = 200 , orient = 'horizontal', mode = 'determinate' )
# pb.grid(column = 0, row = 3, columnspan=5, sticky=(tk.W,tk.E,tk.N,tk.S))  

fig,ax = plt.subplots(4, 1, figsize=(15,8)) 
fig.show()
           
top.mainloop()