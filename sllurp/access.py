from __future__ import print_function
import argparse
import logging
import pprint
import time
import os
from twisted.internet import reactor, defer

import sllurp.llrp as llrp

tagReport = 0
logger = logging.getLogger('sllurp')
fac = None
args = None

# Stuff needed for changing access_specs.
current_line = None
write_data   = None
write_state  = None
pckt_num     = ["00", "01", "02", "03", "04"]
hexindex     = 0


# Line index of hexfile.
index = 0

# Start and end indices of block in current line.
strindex  = [9,25]

# The Intel hexfile.
hexfile   = None

# List with all the lines in the hexfile.
lines     = None

# Transmission stats.
total_bytes_to_send = 0
bytes_sent    = 0

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

# Convert a single character to hex.
def char_to_hex (c):
	return chr(int(c,16))


# Stop the twisted reactor at the end of the program.
def finish (_):
	logger.info('total # of tags seen: {}'.format(tagReport))
	
	if reactor.running:
		reactor.stop()

# The first access command.
def access (proto):
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
		global write_state
		global start_time
		
		write_data = "b1050000000000000000"
		write_state= 0
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
	global tagReport
	global strindex
	global current_line
	global lines
	global index
	global write_data
	global write_state
	global pckt_num
	global hexindex
		
	# Proceed to next AccessSpec iff read EPC matches with data sent with BlockWrite.
	if ((index < len(lines)) and (seen_tags[0]['EPC-96'][0:20] == write_data.lower())):
		logger.info("Match!")
		
		accessSpecStopParam = {
			'AccessSpecStopTriggerType': 1,
			'OperationCountValue': 15,
		}
		
		# Start of a new line.
		if (write_state == 0):
			
			# Update current line.
			current_line = lines[index]
			
			# Check if EOF reached.
			if (len(current_line) == 12):
				logger.info("EOF reached.")
				write_state = -1
				# Construct the AccessSpec.
				try:
					writeSpecParam = {
						'OpSpecID': 0,
						'MB': 3,
						'WordPtr': 0,
						'AccessPassword': 0,
						'WriteDataWordCount': int(1),
						'WriteData': '\xb0\x07',
					}
					
					# Change write_data for comparison against EPC.
					write_data = "b0070000000000000000"
					
					# Call factory to do the next access.
					fac.nextAccess(readParam=None, writeParam=writeSpecParam, stopParam=accessSpecStopParam)
				except:
					logger.info("Error when trying to send boot command.")
			
			# Check what the length of the data is before doing anything.
			data_length = len(current_line) - 12
			logger.info(data_length)
			
			
			# If data length = 4, it's an ISR vector entry so we finish the whole line with 1 BlockWrite.
			if (data_length == 4):
				write_data = "DE" + current_line[1:7] + current_line[9:13]
				logger.info("Next block: " + str(write_data))
				
				# Construct the AccessSpec.
				try:
					writeSpecParam = {
						'OpSpecID': 0,
						'MB': 3,
						'WordPtr': 0,
						'AccessPassword': 0,
						'WriteDataWordCount': int(3),
						'WriteData': write_data.decode("hex"),
					}
					
					# Change write_data for comparison against EPC.
					write_data = write_data + "00000000"
					
					# Proceed to next line.
					index = index + 1
					
					# Call factory to do the next access.
					fac.nextAccess(readParam=None, writeParam=writeSpecParam, stopParam=accessSpecStopParam)
				except:
					logger.info("Error when trying to construct next AccessSpec on new line.")
				
			
			if (data_length % 16 == 0):
				logger.info("Mod16 success")
				
				# Reset hexindex and strindex for new set of data packets.
				hexindex = 0
				strindex  = [9,25]
				
				# write_data = [fd:size:address] (2 words)
				write_data = "DD" + current_line[1:7]
				logger.info("Next block: " + str(write_data))
				
				# Construct the AccessSpec.
				try:
					writeSpecParam = {
						'OpSpecID': 0,
						'MB': 3,
						'WordPtr': 0,
						'AccessPassword': 0,
						'WriteDataWordCount': int(2),
						'WriteData': write_data.decode("hex"),
					}
					
					# Change write_data for comparison against EPC.
					write_data = write_data + "000000000000"
					
					# Proceed to next state.
					write_state = 1
					
					# Call factory to do the next access.
					fac.nextAccess(readParam=None, writeParam=writeSpecParam, stopParam=accessSpecStopParam)
				except:
					logger.info("Error when trying to construct next AccessSpec on new line.")
		
		# Data packets.
		elif (write_state == 1):
			# write_data = [pckt_id:pckt_num:data] (5 words)
			write_data = "DA" + pckt_num[hexindex] + current_line[strindex[0]:strindex[1]]
			strindex = [min(x + 16, len(current_line)) for x in strindex]
			logger.info("Next block: " + str(write_data))
			
			# Construct the AccessSpec.
			try:
				writeSpecParam = {
					'OpSpecID': 0,
					'MB': 3,
					'WordPtr': 0,
					'AccessPassword': 0,
					'WriteDataWordCount': int(5),
					'WriteData': write_data.decode("hex"),
				}
				
				hexindex = hexindex + 1
				
				# Done with data, so put state machine back to new line.
				if (strindex[1] == len(current_line)):
					write_state = 0
					index = index + 1
				
				# Call factory to do the next access.
				fac.nextAccess(readParam=None, writeParam=writeSpecParam, stopParam=accessSpecStopParam)
			except:
				logger.info("Error when trying to construct next AccessSpec on data packets.")
		

def tagReportCallback (llrpMsg):
	"""Function to run each time the reader reports seeing tags."""
	
	global tagReport
	
	tags = llrpMsg.msgdict['RO_ACCESS_REPORT']['TagReportData']
	if len(tags):
		#logger.info('saw tag(s): {}'.format(pprint.pformat(tags)))
		
		# Print EPC-96.
		logger.info("Read EPC: " + str(tags[0]['EPC-96'][0:20]))
		
		try:
			logger.info(str(tags[0]['OpSpecResult']['NumWordsWritten']) + ", " + str(tags[0]['OpSpecResult']['Result']))
		except:
			logger.info("")
		
		# Call protocol.
		if not(hexfile == None):
			doFirmwareFlashing(tags)
		
	else:
		logger.info('no tags seen')
		return
	for tag in tags:
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
	
	args = parser.parse_args()


def init_logging ():
	logLevel = (args.debug and logging.DEBUG or logging.INFO)
	logFormat = '%(asctime)s %(name)s: %(levelname)s: %(message)s'
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
		global total_bytes_to_send
	
		hexfile   = open(args.filename, 'r')
		lines     = hexfile.readlines()
		
		for i in range(0,len(lines)-1):
			total_bytes_to_send = total_bytes_to_send + ((len(lines[i]) - 2)/2)
		
		logger.info('Bytes to send: ' + str(total_bytes_to_send))
	
	# will be called when all connections have terminated normally
	onFinish = defer.Deferred()
	onFinish.addCallback(finish)
	
	global fac
	fac = llrp.LLRPClientFactory(onFinish=onFinish,
	        disconnect_when_done=True,
	        modulation=args.modulation,
	        tari=args.tari,
	        session=args.session,
	        tag_population=args.population,
	        start_inventory=True,
	        tx_power=args.tx_power,
	        report_every_n_tags=args.every_n,
	        #report_every_n_tags=600,
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
