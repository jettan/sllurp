from __future__ import print_function
import argparse
import logging
import pprint
import time
import os
import sys
from twisted.internet import reactor, defer

import sllurp.llrp as llrp

# General sllurp stuff.
tagReport = 0
logger = logging.getLogger('sllurp')
fac = None
args = None

#################### SYSTEM PARAMETERS ###############################################################

# Number of NACKs before resend.
TIMEOUT_VALUE = 20

# Maximum number of resends.
MAX_RESEND_VALUE = 3

# Number of times a single ACCESSSPEC is performed by the reader before the reader disables it.
OPERATION_COUNT_VALUE = 15

# The maximum amount of DATA WORDS included in a single BlockWrite command.
MAX_WORD_COUNT = 16

# Max word count will be DIVIDED by this number when shit happens.
THROTTLE_DOWN = 2

# Max word count will be INCREMENTED by this number when all is well.
THROTTLE_UP = 2

# Throttle speed up after this number of succeeded lines.
THROTTLE_UP_AFTER_N_SUCCESS = 2

######################################################################################################

# Stuff needed for changing access_specs.
current_line     = None
write_data       = None
check_data       = None
write_state      = None
resend_count     = 0
timeout          = 0
remaining_length = 0
success_count    = 0

# Line index of hexfile.
index = 0

# The Intel hexfile.
hexfile   = None

# List with all the lines in the hexfile.
lines     = None

# Transmission stats.
total_words_to_send = 0
words_sent          = 0

# Time related vars.
start_time = None
current_time = None


# Parse hex argument.
class hexact(argparse.Action):
	'An argparse.Action that handles hex string input'
	def __call__(self,parser, namespace, values, option_string=None):
		base = 10
		if '0x' in values: base = 16
		setattr(namespace, self.dest, int(values,base))
		return
	pass

# Stop the twisted reactor at the end of the program.
def finish (_):
	logger.info('total # of tags seen: {}'.format(tagReport))
	
	if reactor.running:
		reactor.stop()

# The first access command.
def access (proto):
	global write_state
	write_state = -1
	readSpecParam = None
	if args.read_words:
		readSpecParam = {
			'OpSpecID': 0,
			'MB': 3,
			'WordPtr': 0,
			'AccessPassword': 0,
			'WordCount': args.read_words
		}
	
	writeSpecParam = None
	if args.write_words:
		writeSpecParam = {
			'OpSpecID': 0,
			'MB': 3,
			'WordPtr': 0,
			'AccessPassword': 0,
			'WriteDataWordCount': args.write_words,
			'WriteData': chr(args.write_content >> 8) + chr(args.write_content & 0xff),
		}
	
	# If command to write a firmware is issued (0xb105), make AccessSpec finite.
	if (args.write_content == 45317):
		global write_data
		global check_data
		global start_time
		
		check_data = "b105000000"
		write_state = 0
		start_time = time.time()
		
		accessSpecStopParam = {
			'AccessSpecStopTriggerType': 1,
			'OperationCountValue': 10,
		}
	
	# Otherwise, use default behavior and keep AccessSpec alive.
	else:
		accessSpecStopParam = {
			'AccessSpecStopTriggerType': 0,
			'OperationCountValue': 1,
		}
	
	return proto.startAccess(readWords=readSpecParam, writeWords=writeSpecParam, accessStopParam=accessSpecStopParam)


def politeShutdown (factory):
	return factory.politeShutdown()


