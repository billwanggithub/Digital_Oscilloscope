import tkinter as tk
from tkinter.colorchooser import askcolor
     
def setBgColor():
    (triple, hexstr) = askcolor()
    if hexstr:
        print(hexstr)
        push.config(bg=hexstr)
     
root = tk.Tk()
push = tk.Button(root, text='Set Background Color', command=setBgColor)
push.config(height=3, font=('times', 20, 'bold'))
push.pack(expand=tk.YES, fill=tk.BOTH)
root.mainloop()