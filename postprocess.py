#!/usr/bin/python

import sys

if (len(sys.argv) < 2):
	print "I'm afraid I can't do that Dave!"
else:
	f     = open(str(sys.argv[1]),'r')
	lines = f.readlines()
	
	indices = []
	diffs   = []
	
	# Get indices
	for i in range(0,len(lines)):
		if "elapsed" in lines[i]:
			indices.append(i)
		else:
			continue
	
	for i in range(1,len(indices)):
		diffs.append(indices[i] - indices[i-1]-1)
	
	s = 0
	for i in range(0,len(diffs)):
		#print diffs[i]
		s += diffs[i]
	
	print str(s) + "/ (OCV * " + str(len(diffs)) + ")"
	print "Average EPC needed before next message: " + str((0.0 + s)/len(diffs))

