import struct

with open('binfile.bin', 'wb') as f:
  for ix in range(256):
    f.write(struct.pack("=B", ix))