def doFirmwareFlashing (seen_tags):
	global current_line
	global index
	global check_data
	global write_data
	global write_state
	global words_sent
	global total_words_to_send
	global timeout
	global resend_count
	global remaining_length
	global MAX_WORD_COUNT
	global success_count
	
	
	# Timeout/Resend mechanism.
	if (write_state >= 0):
		if (timeout < TIMEOUT_VALUE):
			timeout += 1
		elif (timeout == TIMEOUT_VALUE and resend_count < MAX_RESEND_VALUE):
			logger.info("Timeout reached. Resending...")
			resend_count += 1
			success_count = 0
			timeout = 0
			
			# Undo progress.
			words_sent -=  (len(write_data)/4) - 3
			
			if (remaining_length == 0):
				index -= 1
			
			remaining_length = len(current_line) - 12
			
			# Throttle speed.
			MAX_WORD_COUNT = max(1, MAX_WORD_COUNT / THROTTLE_DOWN)
			num_words = remaining_length / 4
			
			accessSpecStopParam = {
				'AccessSpecStopTriggerType': 1,
				'OperationCountValue': int(OPERATION_COUNT_VALUE),
			}
			
			# Remaining data can be send in one go.
			if (num_words <= MAX_WORD_COUNT):
				header  = "{:02x}".format(2+num_words)
				size    = "{:02x}".format(num_words*2)
				offset  = ((len(current_line)-12)-remaining_length)/4
				address = "{:04x}".format(int("0x"+current_line[3:7],0) + 2*offset)
				write_data = header + size + address
				
				# Data
				for x in range(0, num_words):
					write_data += current_line[9+4*(x+offset):9+4*(x+offset+1)]
				
				# Checksum
				checksum = 0
				for i in range(0, len(write_data)/2):
					checksum += int("0x"+ write_data[2*i:2*i+2], 0)
				checksum = checksum % 256
				checksum = "{:02x}".format(checksum)
				checksum += "00"
				
				write_data += checksum
				
				# Construct the AccessSpec.
				try:
					writeSpecParam = {
						'OpSpecID': 0,
						'MB': 3,
						'WordPtr': 0,
						'AccessPassword': 0,
						'WriteDataWordCount': int(3+num_words),
						'WriteData': write_data.decode("hex"),
					}
					
					# Pad write_data with zeroes for comparison against EPC.
					check_data = header + size + address + checksum[0:2]
					words_sent += num_words
					remaining_length -= num_words*4
					
					# Proceed to next line.
					index += 1
					
					# Call factory to do the next access.
					fac.nextAccess(readParam=None, writeParam=writeSpecParam, stopParam=accessSpecStopParam)
				except:
					logger.info("Error when trying to construct next AccessSpec on new line.")
					
			# Remaining data capped by MAX_WORD_COUNT.
			else:
				header  = "{:02x}".format(2+MAX_WORD_COUNT)
				size    = "{:02x}".format(MAX_WORD_COUNT*2)
				offset  = ((len(current_line)-12)-remaining_length)/4
				address = "{:04x}".format(int("0x"+current_line[3:7],0) + 2*offset)
				write_data = header + size + address
				
				# Data
				for x in range(0, MAX_WORD_COUNT):
					write_data += current_line[9+4*(x+offset):9+4*(x+offset+1)]
				
				# Checksum
				checksum = 0
				for i in range(0, len(write_data)/2):
					checksum += int("0x"+ write_data[2*i:2*i+2], 0)
				checksum = checksum % 256
				checksum = "{:02x}".format(checksum)
				checksum += "00"
				
				write_data += checksum
				
				# Construct the AccessSpec.
				try:
					writeSpecParam = {
						'OpSpecID': 0,
						'MB': 3,
						'WordPtr': 0,
						'AccessPassword': 0,
						'WriteDataWordCount': int(3+MAX_WORD_COUNT),
						'WriteData': write_data.decode("hex"),
					}
					
					# Pad write_data with zeroes for comparison against EPC.
					check_data = header + size + address + checksum[0:2]
					words_sent += MAX_WORD_COUNT
					remaining_length -= MAX_WORD_COUNT*4
					
					# Call factory to do the next access.
					fac.nextAccess(readParam=None, writeParam=writeSpecParam, stopParam=accessSpecStopParam)
				except:
					logger.info("Error when trying to construct next AccessSpec on new line.")
		else:
			logger.info("Maximum resends reached... aborting.")
			write_state = -1
	
	# Normal scenario: check if the tag we want to talk to is in the list.
	for tag in seen_tags:
		try:
			if (tag['EPC-96'][0:4] == "1337"):
				
				# Proceed to next AccessSpec iff read EPC matches with data sent with BlockWrite.
				if (write_state >= 0 and (seen_tags[0]['EPC-96'][4:14] == check_data.lower())):
					timeout      = 0
					resend_count = 0
					current_time = time.time()
					progress_string = "(" + str(words_sent) + "/" + str(total_words_to_send) + ") --- Time elapsed: %.3f secs" % (current_time - start_time)
					
					accessSpecStopParam = {
						'AccessSpecStopTriggerType': 1,
						'OperationCountValue': int(OPERATION_COUNT_VALUE),
					}
					
					success_count += 1
					
					if (success_count >= THROTTLE_UP_AFTER_N_SUCCESS):
						logger.info("Throttling speed up!")
						success_count = 0
						MAX_WORD_COUNT = min(16, MAX_WORD_COUNT+2)
					
					# Start of a new line.
					if (write_state == 0):
						# Update current line.
						current_line = lines[index]
						
						# Check if EOF reached.
						if (index == len(lines)-1):
							#logger.info(progress_string + " EOF reached. Booting into new firmware...")
							logger.info(progress_string + " EOF reached.")
							write_state = -1
							
							#politeShutdown(fac)
							# Construct the AccessSpec.
							
							try:
								accessSpecStopParam = {
									'AccessSpecStopTriggerType': 0,
									'OperationCountValue': 1,
								}
								writeSpecParam = {
									'OpSpecID': 0,
									'MB': 3,
									'WordPtr': 0,
									'AccessPassword': 0,
									'WriteDataWordCount': int(1),
									'WriteData': '\xb0\x07',
								}
								
								# Call factory to do the next access.
								fac.nextAccess(readParam=None, writeParam=writeSpecParam, stopParam=accessSpecStopParam)
							except:
								logger.info("Error when trying to send boot command.")
							
							return
						
						# Reset remaining length on new line.
						if (remaining_length == 0):
							remaining_length = len(current_line) - 12
						
						if ((remaining_length % 4) == 0):
							num_words = remaining_length / 4
							
							# Remaining data can be send in one go.
							if (num_words <= MAX_WORD_COUNT):
								header  = "{:02x}".format(2+num_words)
								size    = "{:02x}".format(num_words*2)
								offset  = ((len(current_line)-12)-remaining_length)/4
								address = "{:04x}".format(int("0x"+current_line[3:7],0) + 2*offset)
								write_data = header + size + address
								
								# Data
								for x in range(0, num_words):
									write_data += current_line[9+4*(x+offset):9+4*(x+offset+1)]
								
								# Checksum
								checksum = 0
								for i in range(0, len(write_data)/2):
									checksum += int("0x"+ write_data[2*i:2*i+2], 0)
								checksum = checksum % 256
								checksum = "{:02x}".format(checksum)
								checksum += "00"
								
								write_data += checksum
								logger.info("Next block: " + str(header + size + address + checksum[0:2])  + progress_string)
								
								# Construct the AccessSpec.
								try:
									writeSpecParam = {
										'OpSpecID': 0,
										'MB': 3,
										'WordPtr': 0,
										'AccessPassword': 0,
										'WriteDataWordCount': int(3+num_words),
										'WriteData': write_data.decode("hex"),
									}
									
									# Pad write_data with zeroes for comparison against EPC.
									check_data = header + size + address + checksum[0:2]
									words_sent += num_words
									remaining_length -= num_words*4
									
									# Proceed to next line.
									index += 1
									
									# Call factory to do the next access.
									fac.nextAccess(readParam=None, writeParam=writeSpecParam, stopParam=accessSpecStopParam)
								except:
									logger.info("Error when trying to construct next AccessSpec on new line.")
									
							# Remaining data capped by MAX_WORD_COUNT.
							else:
								header  = "{:02x}".format(2+MAX_WORD_COUNT)
								size    = "{:02x}".format(MAX_WORD_COUNT*2)
								offset  = ((len(current_line)-12)-remaining_length)/4
								address = "{:04x}".format(int("0x"+current_line[3:7],0) + 2*offset)
								write_data = header + size + address
								
								# Data
								for x in range(0, MAX_WORD_COUNT):
									write_data += current_line[9+4*(x+offset):9+4*(x+offset+1)]
								
								# Checksum
								checksum = 0
								for i in range(0, len(write_data)/2):
									checksum += int("0x"+ write_data[2*i:2*i+2], 0)
								checksum = checksum % 256
								checksum = "{:02x}".format(checksum)
								checksum += "00"
								
								write_data += checksum
								logger.info("Next block: " + str(header + size + address + checksum[0:2])  + progress_string)
								
								# Construct the AccessSpec.
								try:
									writeSpecParam = {
										'OpSpecID': 0,
										'MB': 3,
										'WordPtr': 0,
										'AccessPassword': 0,
										'WriteDataWordCount': int(3+MAX_WORD_COUNT),
										'WriteData': write_data.decode("hex"),
									}
									
									# Pad write_data with zeroes for comparison against EPC.
									check_data = header + size + address + checksum[0:2]
									words_sent += MAX_WORD_COUNT
									remaining_length -= MAX_WORD_COUNT*4
									
									# Call factory to do the next access.
									fac.nextAccess(readParam=None, writeParam=writeSpecParam, stopParam=accessSpecStopParam)
								except:
									logger.info("Error when trying to construct next AccessSpec on new line.")
								
						else:
							logger.info("Line " + str(index) + " of hex file has odd number of Bytes!")
		except:
			continue

