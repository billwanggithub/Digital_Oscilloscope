
#http://www.tastones.com/zh-tw/tutorial/tkinter/tkinter-askquestion-dialog/
from timeit import default_timer as timer
import pandas as pd
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
import easygui as ezgui
import csv
import os
#import waveform as wave


ch_map1 = {0:'CH1', 1:'CH2', 2:'CH3', 3:'CH4'}
ch_map = {0:1, 1:2, 2:4, 3:8}
ch_choice = []
ch_sel = 0
chchkbox = [] 

# fn = ''
# time = []
# wave = [[],[],[],[]]
# time_start = 0
# time_end = 0

class Waveform:
    def __init__(self, fn, pb):    
        self.filename = fn
        self.opencorrect = False
        self.sample_time = 0
        self.time_start = 0
        self.time_end = 0
        self.time = []
        self.wave = [[],[],[],[]]
        self.pb = pb
        self.get_info()

    def get_info(self):
        line_count = 0
        with open(self.filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')  
            for row in csv_reader:
                if line_count == 0:
                    if row[0] != "Model" and (row[1]!="MDO4034C" or row[1]!='DPO3034'):
                        print("Not Corrent Model,MDO4034C waveform file!!")
                        messagebox.showwarning("Waveform","Not Correct Waveform format!!")
                        break
                    else:
                        self.opencorrect = True
                    print("Oscilloscope =", row)
                if line_count > 30:
                    break
                if (len(row) != 0):
                    if row[0] == "Sample Interval":
                        self.sample_time = float(row[1]) 
                    if row[0] == "Record Length":
                        record_cnt = float(row[1])
                        self.total_time = record_cnt * self.sample_time                         
                    if row[0] == "TIME": 
                        #read next line
                        data = next(csv_reader)
                        self.time_start = float(data[0])
                        self.time_end = self.time_start + self.total_time - self.sample_time                    
                line_count += 1 

        print("sampling time=", self.sample_time)  
        print("File total time=", self.total_time) 
        print("File Start Time= %2.8f End Time =  %2.8f" % (self.time_start, self.time_end))        

    def get_ch(self, time_start, time_end, chnum):
        data_cnt = 0
        time_now = 0
        ch_map = {0:1, 1:2, 2:4, 3:8}
        print("Read wave %d from %2.8fs To %2.8fs" % (chnum, time_start, time_end))
        self.pb['maximum'] = time_end - time_start
        with open(self.filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')  
            for row in csv_reader:                               
                if (len(row)> 0):
                    if time_now > time_end:
                        break                       
                    if data_cnt >= 1:
                        time_now = float(row[0])
                        if (time_now >= time_start):
                            self.time.append(time_now)
                            for ch in range(4):
                                if (chnum  & ch_map[ch] ) == ch_map[ch] :
                                    if row[ch +1] != '':
                                        self.wave[ch].append(float(row[ch +1]))
                        if (data_cnt > 0) and (data_cnt % 200000) == 0:
                            #print(".",end = '',flush = True) 
                            self.pb['value'] = time_now - time_start                              
                            top.update()                                                                   
                        if (data_cnt > 0) and (data_cnt % 5000000) == 0:
                            print("data number read = %d time = %f" % (data_cnt, time_now))   
                        data_cnt += 1                                                                           
                    if row[0] == "TIME" : # check if next line is real data
                        data_cnt = 1 
        self.pb['value'] = time_end - time_start
        top.update()                    
        print('\nDone')  

    # def __str__(self):
    #     return 'Account({0}, {1}, {2})'.format(
    #         self.name, self.number, self.balance)    
    
# calculate duty of input analog waveform, tdig/ddig/tduty/dduty saved as value changed list
def decode_duty(sample_time, threshold, timein, datain , tdig, ddig, tduty, dduty) :
    thdl = threshold * 0.8
    thdh = threshold * 1.2
    data_cnt = 0 # input list number
    data01 = 0 #digital data
    data01_old = 0 # old value of digital data
    period = 0.0
    duty = 0.0    
    time_now = 0    
    time01 = 0.0 #time @ 0 --> 1
    time10 = 0.0 #time @ 1 --> 0  
    cnt_01= 0 #number of transition from low to high
    val_old = 0
    
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
                    tdig.append(time_now)
                    ddig.append(data01)                     
            # at falling, must less then thdl
            elif val < val_old:
                if val <= thdl:
                    data01 = 0  
                    # save at rising/falling edge
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
                    duty = 0                                                                    
                else :
                    #save old duty before dt
                    tduty.append(time01 - sample_time)
                    dduty.append(duty)                      
                    #save new value
                    period = time_now - time01
                    duty = (time10 - time01) / period                                       
                    tduty.append(time01)
                    dduty.append(duty)                    
                    #update time01 and time10     
                    time01 = time_now 
                    time10 = time_now
                cnt_01+= 1
            # 1 -> 0, latch the time from high to low
            elif data01 < data01_old :
                time10 = time_now 
            data01 = data01
        data01_old = data01   
        val_old = val                        
        data_cnt += 1
        
    #save last duty
    tduty.append(time01 - sample_time)
    dduty.append(duty)    
    tduty.append(time_now)
    dduty.append(duty)            
    return cnt_01

# read data file into list
def read_data(fn, tout, dout): 
    global pb   
    data_cnt = 0
    linecnt = 0
    with open(fn) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')  
        rowlines= get_file_length(fn)
        pb['maximum'] = rowlines
        print("data count =", rowlines)
        print("Read Data")
        for row in csv_reader:                               
            if (len(row)> 0):              
                time_now = float(row[0])
                tout.append(time_now)
                dout.append(float(row[1]))
                data_cnt += 1
                if (data_cnt > 0) and (data_cnt % 100000) == 0:
                    pb['value'] = linecnt   
                    top.update()                           
                    #top.update_idletasks()  
                if (data_cnt > 0) and (data_cnt % 100000) == 0:
                    print(".",end = '',flush = True)
                if (data_cnt > 0) and (data_cnt % 5000000) == 0:
                    print('\n')
                linecnt += 1
    pb['value'] = rowlines                              
    top.update()                 
    print("\nDone")
    return rowlines

def save_csvfile(fn, tin, din):
    print("Write ",fn)
    df = pd.DataFrame(list(zip(*[tin,din])))
    df.to_csv(fn, index=False, header = False) 
    print("Write DOne")

def get_timerange(wfm):
    msg = "Enter the Waveform Start/TIme to Show"
    title = "Oscilloscope Waveform Viewer"
    fieldNames = ["Start TIme","End Time"]
    fieldValues = [str(wfm.time_start), str(wfm.time_end)]  # we start with defalut values
    fieldValues = ezgui.multenterbox(msg,title, fieldNames, fieldValues)    
    return fieldValues

def get_file_length(fn):
    print("Calculate data length")
    df = pd.read_csv(fn, header = None)
    numline = len(df)
    # with open(fn) as f:
    #     numline = len(f.readlines())
    # print("length=", numline)
    return numline
 
def process_file():  
    # global time_start
    # global time_end
    global ch_sel

    if ch_sel == 0:
        messagebox.showwarning("Waveform","No Channel Selected")
        return
    fn =  filedialog.askopenfilename(initialdir='.', title="Select csv file to open", filetypes = (("excel files","*.csv"),("all files","*.*")))
    if fn == '':
        messagebox.showwarning("Waveform","No File Selected")
        return
    print("filename=",fn)    
    wfm =Waveform(fn,pb)

    time_range = get_timerange(wfm)
    time_start = max(float(time_range[0]), wfm.time_start)
    time_end = min(float(time_range[1]), wfm.time_end)
    wfm.get_ch(time_start, time_end, ch_sel)

    start = timer()
    print("Start save file")
    for ch in range(4):
        if (ch_sel  & ch_map[ch] ) == ch_map[ch] :
            save_csvfile('ch%s.csv' % (ch+1), wfm.time, wfm.wave[ch])     
    end = timer()
    msg = "\nprocess time = %f s" % (end - start)
    print(msg)
    messagebox.showinfo("Waveform",msg)

def process_duty():
    tout = []
    dout = []
    tdigital = []
    ddigital = []
    tduty = []
    dduty = []
    if e1.get() == '':
        messagebox.showwarning("Duty","Please enter threshold value")
        return      
    threshold = float(e1.get())
    print('threshold =', threshold)
    # get the waveform to process
    fn =  filedialog.askopenfilename(initialdir='.', title="Select csv file to open", filetypes = (("excel files","*.csv"),("all files","*.*")))
    if fn == '':
        messagebox.showwarning("Duty","No File Selected")
        return
    print("filename=",fn) 
    read_data(fn, tout, dout)
    decode_duty(2e-7, threshold, tout, dout, tdigital, ddigital, tduty, dduty)
        
    (file, ext) = os.path.splitext(fn)
    # print("Full file path without extension =", file)
    # print("Extension =", ext)    
    
    save_csvfile(file+"_duty.csv", tduty, dduty)   
    save_csvfile(file+"_digital.csv", tdigital, ddigital)   
    messagebox.showinfo("Duty","File saved OK!!") 

def set_chsel():
    global ch_sel
    for ch in range(4):
        temp = ~(0x1 << ch) & 0xff
        ch_sel &= temp
        if ch_choice[ch].get() == 1:
            temp = (0x01) << ch
            ch_sel |= temp
    print("ch chebox =", ch_sel)

top = tk.Tk() 
top.title("Tektronic Waveform Process")

tk.Label(top, text="Channel").grid(column = 0, row=0, sticky = tk.W)
for ch in range(4):
    ch_choice.append(tk.IntVar())
    chchkbox.append(tk.Checkbutton(top, text = ch_map1[ch] , variable = ch_choice[ch], command=set_chsel).grid(column = ch + 1, row = 0)) 

L1 = tk.Label(top, text="Threshold(V)").grid(column = 0, row = 1, sticky=tk.E)

thd_val = tk.StringVar
e1 = tk.Entry(top, textvariable = thd_val, width = 6, bd =5)
e1.grid(column = 1, row = 1, sticky=tk.E) 

tk.Button(top, text = 'Waveform', command =lambda : process_file()).grid(column = 0, row = 2, sticky=tk.W) 
tk.Button(top, text = 'Duty',command =lambda : process_duty()).grid(column = 1, row = 2, sticky=tk.W)         

pb = ttk.Progressbar(top,  maximum = 100, length = 200 , orient = 'horizontal', mode = 'determinate' )
pb.grid(column = 0, row = 3, columnspan=5, sticky=(tk.W,tk.E,tk.N,tk.S))  





top.mainloop()

