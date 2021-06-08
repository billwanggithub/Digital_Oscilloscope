import csv
import waveform



filename = waveform.get_filename()
print(waveform.get_file_length(filename))

# with open('ch1.csv') as csv_file:
#     csv_reader = csv.reader(csv_file, delimiter=',')  
#     print(len(csv_file))