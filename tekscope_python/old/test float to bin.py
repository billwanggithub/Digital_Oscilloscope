import sys
import struct

data = [1.0,  1.2, 1.5, 1.7 , 1.8, 1.9, 2.0]

handle = open('floats.bin', 'wb')
handle.write(struct.pack('<%df' % len(data), *data))
handle.close()

handle = open('doubles.bin', 'wb')
handle.write(struct.pack('<%dd' % len(data), *data))
handle.close()