import csv
import numpy as np
import pandas as pd
import waveform as wave

#time = pd.read_csv("ch1.csv", usecols=[0])
time = pd.read_csv("ch1.csv")
time = time.transpose().values.tolist()

print("time type = ", type(time))
#print(time[0])
# print("time 1type = ", type(time1))
# print(time1[:][0])
# ch1d = []
# wave.convert_digital(10,time, ch1a, ch1d)
# print(ch1d[:100])
#row_list = df.to_csv(None, header=False, index=False).split('\n')

# wfm.convert_digital(10,wfm.time, wfm.ch[0], digital_data)
# wfm.decode_duty(wfm.sample_time, 10, wfm.time, wfm.ch[0], t_duty, duty)