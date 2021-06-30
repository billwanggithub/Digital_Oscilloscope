import easygui as g
import csv
import matplotlib.pyplot as plt
#import numpy as np
import cursor as cur
import waveform as wave
# from time import sleep
# from oscilloscope import Osc


##########################################################################
#         Test Program
##########################################################################
t_duty = []
duty = []
digital_data = []
filename = get_filename()
print("filename = ",filename)

wfm =wave.Waveform(filename)

# Select channels
msg = "Select Channels"
title = "Oscilloscope Waveform Viewer"
listOfOptions = ["CH1", "CH2", "CH3" , "CH4"]
ch_choice = g.multchoicebox(msg , title, listOfOptions)
ch_map = {'CH1':wave.CH1, 'CH2':wave.CH2, 'CH3':wave.CH3, 'CH4':wave.CH4}
ch_sel = 0
print("Channels selected:")
for ch in ch_choice:
    ch_sel |= ch_map[ch]
    print("%s " % (ch))

# Select time range
msg = "Enter the Waveform Start/TIme to Show"
title = "Oscilloscope Waveform Viewer"
fieldNames = ["Start TIme","End Time"]
fieldValues = [str(wfm.time_start), str(wfm.time_end)]  # we start with defalut values
fieldValues = g.multenterbox(msg,title, fieldNames, fieldValues)
time_start = float(fieldValues[0])
time_end = float(fieldValues[1])

time_start = max(time_start, wfm.time_start)
time_end = min(time_end, wfm.time_end)
g.msgbox("Process waveform from %fs to %fs" % (time_start, time_end))

# extract selected channels
wfm.get_ch(time_start, time_end, ch_sel)
if (chnum & wave.CH1) == wave.CH1 :
    wfm.save_file('ch1.csv', wfm.time, wfm.ch[0])
if (chnum & wave.CH2) == wave.CH2 :
    wfm.save_file('ch2.csv', wfm.time, wfm.ch[1])
if (chnum & wave.CH3) == wave.CH3 :
    wfm.save_file('ch3.csv', wfm.time, wfm.ch[2])
if (chnum & wave.CH4) == wave.CH4 :
    wfm.save_file('ch4.csv', wfm.time, wfm.ch[3])            
# calculate the duty cycles
# wfm.convert_digital(10,wfm.time, wfm.ch[0], digital_data)
# wfm.decode_duty(wfm.sample_time, 10, wfm.time, wfm.ch[0], t_duty, duty)
print("Done!!")

# get X limit
msg = "Enter the X/Y Axis Limits (X = %fs to %fs)" % (time_start, time_end)
title = "Oscilloscope Waveform Viewer"
fieldNames = ["X Start TIme","X End Time","CH1 Low","CH1 High","CH2 Low","CH2 High","CH3 Low","CH3 High","CH4 Low","CH4 High"]
fieldValues = [str(time_start), str(time_end), 0, 12, 0, 12, 0, 12, 0, 12 ]  # we start with defalut values
fieldValues = g.multenterbox(msg,title, fieldNames, fieldValues)
#check input raege
ylim_low = [0,0,0,0]
ylim_high = [0,0,0,0]
if float(fieldValues[1]) > float(fieldValues[0]) :
    xlim_low = float(fieldValues[0])
    xlim_high= float(fieldValues[1])  
xlim_low = max(xlim_low, time_start)
xlim_high= min(xlim_high, time_end)
for ch in [0,1,2,3]:
    ylim_low[ch] = float(fieldValues[ch * 2 + 2])
    ylim_high[ch]= float(fieldValues[ch * 2 + 3])  
print("Set X Axis from %fs to %fs" % (xlim_low, xlim_high))

fig,ax = plt.subplots(4, 1, figsize=(15,8)) 
#plot analog waveform
for ch in [0,1,2,3]:
    if len(wfm.ch[ch]) > 0:
        ax[ch].plot(wfm.time,wfm.ch[ch])  

# ax[0].plot(wfm.time, digital_data)
# ax[1].plot(wfm.time, digital_data)
# ax[1].plot(t_duty, duty)     

# Set Axis Limits

cursor_snap = [0,0,0,0]
for ch in [0,1,2,3]:
    ax[ch].set_xlim([xlim_low , xlim_high])  
    ax[ch].set_ylim([ylim_low[ch] , ylim_high[ch]]) 
    cursor_snap[ch] = cur.SnaptoCursor(ax[ch],wfm.time,wfm.ch[ch])
    fig.canvas.mpl_connect('motion_notify_event', cursor_snap[ch].mouse_move)
# Snap Cursor
# cursor0 = SnaptoCursor(ax[0],wfm.time,wfm.ch[0])
# fig.canvas.mpl_connect('motion_notify_event', cursor0.mouse_move)
# cursor1 = SnaptoCursor(ax[1],wfm.time,wfm.ch[1])
# fig.canvas.mpl_connect('motion_notify_event', cursor1.mouse_move)
# cursor2 = SnaptoCursor(ax[2],wfm.time,wfm.ch[2])
# fig.canvas.mpl_connect('motion_notify_event', cursor2.mouse_move)
# cursor3 = SnaptoCursor(ax[3],wfm.time,wfm.ch[3])
# fig.canvas.mpl_connect('motion_notify_event', cursor3.mouse_move)            
# print("type:",type(cursor1))

plt.tight_layout()

while True:
    fig.show()
    fieldValues = [str(xlim_low ), str(xlim_high), 
        ylim_low[0], ylim_high[0], ylim_low[1], ylim_high[1], ylim_low[2], ylim_high[2], ylim_low[3], ylim_high[3]]  # we start with defalut values
    fieldValues = g.multenterbox(msg,title, fieldNames, fieldValues)
    #check input raege    
    if float(fieldValues[1]) > float(fieldValues[0]) :
        xlim_low = float(fieldValues[0])
        xlim_high= float(fieldValues[1])  
    xlim_low = max(xlim_low, time_start)
    xlim_high= min(xlim_high, time_end)
    for ch in [0,1,2,3]:
        ylim_low[ch] = float(fieldValues[ch * 2 + 2])
        ylim_high[ch]= float(fieldValues[ch * 2 + 3])     

    for ch in [0,1,2,3]:
        ax[ch].set_xlim([xlim_low , xlim_high])  
        ax[ch].set_ylim([ylim_low[ch] , ylim_high[ch]]) 

    print("Set X Axis from %fs to %fs" % (xlim_low, xlim_high))
