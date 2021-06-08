#http://www.tastones.com/zh-tw/tutorial/tkinter/tk-file-dialogs/
from tkinter import filedialog
import tkinter as tk
top = tk.Tk() 
filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
print (filename)


