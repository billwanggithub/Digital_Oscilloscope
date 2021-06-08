import os
import csv
import pandas as pd
import pprint


# class ReadCSVRecord:
#     def __init__(self, fn):
#         self.filename = fn
# 		self.data = []

# 	def read(self):
# 		with open(self.filename, 'r') as f:
# 			reader = csv.reader(f)
# 			self.data = [float(row[0]) for row in reader]
# 		return self.data
	
# 	def print_data(self):
# 		pprint.pprint(self.data)
  
""" this function will return the file size """
def get_file_size(file_path):
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return file_info.st_size
    
""" this function will return lines of the file """
def get_csv_file_length(fn):
    if get_file_size(fn) == 0:
        print("File Size is Zero!!")
        return
    print("Calculate data length")
    df = pd.read_csv(fn, header = None)
    numline = len(df)
    # with open(fn) as f:
    #     numline = len(f.readlines())
    # print("length=", numline)
    return numline

""" Read CSV File to list 
    pb: messagebox
"""    
def read_csv_data(tktop, pb, fn, tout, dout): 
    data_cnt = 0
    linecnt = 0
    with open(fn) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')  
        rowlines= get_csv_file_length(fn)
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
                    if tktop != 'None':
                        pb['value'] = linecnt   
                        tktop.update()                           
                    #top.update_idletasks()  
                if (data_cnt > 0) and (data_cnt % 100000) == 0:
                    print(".",end = '',flush = True)
                if (data_cnt > 0) and (data_cnt % 5000000) == 0:
                    print('\n')
                linecnt += 1
    if tktop != 'None':
        pb['value'] = rowlines                              
        tktop.update()                 
    print("\nDone")
    return rowlines