#!/usr/bin/python

import sys

if (len(sys.argv) < 2):
	print "I'm afraid I can't do that Dave!"
else:
	f     = open(str(sys.argv[1]),'r')
	lines = f.readlines()
	
	success = 0
	total = 0
	m = 0
	r = 0
	eof_line = "EOF was not reached!"
	for i in range(0,len(lines)):
		if "Resending" in lines[i]:
			r += 1
		if "elapsed" in lines[i]:
			m += 1
		if "Result" in lines[i]:
			total += 1
		if "Result=0" in lines[i]:
			success += 1
		if "EOF reached" in lines[i]:
			eof_line = lines[i]
		else:
			continue
	
	num_words =  int(str.split(lines[1])[3])
	
	print "-------------------------------------------------------"
	print "Filename: " + sys.argv[1]
	print "Total number of words in transfer: " + str(num_words)
	print "Messages sent (excluding resend): " + str(m)
	print "Number of resends: " + str(r) + "/" + str(r + m) + " = " + str(float(r)/(r+m))
	print "Message reports efficiency of transfer: " + str(success) + "/" + str(total) + " = " + str(float(success)/total)
	print "Average OPM (success only/total): " + str(float(success)/(r+m)) + "/" + str(float(total)/(r+m))
	
	if len(str.split(eof_line)) > 4:
		runtime = float(str.split(eof_line)[4])
		
		print "Total runtime: " + str(runtime) + " sec"
		print "Average time per message: " + str(runtime/(r+m)) + " sec = " + str(1/(runtime/(r+m))) + " messages/sec"
		print "Time used for resends (based on avg): " + str((runtime/(r+m))*(r)) + " sec"
		print "Average time per operation: " + str(runtime/total) + " sec"
		print "Average OPS: " + str((float(success)/(r+m))*(1/(runtime/(r+m)))) + "/" + str((float(total)/(r+m))*4)
		print "Transfer goodput: " + str((num_words*2)/runtime) + " bytes/sec"
		print "Transfer throughput: " + str((num_words*2)/runtime + (m*2*2)/runtime) + " bytes/sec"
	print "-------------------------------------------------------"
	