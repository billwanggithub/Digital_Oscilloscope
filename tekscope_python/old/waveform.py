import easygui as g
import tkinter
import csv
import pandas as pd
import sys
import PySimpleGUI as sg
import gui as gu
#from itertools import zip_longest

CH1 = 1
CH2 = 2
CH3 = 4
CH4 = 8 

class Waveform:
    def __init__(self, fn):    
        self.filename = fn
        self.opencorrect = False
        self.sample_time = 0
        self.time_start = 0
        self.time_end = 0
        self.time = []
        self.ch = [[],[],[],[]]
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
        print("total time=", self.total_time) 
        print("Start Time= %2.8f End Time =  %2.8f" % (self.time_start, self.time_end))        

    def get_ch(self, start_time, end_time, chnum):
        data_cnt = 0
        time_now = 0
        time_start = max(start_time, self.time_start)
        time_end = min(end_time, self.time_end)
        print("Porcess from %2.8f To %2.8f" % (time_start, time_end))

        #f1 = open('ch1.csv', 'w')

        #sg.OneLineProgressMeter('Processing Data', 0, time_end - time_start,'key','Extracting data ....',  orientation='v')
        pb = gu.progress_bar(time_end - time_start, 0)
        pb.go()
        with open(self.filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')  
            for row in csv_reader:                               
                if (len(row)> 0):
                    # if data_cnt >= 100:
                    #     break    
                    if time_now > time_end:
                        break                       
                    if data_cnt >= 1:
                        time_now = float(row[0])
                        if (time_now >= time_start):
                            self.time.append(time_now)
                            if (chnum & 1) == 1 :
                                self.ch[0].append(float(row[1]))
                            if (chnum & 2) == 2 :
                                self.ch[1].append(float(row[2]))
                            if (chnum & 4) == 4 :
                                self.ch[2].append(float(row[3]))
                            if (chnum & 8) == 8 :
                                self.ch[3].append(float(row[4]))

                        data_cnt += 1
                        if (data_cnt > 0) and (data_cnt % 100000) == 0:
                            #sg.OneLineProgressMeter('Processing Data', time_now - time_start, time_end - time_start, 'key','Extracting data ....',  orientation='v')
                            pb.update(time_now - time_start)
                        # if (data_cnt > 0) and (data_cnt % 100000) == 0:
                        #     print(".",end = '',flush = True)                        
                        # if (data_cnt > 0) and (data_cnt % 5000000) == 0:
                        #     print("\ndata number read = %d time = %f" % (data_cnt, time_now))                            
                    if row[0] == "TIME" : # check if next line is real data
                        data_cnt = 1   


    # def __str__(self):
    #     return 'Account({0}, {1}, {2})'.format(
    #         self.name, self.number, self.balance)    

# digital the analog waveform
def convert_digital(threshold, timein, datain , dataout) :
    data01 = 0
    for val in datain :
        if val >= threshold:
            data01 = 1
        else:
            data01 = 0            
        dataout.append(data01)

# calculate duty of input analog waveform, timeout and dataout is saved as value changed list
def decode_duty(sample_time, threshold, timein, datain , timeout, dataout) :
    data_cnt = 0 # input list number
    data_old = 0 # old value
    period = 0.0
    period_old =0
    time_now = 0    
    time01 = 0.0
    time10 = 0.0
    duty = 0.0
    data01 = 0
    l2hcnt = 0 #number of transition from low to high
    for val in datain :
        time_now = timein[data_cnt] 
        if val >= threshold:
            data01 = 1
        else:
            data01 = 0

        if data_cnt > 0 :           
            # 0 -> 1, calculate period value
            if data01 > data_old:                                
                if time01 == 0  : 
                    time01 = time_now 
                    #first transition detected
                    if l2hcnt == 0 : 
                        timeout.append(timein[0])
                        dataout.append(0)
                    timeout.append(time01 - sample_time)
                    dataout.append(duty)                                                                      
                else :
                    period = time_now - time01
                    duty = (time10 - time01) / period 
                    if (period <= (period_old * 1.2)) and (period >= (period_old * 0.8)):
                        #save old value
                        timeout.append(time01)
                        dataout.append(duty)                   
                        #save old value before dt
                        timeout.append(time_now-sample_time)
                        dataout.append(duty)      
                        #update time01 and time10     
                        time01 = time_now 
                        time10 = time_now
                    period_old = period
                l2hcnt += 1
            # 1 -> 0, latch the time from high to low
            elif data01 < data_old :
                time10 = time_now 

            # if (check_zero== 1) and (period > 0) and ((time_now - time01) >= (period *2)):
            #     #print("check_zero time =", time_now)
            #     duty = (time10 - time01) / period
            #     timeout.append(time01)
            #     dataout.append(duty) 
            #     timeout.append(time01 + period)
            #     dataout.append(duty)     
            #     timeout.append(time01 + period + sample_time)
            #     dataout.append(0)                     
            #     duty = 0    
            #     time01 = 0
            #     time10 = 0             
            #     check_zero = 0   

            data_old = data01               
        data_cnt += 1

def get_filename():
    fn= g.fileopenbox(default="*.csv")
    return fn

def get_file_length(fn):
    print("Calculate data length")
    with open(fn) as f:
        numline = len(f.readlines())
    print("length=", numline)
    return numline
    # with open(filename) as f:
    #     return sum(1 for line in f)

# read data file into list
def read_data(fn, tout, dout):    
    data_cnt = 0
    with open(fn) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')  
        rowlines= get_file_length(fn)
        print("data count =", rowlines)
        print("Read Data")
        for row in csv_reader:                               
            if (len(row)> 0):              
                time_now = float(row[0])
                tout.append(time_now)
                dout.append(float(row[1]))
                data_cnt += 1
                if (data_cnt > 0) and (data_cnt % 100000) == 0:
                        sg.OneLineProgressMeter('Read  Data', data_cnt, rowlines, 'key','Reading data ....',  orientation='v', grab_anywhere= True)
                if (data_cnt > 0) and (data_cnt % 100000) == 0:
                    print(".",end = '',flush = True)
    print("\nDone")
    return rowlines

def save_csvfile(fn, tin, din):
    print("Save Data to %s" % (fn)) 
    df = pd.DataFrame(list(zip(*[tin,din])))
    df.to_csv(fn, index=False, header = False) 
    print("\nDone")