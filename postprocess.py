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
	s = 0
	eof_line = "EOF was not reached!"
	for i in range(0,len(lines)):
		if "Resending" in lines[i]:
			r += 1
		if "elapsed" in lines[i]:
			m += 1
			eof_line = lines[i]
		if "Result" in lines[i]:
			total += 1
		if "Result=0" in lines[i]:
			success += 1
		if "'Result': 0" in lines[i]:
			s+=1
		if "EOF reached" in lines[i]:
			eof_line = lines[i]
		else:
			continue
	
	try:
		num_words =  int(str.split(lines[1])[3])
	except:
		num_words = 1
#	print "-------------------------------------------------------"
#	print "Filename: " + sys.argv[1]
#	print "Total number of words in transfer: " + str(num_words)
#	print "Messages sent (excluding resend): " + str(m)
#	print "Number of resends: " + str(r) + "/" + str(r + m) + " = " + str(float(r)/(r+m))
#	print "Message reports efficiency of transfer: " + str(success) + "/" + str(total) + " = " + str(float(success)/total)
#	print "Average OPM (success only/total): " + str(float(success)/(r+m)) + "/" + str(float(total)/(r+m))
	
	if "EOF reached" in eof_line:
		runtime = float(str.split(eof_line)[4])
	else:
		runtime = float(1)
		
#		print "Total runtime: " + str(runtime) + " sec"
#		print "Average time per message: " + str(runtime/(r+m)) + " sec = " + str(1/(runtime/(r+m))) + " messages/sec"
#		print "Time used for resends (based on avg): " + str((runtime/(r+m))*(r)) + " sec"
#		print "Average time per operation: " + str(runtime/total) + " sec"
#		print "Average OPS: " + str((float(success)/(r+m))*(1/(runtime/(r+m)))) + "/" + str((float(total)/(r+m))*4)
#		print "Transfer goodput: " + str((num_words*2)/runtime) + " bytes/sec"
#		print "Transfer throughput: " + str((num_words*2)/runtime + (m*2*2)/runtime) + " bytes/sec"
#	print "-------------------------------------------------------"
	try:
		payload = int(sys.argv[1][3:len(sys.argv[1])-6])
		messages_sent = m
		messages_resent = r
		resend_ratio = float(r)/(r+m)
		success_reports = success
		total_reports = total
		efficiency = float(success)/(total)
		success_opm = float(success)/(r+m)
		total_opm = float(total)/(r+m)
		
		time_per_message = runtime/(r+m)
		messages_per_second = 1/time_per_message
		time_per_op = runtime/total
		success_ops = success_opm*messages_per_second
		total_ops = total_opm*messages_per_second
		goodput = (num_words*2)/runtime
		throughput = goodput + (m*2*2)/runtime
		
		if (runtime == float(1)):
			goodput = 0
			throughput = 0
		
		print "%d, %d, %d, %f, %d, %d, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f" % ( payload, messages_sent, messages_resent, resend_ratio, success_reports, total_reports, efficiency, 
		success_opm, total_opm, runtime, time_per_message, messages_per_second, time_per_op, success_ops, total_ops, goodput, throughput)
	except:
		finger = len(sys.argv[1].split('_')) - 2
		payload = int(sys.argv[1].split('_')[finger])
		success_reports = s
		total_reports = total
		efficiency = float(s)/total
		throughput = (float(s)*payload*2)/10
		ops = float(s)/10
		
		print "%d, %d, %d, %f, %f, %f" % (payload, total_reports, success_reports, efficiency, throughput, ops)
	