def tagReportCallback (llrpMsg):
	"""Function to run each time the reader reports seeing tags."""
	
	global tagReport
	global write_state
	
	tags = llrpMsg.msgdict['RO_ACCESS_REPORT']['TagReportData']
	if len(tags):
		#logger.info('saw tag(s): {}'.format(pprint.pformat(tags)))
		
		# Print EPC-96.
		#logger.info("Read EPC: " + str(tags[0]['EPC-96'][0:15]))
		
		try:
			logger.debug(str(tags[0]['OpSpecResult']['NumWordsWritten']) + ", " + str(tags[0]['OpSpecResult']['Result']))
		except:
			logger.debug("")
		
		# Call protocol.
		if not(hexfile == None):
			doFirmwareFlashing(tags)
		
	else:
		if (write_state >= 0):
			logger.info('no tags seen')
			
			global timeout
			global resend_count
			global write_data
			global words_sent
			global remaining_length
			global current_line
			global MAX_WORD_COUNT
			global success_count
			global index
			
			# Handle timeout.
			if (timeout < TIMEOUT_VALUE):
				timeout += 1
			elif (timeout == TIMEOUT_VALUE and resend_count < MAX_RESEND_VALUE):
				logger.info("Timeout reached. Resending...")
				resend_count += 1
				timeout = 0
				success_count = 0
				
				# Undo progress.
				words_sent -=  (len(write_data)/4) - 3
				
				if (remaining_length == 0):
					index -= 1
				remaining_length = len(current_line) - 12
				
				# Throttle speed.
				MAX_WORD_COUNT = max(1, MAX_WORD_COUNT / THROTTLE_DOWN)
				num_words = remaining_length / 4
				
				accessSpecStopParam = {
					'AccessSpecStopTriggerType': 1,
					'OperationCountValue': int(OPERATION_COUNT_VALUE),
				}
				
				# Remaining data can be send in one go.
				if (num_words <= MAX_WORD_COUNT):
					header  = "{:02x}".format(2+num_words)
					size    = "{:02x}".format(num_words*2)
					offset  = ((len(current_line)-12)-remaining_length)/4
					address = "{:04x}".format(int("0x"+current_line[3:7],0) + 2*offset)
					write_data = header + size + address
					
					# Data
					for x in range(0, num_words):
						write_data += current_line[9+4*(x+offset):9+4*(x+offset+1)]
					
					# Checksum
					checksum = 0
					for i in range(0, len(write_data)/2):
						checksum += int("0x"+ write_data[2*i:2*i+2], 0)
					checksum = checksum % 256
					checksum = "{:02x}".format(checksum)
					checksum += "00"
					
					write_data += checksum
					
					# Construct the AccessSpec.
					try:
						writeSpecParam = {
							'OpSpecID': 0,
							'MB': 3,
							'WordPtr': 0,
							'AccessPassword': 0,
							'WriteDataWordCount': int(3+num_words),
							'WriteData': write_data.decode("hex"),
						}
						
						# Pad write_data with zeroes for comparison against EPC.
						check_data = header + size + address + checksum[0:2]
						words_sent += num_words
						remaining_length -= num_words*4
						
						# Proceed to next line.
						index += 1
						
						# Call factory to do the next access.
						fac.nextAccess(readParam=None, writeParam=writeSpecParam, stopParam=accessSpecStopParam)
					except:
						logger.info("Error when trying to construct next AccessSpec on new line.")
						
				# Remaining data capped by MAX_WORD_COUNT.
				else:
					header  = "{:02x}".format(2+MAX_WORD_COUNT)
					size    = "{:02x}".format(MAX_WORD_COUNT*2)
					offset  = ((len(current_line)-12)-remaining_length)/4
					address = "{:04x}".format(int("0x"+current_line[3:7],0) + 2*offset)
					write_data = header + size + address
					
					# Data
					for x in range(0, MAX_WORD_COUNT):
						write_data += current_line[9+4*(x+offset):9+4*(x+offset+1)]
					
					# Checksum
					checksum = 0
					for i in range(0, len(write_data)/2):
						checksum += int("0x"+ write_data[2*i:2*i+2], 0)
					checksum = checksum % 256
					checksum = "{:02x}".format(checksum)
					checksum += "00"
					
					write_data += checksum
					
					# Construct the AccessSpec.
					try:
						writeSpecParam = {
							'OpSpecID': 0,
							'MB': 3,
							'WordPtr': 0,
							'AccessPassword': 0,
							'WriteDataWordCount': int(3+MAX_WORD_COUNT),
							'WriteData': write_data.decode("hex"),
						}
						
						# Pad write_data with zeroes for comparison against EPC.
						check_data = header + size + address + checksum[0:2]
						words_sent += MAX_WORD_COUNT
						remaining_length -= MAX_WORD_COUNT*4
						
						# Call factory to do the next access.
						fac.nextAccess(readParam=None, writeParam=writeSpecParam, stopParam=accessSpecStopParam)
					except:
						logger.info("Error when trying to construct next AccessSpec on new line.")
			else:
				logger.info("Maximum resends reached... aborting.")
				write_state = -1
		return
	for tag in tags:
		if (write_state >= 0):
			tagReport += tag['TagSeenCount'][0]


