# timeout and dataout is saved as value changed list
def calc_duty(sample_time, timein, datain , timeout, dataout) :
    data_cnt = 0 # input list number
    data_old = 0 # old value
    period = 0.0
    time_now = 0    
    time01 = 0.0
    time10 = 0.0
    duty = 0.0
    check_zero = 0
    l2hcnt = 0
    for val in datain :
        time_now = timein[data_cnt] 
        if data_cnt > 0 :           
            # 0 -> 1, calculate period value
            if val > data_old:                                
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
                    #save old value
                    timeout.append(time01)
                    dataout.append(duty)                   
                    #save old value before dt
                    timeout.append(time_now-sample_time)
                    dataout.append(duty)      
                    #update time01 and time10     
                    time01 = time_now 
                    time10 = time_now
                check_zero = 0
                l2hcnt += 1
            # 1 -> 0, latch the time from high to low
            elif val < data_old :
                check_zero = 1
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

            data_old = val               
        data_cnt += 1