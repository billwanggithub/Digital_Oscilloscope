from timeit import default_timer as timer
import pandas as pd
from tkinter import ttk
from tkinter import filedialog
import tkinter as tk
import easygui as g
import csv
#import waveform as wave

top = tk.Tk() 
top.title("Tektronic Waveform Process")

ch_map1 = {0:'CH1', 1:'CH2', 2:'CH3', 3:'CH4'}
ch_map = {0:1, 1:2, 2:4, 3:8}
ch_choice = []
ch_sel = 0
chchkbox = [] 
fn = ''
time = []
wave = [[],[],[],[]]
time_start = 0
time_end = 0

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
                    if row[0] != "Model" and row[1]!="MDO4034C":
                        print("Not Corrent Model,MDO4034C waveform file!!")
                        break
                    else:
                        self.opencorrect = True
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
                            for ch in [0, 1, 2, 3]:
                                if (chnum  & ch_map[ch] ) == ch_map[ch] :
                                    if row[ch +1] != '':
                                        self.wave[ch].append(float(row[ch +1]))
                        if (data_cnt > 0) and (data_cnt % 500000) == 0:
                            #print(".",end = '',flush = True) 
                            self.pb['value'] = time_now - time_start                              
                            top.update_idletasks()                                                                   
                        if (data_cnt > 0) and (data_cnt % 5000000) == 0:
                            print("data number read = %d time = %f" % (data_cnt, time_now))   
                        data_cnt += 1                                                                           
                    if row[0] == "TIME" : # check if next line is real data
                        data_cnt = 1 
        self.pb['value'] = time_end - time_start
        top.update_idletasks()                    
        print('\nDone')  

    # def __str__(self):
    #     return 'Account({0}, {1}, {2})'.format(
    #         self.name, self.number, self.balance)    

def save_csvfile(fn, tin, din):
    df = pd.DataFrame(list(zip(*[tin,din])))
    df.to_csv(fn, index=False, header = False) 

def get_timerange(wfm):
    msg = "Enter the Waveform Start/TIme to Show"
    title = "Oscilloscope Waveform Viewer"
    fieldNames = ["Start TIme","End Time"]
    fieldValues = [str(wfm.time_start), str(wfm.time_end)]  # we start with defalut values
    fieldValues = g.multenterbox(msg,title, fieldNames, fieldValues)    
    return fieldValues

def get_file_length(fn):
    print("Calculate data length")
    with open(fn) as f:
        numline = len(f.readlines())
    print("length=", numline)
    return numline
 
def process_file():  
    global fn
    global time_start
    global time_end
    global ch_sel

    fn =  filedialog.askopenfilename(initialdir='.', title="Select csv file", filetypes = (("excel files","*.csv"),("all files","*.*")))
    print("filename=",fn)    
    wfm =Waveform(fn,pb)

    time_range = get_timerange(wfm)
    time_start = max(float(time_range[0]), wfm.time_start)
    time_end = min(float(time_range[1]), wfm.time_end)
    wfm.get_ch(time_start, time_end, ch_sel)

    start = timer()
    print("Start save file")
    for ch in [0, 1, 2, 3]:
        #if (chkbox1.value  & (0x01 << ch) ) == (0x01 << ch) :
        if (ch_sel  & ch_map[ch] ) == ch_map[ch] :
            print("Write ch%s.csv" % (ch + 1))
            print("time len =", len(wfm.time))
            print("wave len=", len(wfm.wave[ch]))
            save_csvfile('ch%s.csv' % (ch+1), wfm.time, wfm.wave[ch])   
            print("Write ch%s.csv done\n" % (ch + 1))    
    end = timer()
    print("\nprocess time = %f s" % (end - start))

def set_chsel():
    global ch_sel
    for ch in [0,1,2,3]:
        temp = ~(0x1 << ch) & 0xff
        ch_sel &= temp
        if ch_choice[ch].get() == 1:
            temp = (0x01) << ch
            ch_sel |= temp
    print("ch chebox =", ch_sel)

for ch in [0,1,2,3]:
    ch_choice.append(tk.IntVar())
    chchkbox.append(tk.Checkbutton(top, text = ch_map1[ch] , variable = ch_choice[ch], command=set_chsel).grid(column = ch + 1, row = 0)) 

pb = ttk.Progressbar(top,  maximum = 100, length = 200 , orient = 'horizontal', mode = 'determinate' )
pb.grid(column = 0, row = 1, columnspan=4, sticky=tk.W+tk.E+tk.N+tk.S)  

tk.Button(top, text = 'Process File', command =lambda : process_file()).grid(column = 0, row = 2, sticky=tk.W) 
tk.Button(top, text = 'View duty').grid(column = 1, row = 2, sticky=tk.W)         
tk.Label(top, text="Channel").grid(column = 0, row=0, sticky = tk.W)


top.mainloop()