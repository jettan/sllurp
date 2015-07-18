#!/usr/bin/python

# Generate an Intel Hex file with
# random data with 2*argv[1] data bytes in each record.
#
# Jethro Tan
# Delft University of Technology - 2015


import random
import sys
import math

# Generate Intel Hex file with this many bytes of data.
SIZE = 5*1024

# Start address for data of the Intel Hex file.
START = "6400"


if (len(sys.argv) < 2):
	print "Please specify the number of data words for each record as argument!"
else:
	# Initialize variables.
	num_bytes = 2 * int(sys.argv[1])
	address = int("0x" + START, 0)
	
	# Calculate number of records to generate.
	num_records = int(math.ceil((0.0 + SIZE) / num_bytes))
	
	# Keep track of how many bytes still need to be generated.
	remaining_bytes = SIZE
	
	for i in range(0, num_records):
		# Construct bytefield.
		bytefield = "{:02X}".format(num_bytes)
		
		# Construct address field.
		current_address = address + num_bytes * i
		address_field = "{:04X}".format(current_address)
		
		if (remaining_bytes > num_bytes):
			remaining_bytes -= num_bytes
		else:
			num_bytes = remaining_bytes
			remaining_bytes -= num_bytes
		
		# Construct random data field.
		data = ""
		for j in range (0, num_bytes):
			r = random.randint(0,255)
			data += "{:02X}".format(r)
		
		# Construct the record so far.
		record = bytefield + address_field + "00" + data
		
		# Calculate the checksum of the entire record.
		checksum = 0
		for j in range(0, len(record)/2):
			checksum += int("0x"+ record[2*j:2*j+2], 0)
		checksum = 256 - (checksum % 256)
		checksum = "{:02X}".format(checksum)
		if (checksum == "100"):
			checksum = "00"
		
		# Assemble the whole record and print.
		record = ":" + record + checksum
		print record
		
	# End of File.
	print ":00000001FF"

