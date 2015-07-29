#####################################################################################################
#                                                                                                   #
#  ___       __   ___  ________  _______   ________   _________                                     #
# |\  \     |\  \|\  \|\   ____\|\  ___ \ |\   ___  \|\___   ___\                                   #
# \ \  \    \ \  \ \  \ \  \___|\ \   __/|\ \  \\ \  \|___ \  \_|                                   #
#  \ \  \  __\ \  \ \  \ \_____  \ \  \_|/_\ \  \\ \  \   \ \  \                                    #
#   \ \  \|\__\_\  \ \  \|____|\  \ \  \_|\ \ \  \\ \  \   \ \  \                                   #
#    \ \____________\ \__\____\_\  \ \_______\ \__\\ \__\   \ \__\                                  #
#     \|____________|\|__|\_________\|_______|\|__| \|__|    \|__|                                  #
#                        \|_________|                                                               #
#                                                                                                   #
#          Wisent - a robust downstream protocol for CRFIDs                                         #
#####################################################################################################
#                                                                                                   #
# ## Wisent has been tested and reportedly working on the following readers:                        #
#    - Impinj Speedway R420 (FCC)                                                                   #
#    - Impinj Speedway R1000                                                                        #
#                                                                                                   #
# ## Example usage:                                                                                 #
#   bin/wisent -f <Intel Hex file> <reader IP address>                                              #
#                                                                                                   #
#  # Some extra options can be specied e.g. for setting the starting throttle index:                #
#   bin/wisent -m <throttle index> -f <Intel Hex file> <reader IP address>                          #
#                                                                                                   #
#####################################################################################################

from __future__ import print_function
import argparse
import logging
import pprint
import time
import os
import sys
from twisted.internet import reactor, defer

import sllurp.llrp as llrp

######################################################################################################

## Wisent system constants.
CRC_SEED                       = 0xFFFF            # CRC16 CCITT seed. Same as on CRFID side.
OCV                            = 15                # Number of operations/command in operation frame.
TIMEOUT_VALUE                  = 20                # Number of NACKs before timeout.  (N_threshold)
MAX_RESEND_VALUE               = 3                 # Maximum number of resends. (R_max)
CONSECUTIVE_MESSAGES_THRESHOLD = 10                # Messages before throttle up. (M_threshold)
T                              = [1,2,3,4,6,8,16]  # Set of allowed values for S_p after throttle.
THROTTLE_DOWN_LOS              = 3                 # Decrease throttle index by this on LOS.
THROTTLE_DOWN                  = 2                 # Decrease throttle index by this on wrong EPC
THROTTLE_UP                    = 1                 # Increase throttle index by this on threshold.

######################################################################################################

# Sllurp global variables.
fac                 = None
args                = None
tagReport           = 0
logger              = logging.getLogger('sllurp')
global_stop_param   =  {'AccessSpecStopTriggerType': 1, 'OperationCountValue': int(OCV),}

# The Intel Hex file.
hexfile             = None
lines               = None
current_line        = None
index               = 0

# CRC16 CCITT over the data in the Intel Hex file.
crc_update          = None

# Wisent Global variables needed to change/construct messages.
write_data                 = None
check_data                 = None
write_state                = None
resend_count               = 0
nack_counter               = 0
remaining_length           = 0
consecutive_messages_count = 0
throttle_index             = 0
message_payload            = T[throttle_index]     # Maximum message payload size in words.     (S_p)

# Wisent transfer statistics.
start_time          = None
current_time        = None
total_words_to_send = 0
words_sent          = 0

######################################################################################################

# Stop the twisted reactor at the end of the program.
def finish (_):
	logger.info('Total number of tags seen: {}'.format(tagReport))
	
	if reactor.running:
		reactor.stop()


def toLLRPMessage(word_count, content):
	llrp_message = {
		'OpSpecID': 0,
		'MB': 3,
		'WordPtr': 0,
		'AccessPassword': 0,
		'WriteDataWordCount': int(word_count),
		'WriteData': content.decode('hex'),
	}
	return llrp_message


def constructWisentMessage(payload_size):
	checksum        = 0
	word_count      = "{:02x}".format(2 + payload_size)
	payload_length  = "{:02x}".format(2 * payload_size)
	offset          = ((len(current_line)-12)-remaining_length)/4
	address         = "{:04x}".format(int("0x" + current_line[3:7], 0) + 2 * offset)
	wisent_message  = word_count + payload_length + address
	
	# Data
	for x in range(0, payload_size):
		wisent_message += current_line[9+4*(x+offset):9+4*(x+offset+1)]
	
	for i in range(0, len(wisent_message)/2):
		checksum += int("0x"+ wisent_message[2*i:2*i+2], 0)
	checksum = checksum % 256
	checksum = "{:02x}".format(checksum)
	
	message_verification = word_count + payload_length + address + checksum
	wisent_message += checksum + "00"
	return [wisent_message, message_verification]


