#######################################################################
#                                                                     #
#  ___       __   ___  ________  _______   ________   _________       #
# |\  \     |\  \|\  \|\   ____\|\  ___ \ |\   ___  \|\___   ___\     #
# \ \  \    \ \  \ \  \ \  \___|\ \   __/|\ \  \\ \  \|___ \  \_|     #
#  \ \  \  __\ \  \ \  \ \_____  \ \  \_|/_\ \  \\ \  \   \ \  \      #
#   \ \  \|\__\_\  \ \  \|____|\  \ \  \_|\ \ \  \\ \  \   \ \  \     #
#    \ \____________\ \__\____\_\  \ \_______\ \__\\ \__\   \ \__\    #
#     \|____________|\|__|\_________\|_______|\|__| \|__|    \|__|    #
#                        \|_________|                                 #
#                                                                     #
#          Wisent - a robust downstream protocol for CRFIDs           #
#######################################################################

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
CRC_SEED                       = 0xFFFF # CRC16 CCITT seed. Must be the same as the CRFID side.
OCV                            = 15     # Number of operations per command in operation frame.
TIMEOUT_VALUE                  = 20     # Number of NACKs before timeout.              (N_threshold)
MAX_RESEND_VALUE               = 3      # Maximum number of resends.                   (R_max)
MAX_PAYLOAD                    = 16     # Maximum message payload size after throttle. (S_r)
MIN_PAYLOAD                      = 1      # Minimum message payload size after throttle.
THROTTLE_DOWN                  = 1      # Temporary throttle down mechanic. (S_p+1 = S_p/T_down)
THROTTLE_UP                    = 0      # Temporaty throttle up mechanic.   (S_p+1 = S_p + T_up)
CONSECUTIVE_MESSAGES_THRESHOLD = 5      # Consecutive successful messages before throttle up. (M_threshold)

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
timeout                    = 0
remaining_length           = 0
consecutive_messages_count = 0
message_payload            = 16     # Maximum message payload size in words.       (S_p)

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
	global write_state, current_line, index
	global write_data, check_data
	global words_sent
	global timeout
	global resend_count
	global remaining_length
	global message_payload
	global consecutive_messages_count
	
	# Normal scenario: check if the tag we want to talk to is in the list.
	for tag in seen_tags:
		if (write_state == -1):
			write_state = -2
			fac.politeShutdown()
		try:
			if (tag['EPC-96'][0:4] == "1337" and write_state >= 0):
				# ACK
				if (seen_tags[0]['EPC-96'][4:14] == check_data.lower()):
					timeout      = 0
					resend_count = 0
					current_time = time.time()
					progress_string = "(" + str(words_sent) + "/" + str(total_words_to_send) + ") --- Time elapsed: %.3f secs" % (current_time - start_time)
					
					consecutive_messages_count += 1
					
					if (consecutive_messages_count >= CONSECUTIVE_MESSAGES_THRESHOLD and message_payload < 16):
						consecutive_messages_count = 0
						message_payload = min(MAX_PAYLOAD, message_payload+THROTTLE_UP)
					
					# Start of a new line.
					if (write_state == 0):
						current_line = lines[index]
						
						# Check for EOF.
						if (index == len(lines)-1):
							logger.info(progress_string + " EOF reached.")
							write_state = -1
							
							try:
								infinite_spec = {'AccessSpecStopTriggerType': 0, 'OperationCountValue': 1,}
								message       = toLLRPMessage(1, crc_update)
								fac.nextAccess(readParam=None, writeParam=message, stopParam=infinite_spec)
							except:
								logger.info("Error when trying to send boot command.")
							return
						
						# Reset remaining length on new line.
						if (remaining_length == 0):
							remaining_length = len(current_line) - 12
						
						if ((remaining_length % 4) == 0):
							num_words = remaining_length / 4
							
							# Remaining data can be send in one go, so proceed to next line after this message.
							if (num_words <= message_payload):
								wisent_message    = constructWisentMessage(num_words)
								message           = toLLRPMessage(3+num_words, wisent_message[0])
								words_sent       += num_words
								remaining_length -= num_words*4
								index += 1
							# Remaining data capped by message payload, so stay on this line.
							else:
								wisent_message    = constructWisentMessage(message_payload)
								message           = toLLRPMessage(3+message_payload, wisent_message[0])
								words_sent       += message_payload
								remaining_length -= message_payload * 4
							
							write_data     = wisent_message[0]
							check_data     = wisent_message[1]
							logger.info("Next block: " + check_data  + progress_string)
								
							# Send the message to the reader.
							try:
								fac.nextAccess(readParam=None, writeParam=message, stopParam=global_stop_param)
							except:
								logger.info("Error when trying to construct next AccessSpec on new line.")
								
						else:
							logger.info("Line " + str(index) + " of hex file has odd number of Bytes, which is not supported atm!")
				# NACK
				else:
					# Generate timeout
					if (timeout < TIMEOUT_VALUE):
						timeout += 1
					
					# Resend
					elif (timeout == TIMEOUT_VALUE and resend_count < MAX_RESEND_VALUE):
						resend_count += 1
						logger.info("Timeout reached. Resending... " + str(resend_count))
						consecutive_messages_count = 0
						timeout = 0
						
						# Throttle speed.
						if (message_payload > MIN_PAYLOAD):
							# Undo progress.
							words_sent -=  ((len(current_line) - 12) - (remaining_length))/4
						
							if (remaining_length == 0):
								index -= 1
						
							remaining_length = len(current_line) - 12
							message_payload = max(MIN_PAYLOAD, message_payload / THROTTLE_DOWN)
							
						# Can't be throttled further, just resend the current message.
						else:
							try:
								message = toLLRPMessage(4, write_data)
								fac.nextAccess(readParam=None, writeParam=message, stopParam=global_stop_param)
								return
							except:
								logger.info("Error when trying to construct next AccessSpec on new line.")
							
						num_words = remaining_length / 4
						
						# Remaining data can be send in one go.
						if (num_words <= message_payload):
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
									message = toLLRPMessage(3+num_words, write_data)
									
									# Pad write_data with zeroes for comparison against EPC.
									check_data = header + size + address + checksum[0:2]
									words_sent += num_words
									remaining_length -= num_words*4
									
									# Proceed to next line.
									index += 1
									
									fac.nextAccess(readParam=None, writeParam=message, stopParam=global_stop_param)
								except:
									logger.info("Error when trying to construct next AccessSpec on new line.")
									
						# Remaining data capped by message_payload.
						else:
							header  = "{:02x}".format(2+message_payload)
							size    = "{:02x}".format(message_payload*2)
							offset  = ((len(current_line)-12)-remaining_length)/4
							address = "{:04x}".format(int("0x"+current_line[3:7],0) + 2*offset)
							write_data = header + size + address
							
							# Data
							for x in range(0, message_payload):
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
								message = toLLRPMessage(3+message_payload, write_data)
								
								# Pad write_data with zeroes for comparison against EPC.
								check_data = header + size + address + checksum[0:2]
								words_sent += message_payload
								remaining_length -= message_payload*4
								
								fac.nextAccess(readParam=None, writeParam=message, stopParam=global_stop_param)
							except:
								logger.info("Error when trying to construct next AccessSpec on new line.")
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
			
			global timeout
			global resend_count
			global write_data
			global words_sent
			global remaining_length
			global current_line
			global message_payload
			global consecutive_messages_count
			global index
			
			# Quit.
			if (resend_count == MAX_RESEND_VALUE):
				logger.info("Maximum resends reached... aborting.")
				write_state = -1
			
			# Handle timeout.
			if (timeout < TIMEOUT_VALUE):
				timeout += 1
			elif (timeout == TIMEOUT_VALUE and resend_count < MAX_RESEND_VALUE):
				resend_count += 1
				logger.info("Timeout reached. Resending... " + str(resend_count))
				timeout = 0
				consecutive_messages_count = 0
						
				# Throttle speed.
				if (message_payload > MIN_PAYLOAD):
					# Undo progress.
					words_sent -=  ((len(current_line) - 12) - (remaining_length))/4
				
					if (remaining_length == 0):
						index -= 1
				
					remaining_length = len(current_line) - 12
					message_payload = max(MIN_PAYLOAD, message_payload / THROTTLE_DOWN)
					
				# Can't be throttled further, just resend the current message.
				else:
					try:
						message = toLLRPMessage(4, write_data)
						fac.nextAccess(readParam=None, writeParam=message, stopParam=global_stop_param)
						return
					except:
						logger.info("Error when trying to construct next AccessSpec on new line.")
							
				num_words = remaining_length / 4
				
				# Remaining data can be send in one go.
				if (num_words <= message_payload):
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
						message          = toLLRPMessage(3+num_words, write_data)
						check_data       = header + size + address + checksum[0:2]
						words_sent       += num_words
						remaining_length -= num_words*4
						
						# Proceed to next line.
						index            += 1
						
						fac.nextAccess(readParam=None, writeParam=message, stopParam=global_stop_param)
					except:
						logger.info("Error when trying to construct next AccessSpec on new line.")
						
				# Remaining data capped by message_payload.
				else:
					header  = "{:02x}".format(2+message_payload)
					size    = "{:02x}".format(message_payload*2)
					offset  = ((len(current_line)-12)-remaining_length)/4
					address = "{:04x}".format(int("0x"+current_line[3:7],0) + 2*offset)
					write_data = header + size + address
					
					# Data
					for x in range(0, message_payload):
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
						message = toLLRPMessage(3+message_payload, write_data)
						
						# Pad write_data with zeroes for comparison against EPC.
						check_data       = header + size + address + checksum[0:2]
						words_sent       += message_payload
						remaining_length -= message_payload*4
						
						fac.nextAccess(readParam=None, writeParam=message, stopParam=global_stop_param)
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
	
	parser.add_argument('-f', '--filename', type=str, help='the Intel Hex file to transfer', dest='filename')
	parser.add_argument('-m', '--maxwordcount', default=16, type=int, help='start size of message payload in words', dest='message_payload')
	
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
		global hexfile
		global lines
		global total_words_to_send
		global words_sent
		global message_payload
		global crc_update
		
		message_payload = args.message_payload
		hexfile         = open(args.filename, 'r')
		lines           = hexfile.readlines()
		crc_update      = CRC_SEED
		words_sent      = 0
		
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
		
		# Add timeout to reader connect attempt.
		for host in args.host:
			reactor.connectTCP(host, args.port, fac, timeout=3)
		
		# Catch Ctrl-C and to politely shut down system.
		reactor.addSystemEventTrigger('before', 'shutdown', politeShutdown, fac)
		
		# Start the sllurp reactor.
		reactor.run()
		
	else:
		logger.info("File not specified.")

if __name__ == '__main__':
	main()

