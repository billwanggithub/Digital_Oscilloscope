import csv
from matplotlib import pyplot

fname='tek0000ALL.csv'
tsample = 1.0 / 20000000 
data_start = 0
dt = tsample * 0.01
time = []
va = []
v1scale = 0
temp = 0.0
vb = []
vc = []
time_va = []
duty_va = []
time_vb = []
duty_vb = []
time_vc = []
duty_vc = []
time_now = 0
duty_va_temp = 0
duty_vb_temp = 0
duty_vc_temp = 0
va_old = 0
va_now = 0
vb_old = 0
vb_now = 0
vc_old = 0
vc_now = 0
va_time_rise = 0.0
va_time_fall = 0.0
vb_time_rise = 0.0
vb_time_fall = 0.0
vc_time_rise = 0.0
vc_time_fall = 0.0
period_a = 0
period_b = 0
period_c = 0

with open(fname) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    #rows = len(list(csv_reader))
    #print("rows =")
    line_count = 0
    
    f1 = open('ch1.csv', 'w')

    for row in csv_reader:
        # if line_count == 1000000:
        #     break    

        if (len(row) != 0):
            if row[0] == "Sample Interval":
                tsample = float(row[1]) 
                print("sampling time=", tsample)   
            if row[0] == "Vertical Scale":
                v1scale = float(row[1]) 
                print("ch1 scale=", v1scale)                 
            if data_start >= 1:
                if (data_start % 1000000) == 0:
                    print("data porcessed = ", data_start)                
                time.append(float(row[0]))
                temp = float(row[1]) #* v1scale
                va.append(temp)
                f1.write(row[0] + ',' + str(temp) +'\n')
                data_start += 1
            if row[0] == "TIME":
                data_start = 1

        line_count += 1


    # out = csv.writer(open("time.csv","w"), delimiter=',',quoting=csv.QUOTE_ALL)
    # out.writerow(time )

    print("samples number =", data_start - 1)
    f1.close
    print("write ch1 data to ch1.csv")

    pyplot.subplot(2,1,1)
    pyplot.plot(time,va)
    pyplot.tight_layout()
    pyplot.show()

''' with open(fname) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
        else:
            time_now = float(row[0])
            va_new = int(row[1])
            vb_new = int(row[2])
            vc_new = int(row[3])     

            if (time_now > 0): #discard time = 0
                if (va_old != va_new): # check va value change
                    if (va_new == 1): #rising edge
                        period_a = time_now - va_time_rise #calculate period
                        duty_va_temp = (va_time_fall - va_time_rise) / period_a
                        va_time_rise = time_now                 
                    else:
                        va_time_fall = time_now

                if (vb_old != vb_new): # check vb value change
                    if (vb_new == 1):
                        period_b = time_now - vb_time_rise
                        duty_vb_temp = (vb_time_fall - vb_time_rise) / period_b
                        vb_time_rise = time_now          
                    else:
                        vb_time_fall = time_now

                if (vc_old != vc_new): # check vc value change
                    if (vc_new == 1):
                        period_c = time_now - vc_time_rise
                        duty_vc_temp = (vc_time_fall - vc_time_rise) / period_c
                        vc_time_rise = time_now                   
                    else:
                        vc_time_fall = time_now

            #record pulse
            if (time_now == 0):
                time.append(time_now)
                va.append(va_now + 4)
                vb.append(vb_now + 2)
                vc.append(vc_now)
                duty_va.append(duty_va_temp)
                duty_vb.append(duty_vb_temp)
                duty_vc.append(duty_vc_temp)
            else: # expand +- dt
                time.append(time_now - dt)
                va.append(va_old + 4)
                vb.append(vb_old + 2)
                vc.append(vc_old )
                duty_va.append(duty_va_temp)
                duty_vb.append(duty_vb_temp)
                duty_vc.append(duty_vc_temp)
                time.append(time_now + dt)
                va.append(va_new + 4)
                vb.append(vb_new + 2)
                vc.append(vc_new)
                duty_va.append(duty_va_temp)
                duty_vb.append(duty_vb_temp)
                duty_vc.append(duty_vc_temp)
# save old values for edge detection
            va_old = va_new
            vb_old = vb_new
            vc_old = vc_new

        line_count += 1
    print(f'Processed {line_count} lines.')
    print(f'vb max duty= {max(duty_vb)} freq = {1/period_b}')
    print(f'vc max duty= {max(duty_vc)} freq = {1/period_c}')

pyplot.subplot(2,1,1)
pyplot.plot(time,va)
pyplot.plot(time,vb)
pyplot.plot(time,vc)
pyplot.xlim([0 , 10e-3])
pyplot.subplot(2,1,2)
pyplot.plot(time, duty_va)
pyplot.plot(time, duty_vb)
pyplot.plot(time, duty_vc)
pyplot.xlim([0 , 10e-3])
pyplot.tight_layout()
pyplot.show() '''