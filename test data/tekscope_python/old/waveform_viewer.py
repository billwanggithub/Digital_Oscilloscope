
import easygui as g
import tkinter as tk
import csv
import matplotlib.pyplot as plt
#import numpy as np
import cursor as cur
import waveform as wave

t_duty = [[],[],[],[]]
ch_duty = [[],[],[],[]]
datalines = 0

fn0 = wave.get_filename()
datalines0 = wave.read_data(fn0, t_duty[0], ch_duty[0])
fn1 = wave.get_filename()
datalines1 = wave.read_data(fn1, t_duty[1], ch_duty[1])

time_start = float(t_duty[0][0])
time_end = float(t_duty[0][datalines0 - 1])

print("time: %fs to %fs " % (time_start, time_end))

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
    if len(ch_duty[ch]) > 0:
        ax[ch].plot(t_duty[ch],ch_duty[ch])  

# ax[0].plot(wfm.time, digital_data)
# ax[1].plot(wfm.time, digital_data)
# ax[1].plot(t_duty, duty)     

# Set Axis Limits

cursor_snap = [0,0,0,0]
for ch in [0,1,2,3]:
    ax[ch].set_xlim([xlim_low , xlim_high])  
    ax[ch].set_ylim([ylim_low[ch] , ylim_high[ch]]) 
    cursor_snap[ch] = cur.SnaptoCursor(ax[ch],t_duty[ch],ch_duty[ch])
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