def parse_args ():
	global args
	parser = argparse.ArgumentParser(description='Simple RFID Reader Inventory')
	parser.add_argument('host', help='hostname or IP address of RFID reader',
	        nargs='*')
	parser.add_argument('-p', '--port', default=llrp.LLRP_PORT, type=int,
	        help='port to connect to (default {})'.format(llrp.LLRP_PORT))
	parser.add_argument('-t', '--time', default=10, type=float,
	        help='number of seconds for which to inventory (default 10)')
	parser.add_argument('-d', '--debug', action='store_true',
	        help='show debugging output')
	parser.add_argument('-n', '--report-every-n-tags', default=1, type=int,
	        dest='every_n', metavar='N', help='issue a TagReport every N tags')
	parser.add_argument('-X', '--tx-power', default=0, type=int,
	        dest='tx_power', help='Transmit power (default 0=max power)')
	parser.add_argument('-M', '--modulation', default='M8',
	        help='modulation (default M8)')
	parser.add_argument('-T', '--tari', default=0, type=int,
	        help='Tari value (default 0=auto)')
	parser.add_argument('-s', '--session', default=2, type=int,
	        help='Gen2 session (default 2)')
	parser.add_argument('-P', '--tag-population', default=4, type=int,
	        dest='population', help="Tag Population value (default 4)")
	
	# read or write
	op = parser.add_mutually_exclusive_group(required=True)
	op.add_argument('-r', '--read-words', type=int,
	        help='Number of words to read from MB 0 WordPtr 0')
	op.add_argument('-w', '--write-words', type=int,
	        help='Number of words to write to MB 0 WordPtr 0')
	parser.add_argument('-l', '--logfile')
	# specify content to write
	parser.add_argument('-c', '--write_content', action=hexact,
	        help='Content to write when using -w, example: 0xaabb, 0x1234')
	parser.add_argument('-f', '--filename', type=str,
	        help='The intel hexfile to flash when using -w', dest='filename')
	parser.add_argument('-m', '--maxwordcount', default=16, type=int, help='maximum number of data words to send using BlockWrite', dest='MAX_WORD_COUNT')
	
	args = parser.parse_args()