def sendWisentMessage(n, p = ""):
	global fac, words_sent, remaining_length, index, write_data, check_data
	
	# Decide whether whole line can be sent with 1 message or has to be split.
	index             = (index + 1) if (n <= message_payload) else index
	n                 = n if (n <= message_payload) else message_payload
	
	wisent_message    = constructWisentMessage(n)
	message           = toLLRPMessage(3+n, wisent_message[0])
	words_sent       += n
	remaining_length -= n*4
	
	write_data        = wisent_message[0]
	check_data        = wisent_message[1]
	
	if (len(p) > 0):
		logger.info("Next block: " + check_data + p)
	else:
		logger.info("Resent: " + check_data)
	
	# Send the message to the reader.
	try:
		fac.nextAccess(readParam=None, writeParam=message, stopParam=global_stop_param)
	except:
		logger.info("Error when trying to construct next AccessSpec on new line.")


# Start Wisent transfer session with a Write command.
def startWisentTransfer (proto):
	global write_state, check_data, start_time
	
	write_state = 0
	check_data  = "b105000000"
	message     = toLLRPMessage(1, "b105")
	start_time  = time.time()
	
	return proto.startAccess(readWords=None, writeWords=message, accessStopParam=global_stop_param)


def politeShutdown (factory):
	return factory.politeShutdown()


def wisentTransfer (seen_tags):
	global write_state, current_line, index, remaining_length, words_sent
	global resend_count, nack_counter, consecutive_messages_count, message_payload, throttle_index
	
	# Normal scenario: check if the tag we want to talk to is in the list.
	for tag in seen_tags:
		if (write_state == -1):
			write_state = -2
			
			# Uncomment this line to shutdown immediately after transfer.
			fac.politeShutdown()
		try:
			if (tag['EPC-96'][0:4] == "1337" and write_state >= 0):
				# ACK
				if (seen_tags[0]['EPC-96'][4:14] == check_data.lower()):
					nack_counter = 0
					resend_count = 0
					current_time = time.time()
					progress_string = "(" + str(words_sent) + "/" + str(total_words_to_send) + ") --- Time elapsed: %.3f secs" % (current_time - start_time)
					
					consecutive_messages_count += 1
					
					# Throttle up.
					if (consecutive_messages_count >= CONSECUTIVE_MESSAGES_THRESHOLD):
						consecutive_messages_count = 0
						throttle_index = min(len(T)-1, throttle_index + THROTTLE_UP)
						message_payload = T[throttle_index]
					
					# Start of a new line.
					if (write_state == 0):
						current_line = lines[index]
						
						# Check for EOF.
						if (index == len(lines)-1):
							logger.info(progress_string + " EOF reached.")
							write_state = -1
							
							try:
								infinite_spec = {'AccessSpecStopTriggerType': 0, 'OperationCountValue': 1,}
								#message       = toLLRPMessage(1, crc_update)
								message       = toLLRPMessage(1, "b007")
								fac.nextAccess(readParam=None, writeParam=message, stopParam=infinite_spec)
							except:
								logger.info("Error when trying to send boot command.")
							return
						
						# Reset remaining length on new line.
						if (remaining_length == 0):
							remaining_length = len(current_line) - 12
						
						# Proceed only if current line has whole number of words of data.
						if ((remaining_length % 4) == 0):
							num_words = remaining_length / 4
							sendWisentMessage(num_words, progress_string)
						else:
							logger.info("Line " + str(index) + " of hex file has odd number of bytes, which is not supported.")
				# NACK
				else:
					# NACK and resend mechanism.
					if (nack_counter < TIMEOUT_VALUE):
						nack_counter += 1
					elif (nack_counter == TIMEOUT_VALUE and resend_count < MAX_RESEND_VALUE):
						resend_count              += 1
						nack_counter               = 0
						consecutive_messages_count = 0
						
						logger.info("Timeout reached. Resending (bad EPC)... " + str(resend_count))
						
						# Undo progress.
						index       = (index -1) if (remaining_length == 0) else index
						sent_data   =  write_data[8:len(write_data)-4]
						words_sent -=  len(sent_data)/4
						logger.info("Undone words: " + str(len(sent_data)/4))
						remaining_length += len(sent_data)
						num_words         = remaining_length / 4
						
						# Throttle down.
						throttle_index    = max(0,throttle_index - THROTTLE_DOWN)
						message_payload   = T[throttle_index]
						sendWisentMessage(num_words)
					else:
						logger.info("Maximum resends reached... aborting.")
						write_state = -1
		except:
			continue


