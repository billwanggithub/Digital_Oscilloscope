import csv
import numpy as np
import waveform as wave

time = []
ch = [[],[],[],[]]

t_duty = [[],[],[],[]]
ch_duty = [[],[],[],[]]
fn = wave.get_filename()
wave.read_data(fn, time, ch[0])
#wfm.convert_digital(10,time, ch[0], digital_data)
wave.decode_duty(2e-7, 10, time, ch[0], t_duty[0], ch_duty[0])
wave.save_csvfile('ch1_duty.csv', t_duty[0], ch_duty[0])

