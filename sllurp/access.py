from __future__ import print_function
import argparse
import logging
import pprint
import time
from twisted.internet import reactor, defer

import sllurp.llrp as llrp

tagReport = 0
logger = logging.getLogger('sllurp')
fac = None
args = None

# Stuff needed for changing access_specs.
current_line = None
checkCharhi  = None
checkCharlo  = None

flag  = 1
index = 0
miss  = 0

strindex  = [1,3]
hexindex  = ":fdfeffdd000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20"
hexfile   = None
lines     = None

class hexact(argparse.Action):
	'An argparse.Action that handles hex string input'
	def __call__(self,parser, namespace, values, option_string=None):
		base = 10
		if '0x' in values: base = 16
		setattr(namespace, self.dest, int(values,base))
		return
	pass


def char_to_hex (c):
	return chr(int(c,16))


def finish (_):
	logger.info('total # of tags seen: {}'.format(tagReport))
	
	if reactor.running:
		reactor.stop()


def access (proto):
	global checkCharhi
	global checkCharlo
	checkCharhi = ord(chr(args.write_content >> 8))
	checkCharlo = ord(chr(args.write_content & 0xff))
	
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
	
	# If command to go into FRAM write is issued, make accessSpec finite.
	if (args.write_content == 45317):
		accessSpecStopParam = {
			'AccessSpecStopTriggerType': 1,
			'OperationCountValue': 10,
		}
	# Otherwise, jump to application and keep accessSpec alive.
	else:
		accessSpecStopParam = {
			'AccessSpecStopTriggerType': 0,
			'OperationCountValue': 1,
		}
	
	return proto.startAccess(readWords=readSpecParam, writeWords=writeSpecParam, accessStopParam=accessSpecStopParam)



def politeShutdown (factory):
	return factory.politeShutdown()



def tagReportCallback (llrpMsg):
	"""Function to run each time the reader reports seeing tags."""
	
	global tagReport
	global flag
	global checkCharlo
	global checkCharhi
	global lines
	global current_line
	global strindex
	global index
	global miss
	
	tags = llrpMsg.msgdict['RO_ACCESS_REPORT']['TagReportData']
	if len(tags):
		#logger.info('saw tag(s): {}'.format(pprint.pformat(tags)))
		try:
			opspecresultlength = len(tags[0]['OpSpecResult'])
		except:
			miss = miss + 1
		
		
		logger.info(tags[0]['EPC-96'][10:22])
		
		readEPChi = int(tags[0]['EPC-96'][18:20],16)
		readEPClo = int(tags[0]['EPC-96'][20:22],16)
		
		# If read epc substring is the same as the chars we told the reader to write, it's time for the write the next set of chars.
		if (readEPChi == checkCharhi and readEPClo == checkCharlo):
			if (flag == 1):
				miss = 0
				
				if (index < len(lines)):
					current_line = lines[index]
					
					accessSpecStopParam = {
						'AccessSpecStopTriggerType': 1,
						'OperationCountValue': 5,
					}
					
					logger.info('Changing ACCESS_SPEC')
					write_hi = char_to_hex(hexindex[strindex[0]:strindex[1]])
					write_lo = char_to_hex(current_line[strindex[0]:strindex[1]])
					strindex = [x + 2 for x in strindex]
					
					# End of file reached.
					if (index == len(lines) - 1):
						write_hi = char_to_hex("be")
						write_lo = char_to_hex("ef")
						
						accessSpecStopParam = {
							'AccessSpecStopTriggerType': 0,
							'OperationCountValue': 1,
						}
					
					# If end of line has been reached, do special stuff.
					if (strindex[1] > len(current_line)):
						write_hi = char_to_hex("cc")
						strindex = [1,3]
						index = index + 1
					
					
					checkCharhi = ord(write_hi)
					checkCharlo = ord(write_lo)
					writeData = write_hi + write_lo
					
					writeSpecParam = {
						'OpSpecID': 0,
						'MB': 3,
						'WordPtr': 0,
						'AccessPassword': 0,
						'WriteDataWordCount': int(1),
						'WriteData': writeData,
					}
					fac.nextAccess(readParam=None, writeParam=writeSpecParam, stopParam=accessSpecStopParam)
			
			# Change access spec every x reports.
			#flag = (flag + 1) % 2
		
		# Resend if we missed the access spec window.
		if (miss == 3):
			logger.info('Resend!')
			
			accessSpecStopParam = {
				'AccessSpecStopTriggerType': 1,
				'OperationCountValue': 1,
			}
			
			writeSpecParam = {
				'OpSpecID': 0,
				'MB': 3,
				'WordPtr': 0,
				'AccessPassword': 0,
				'WriteDataWordCount': int(1),
				'WriteData': (chr(checkCharhi) + chr(checkCharlo)),
			}
			miss = 0
			fac.nextAccess(readParam=None, writeParam=writeSpecParam, stopParam=accessSpecStopParam)
			
		
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
	
	global hexfile
	global lines
	
	hexfile   = open(args.filename, 'r')
	lines     = hexfile.readlines()
	
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
	
	# tagReportCallback will be called every time the reader sends a TagReport
	# message (i.e., when it has "seen" tags).
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
