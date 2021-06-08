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
#from mpldatacursor import datacursor
#https://pypi.org/project/mpldatacursor/
import ISF as isf

g = lambda x: x**2

def printg(i):
    print(g(i))


top = tk.Tk()                   
top.title("Tektronic Waveform Processor V1.0.200228")


# file selection 
row  = 0
col = 0
btn= {}
ch_sel = {}
for i in range(4):
    str_ch ="CH%d" % (i+1) 
    btn[str_ch] = tk.Button(top, text = str_ch ,command = lambda c = i :printg(c))
    btn[str_ch].grid(column = col, row = row + i, sticky=tk.W)

top.mainloop()