def tagReportCallback (llrpMsg):
	global tagReport, write_state
	
	tags = llrpMsg.msgdict['RO_ACCESS_REPORT']['TagReportData']
	
	# The reader has seen tags!
	if len(tags):
		try:
			logger.info("Read EPC: " + str(tags[0]['EPC-96'][0:14]) + ", " +  str(tags[0]['OpSpecResult']['NumWordsWritten']) + " , Result=" + str(tags[0]['OpSpecResult']['Result']))
		except:
			logger.debug("")
		
		wisentTransfer(tags)
	
	# No tags were seen.
	else:
		if (write_state >= 0):
			logger.info('no tags seen')
			global current_line, index, remaining_length, words_sent
			global resend_count, nack_counter, consecutive_messages_count, message_payload, throttle_index
			
			# Quit.
			if (resend_count == MAX_RESEND_VALUE):
				logger.info("Maximum resends reached... aborting.")
				write_state = -1
			
			# NACK and resend mechanism.
			if (nack_counter < TIMEOUT_VALUE):
				nack_counter += 1
			elif (nack_counter == TIMEOUT_VALUE and resend_count < MAX_RESEND_VALUE):
				resend_count              += 1
				nack_counter               = 0
				consecutive_messages_count = 0
				
				logger.info("Timeout reached. Resending (line-of-sight)... " + str(resend_count))
				
				# Undo progress.
				index       = (index -1) if (remaining_length == 0) else index
				sent_data   =  write_data[8:len(write_data)-4]
				words_sent -=  len(sent_data)/4
				logger.info("Undone words: " + str(len(sent_data)/4))
				remaining_length += len(sent_data)
				num_words         = remaining_length / 4
				
				# Throttle down.
				throttle_index    = max(0,throttle_index - THROTTLE_DOWN_LOS)
				message_payload   = T[throttle_index]
				sendWisentMessage(num_words)
			else:
				logger.info("Maximum resends reached... aborting.")
				write_state = -1
		return
	for tag in tags:
		if (write_state >= 0):
			tagReport += tag['TagSeenCount'][0]


def parse_args ():
	global args
	parser = argparse.ArgumentParser(description='Wisent data transfer application for CRFID')
	parser.add_argument('host', help='IP address of RFID reader', nargs='*')
	parser.add_argument('-p', '--port', default=llrp.LLRP_PORT, type=int, help='port to connect to (default {})'.format(llrp.LLRP_PORT))
	parser.add_argument('-t', '--time', default=10, type=float, help='number of seconds for which to inventory (default 10)')
	parser.add_argument('-d', '--debug', action='store_true', help='show debugging output')
	parser.add_argument('-n', '--report-every-n-tags', default=200, type=int, dest='every_n', metavar='N', help='issue a TagReport every N tags')
	parser.add_argument('-X', '--tx-power', default=0, type=int, dest='tx_power', help='Transmit power (default 0=max power)')
	parser.add_argument('-M', '--modulation', default='WISP5', help='modulation (default WISP5)')
	parser.add_argument('-T', '--tari', default=0, type=int, help='Tari value (default 0=auto)')
	parser.add_argument('-s', '--session', default=2, type=int, help='Gen2 session (default 2)')
	parser.add_argument('-P', '--tag-population', default=32, type=int, dest='population', help="Tag Population value (default 32)")
	parser.add_argument('-l', '--logfile')
	
	parser.add_argument('-f', '--filename', type=str, help='the Intel Hex file to transfer', dest='filename', required=True)
	parser.add_argument('-m', '--throttleindex', default=6, type=int, help='start size of message payload in words according to set T', dest='throttle_index')
	
	args = parser.parse_args()


def init_logging ():
	logLevel  = (args.debug and logging.DEBUG or logging.INFO)
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


# CRC16-CCITT, poly = 0x1021
# Input: int, hex character.
def crc16_ccitt(crc, data):
	data = int("0x"+data, 0)
	x = (crc >> 8) ^ data
	x ^= x >> 4
	crc = (crc << 8) ^ (x << 12) ^ (x << 5) ^ (x)
	return crc & 0xffff


def main ():
	parse_args()
	init_logging()
	
	if (args.filename):
		global fac
		global hexfile, lines, crc_update
		global message_payload, throttle_index
		global total_words_to_send
		
		hexfile         = open(args.filename, 'r')
		lines           = hexfile.readlines()
		crc_update      = CRC_SEED
		
		throttle_index  = args.throttle_index
		message_payload = T[throttle_index]
		
		# Calculate CRC16 of the data and amount of words/bytes to send.
		for i in range(0,len(lines)-1):
			total_words_to_send = total_words_to_send + ((len(lines[i]) - 12)/4)
			
			s = lines[i][9:len(lines[i])-3]
			for j in range (0, len(s)/2):
				crc_update = crc16_ccitt(crc_update, s[2*j:2*j+2])
		
		crc_update = "{:04x}".format(crc_update)
		
		logger.info('Bytes to send: ' + str(total_words_to_send*2))
		logger.info('CRC16 of data: ' + crc_update)
		
		# Called when all connections have terminated normally.
		onFinish = defer.Deferred()
		onFinish.addCallback(finish)
		
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
		
		# The 'main loop' for tags.
		fac.addTagReportCallback(tagReportCallback)
		
		# Start Wisent transfer session.
		fac.addStateCallback(llrp.LLRPClient.STATE_INVENTORYING, startWisentTransfer)
		
		# Add nack_counter to reader connect attempt.
		for host in args.host:
			reactor.connectTCP(host, args.port, fac, timeout=3)
		
		# Catch Ctrl-C and to politely shut down system.
		reactor.addSystemEventTrigger('before', 'shutdown', politeShutdown, fac)
		
		# Start the sllurp reactor.
		reactor.run()

if __name__ == '__main__':
	main()