def init_logging ():
	logLevel = (args.debug and logging.DEBUG or logging.INFO)
	#logFormat = '%(asctime)s %(name)s: %(levelname)s: %(message)s'
	logFormat = '%(message)s'
	formatter = logging.Formatter(logFormat)
	stderr = logging.StreamHandler()
	stderr.setFormatter(formatter)
	
	root = logging.getLogger()
	root.setLevel(logLevel)
	root.handlers = [stderr,]
	
	if args.logfile:
		fHandler = logging.FileHandler(args.logfile)
		fHandler.setFormatter(formatter)
		root.addHandler(fHandler)
	
	logger.log(logLevel, 'log level: {}'.format(logging.getLevelName(logLevel)))

def main ():
	parse_args()
	init_logging()
	
	if (args.filename):
		global hexfile
		global lines
		global total_words_to_send
		global words_sent
		global MAX_WORD_COUNT
		
		hexfile    = open(args.filename, 'r')
		lines      = hexfile.readlines()
		MAX_WORD_COUNT = args.MAX_WORD_COUNT
		
		words_sent = 0
		
		for i in range(0,len(lines)-1):
			total_words_to_send = total_words_to_send + ((len(lines[i]) - 12)/4)
		
		logger.info('Words to send: ' + str(total_words_to_send))
	
	# will be called when all connections have terminated normally
	onFinish = defer.Deferred()
	onFinish.addCallback(finish)
	
	global fac
	fac = llrp.LLRPClientFactory(onFinish=onFinish,
	        disconnect_when_done=True,
	        modulation=args.modulation,
	        tari=args.tari,
	        session=args.session,
	        tag_population=int(32),
	        start_inventory=True,
	        tx_power=args.tx_power,
	        report_every_n_tags=args.every_n,
	        tag_content_selector={
	            'EnableROSpecID': False,
	            'EnableSpecIndex': False,
	            'EnableInventoryParameterSpecID': False,
	            'EnableAntennaID': True,
	            'EnableChannelIndex': False,
	            'EnablePeakRRSI': True,
	            'EnableFirstSeenTimestamp': False,
	            'EnableLastSeenTimestamp': True,
	            'EnableTagSeenCount': True,
	            'EnableAccessSpecID': True
	        })
	
	# tagReportCallback will be called every time the reader sends a TagReport  message (i.e., when it has "seen" tags).
	fac.addTagReportCallback(tagReportCallback)
	
	# start tag access once inventorying
	fac.addStateCallback(llrp.LLRPClient.STATE_INVENTORYING, access)
	
	for host in args.host:
		reactor.connectTCP(host, args.port, fac, timeout=3)
	
	# catch ctrl-C and stop inventory before disconnecting
	reactor.addSystemEventTrigger('before', 'shutdown', politeShutdown, fac)
	
	reactor.run()

if __name__ == '__main__':
	main()
