#

import jsonrpc
import logging
import threading
import traceback
from datetime import datetime
from binascii import b2a_hex
from binascii import unhexlify
from time import sleep
from util import *

class Rootstock(threading.Thread):
	def __init__(self, *a, **k):
		super().__init__(*a, **k)
		self.daemon = True
		self.logger = logging.getLogger('Rootstock')
		self.blockhash = None
		self.minerfees = None
		self.notify = None
		self.target = None
		self.parenthash = None
		self.lastparenthash = None

	def _prepare(self):
		self.RootstockSources = list(getattr(self, 'RootstockSources', ()))
		self.RootstockPollPeriod = getattr(self, 'RootstockPollPeriod', 0)
		self.RootstockNotifyPolicy = getattr(self, 'RootstockNotifyPolicy', 0)
		if not self.RootstockPollPeriod:
			self.RootstockPollPeriod = self.MM.IdleSleepTime
		LeveledRS = {}
		for i in range(len(self.RootstockSources)):
			RS = self.RootstockSources[i]
			if 'uri' not in RS:
				continue
			if 'name' not in RS:
				RS['name'] = 'RootstockSources[{0}]'.format(i)
			RS.setdefault('priority', 0)
			RS.setdefault('weight', 1)
			LeveledRS.setdefault(RS['priority'], []).append(RS)
		LeveledRS = tuple(x[1] for x in sorted(LeveledRS.items()))
		self.RootstockSources = LeveledRS

	def start(self, *a, **k):
		self._prepare()
		super().start(*a, **k)

	def run(self):
		while True:
			try:
				self.updateRootstock()
			except:
				self.logger.critical(traceback.format_exc())
	
	def updateRootstock(self, triggeredByBlockSubmission = False):
		work = self._callGetWork()
		if work is False:
			work = self._retryCallGetWork(work)
		if work is not None:
			self._processGetWorkResponse(work)
		rskPollPeriod = 0 if triggeredByBlockSubmission else self.RootstockPollPeriod
		sleep(rskPollPeriod)

	def _processGetWorkResponse(self, work):
		try:
			notify = work['notify']
			blockhash = unhexlify(work['blockHashForMergedMining'][2:])
			minerfees = float(work['feesPaidToMiner'])
			target = int(work['target'], 16)
			parenthash = unhexlify(work['parentBlockHash'][2:])
			self._updateBlockHash(blockhash, notify, minerfees, target, parenthash)
		except:
			self.logger.critical(traceback.format_exc())

	def _retryCallGetWork(self, work):
		retryTime = self.RootstockPollPeriod / 3
		getWorkTimeout = 11
		accumRetryTime = 0
		while True:
			sleep(retryTime)
			accumRetryTime += retryTime
			work = self._callGetWork()
			if work is not False:
				break
			if accumRetryTime > getWorkTimeout and self.blockhash is not None:
				self.blockhash = None
		return work

	def _callGetWork(self):
		for RSPriList in self.RootstockSources:
			for i in range(len(RSPriList)):
				RS = RSPriList.pop(0)
				RSPriList.append(RS)
				try:
					r = self._callGetWorkFrom(RS)
					if r is None:
						continue
					return r
				except:
					self.logger.info("RSK {0} is not active".format(RS['name']))
					if RSPriList == self.RootstockSources[-1] and i == len(RSPriList) - 1:
						return False
					else:
						self.logger.error(traceback.format_exc())
		return None

	def _callGetWorkFrom(self, RS):
		access = jsonrpc.ServiceProxy(RS['uri'], timeout = 5)
		return access.mnr_getWork()

	def _updateBlockHash(self, blockhash, notify, minerfees, target, parenthash):
		if self.blockhash != blockhash:
			self.blockhash, self.notify, self.minerfees, self.target, self.parenthash = blockhash, notify, minerfees, target, parenthash
			self.logger.info('New block hash {0} {1:X}'.format(b2a_hex(self.blockhash).decode('utf8'), target))
			if (self._triggerRSKupdate(notify)):
				self.lastparenthash = self.parenthash
				self.logger.info('Update miners work')
				cleanJobs = self.RootstockNotifyPolicy == 3 or self.RootstockNotifyPolicy == 4
				self.MM.updateRSKBlockHashOnCoinbaseTxn(blockhash)
				self.onBlockChange(triggeredByRskGetWork=True, cleanJobs=cleanJobs)

	def _triggerRSKupdate(self, notify):
		notifyFlagUpdate = (self.RootstockNotifyPolicy == 1 or self.RootstockNotifyPolicy == 3) and notify
		differentBlockHashUpdate = (self.RootstockNotifyPolicy == 2 or self.RootstockNotifyPolicy == 4) and self.parenthash != self.lastparenthash

		return notifyFlagUpdate or differentBlockHashUpdate;

	def getBlockInfo(self):
		blockhash, target = self.blockhash, self.target
		if blockhash is None:
			return None, None
		return blockhash, target

	def getRSKTag(self):
		return b'\x52\x53\x4B\x42\x4C\x4F\x43\x4B\x3A'

def rootstockSubmissionThread(payload, blkhash, share):
	servers = list(a for b in rootstockSubmissionThread.rootstock.RootstockSources for a in b)

	payload = b2a_hex(payload).decode('ascii')
	tries = 0
	start_time = None
	finish_time = None
	while len(servers):
		tries += 1
		RS = servers.pop(0)
		#Don't reuse the same conection object that getWork since submitBitcoinBlock can take some time to complete
		#UpstreamRskdJSONRPC = RS['access']
		UpstreamRskdJSONRPC = jsonrpc.ServiceProxy(RS['uri'])
		try:
			start_time = datetime.now()
			UpstreamRskdJSONRPC.mnr_submitBitcoinBlock(payload)
			finish_time = datetime.now()
			rootstock.updateRootstock(True)
		except BaseException as gbterr:
			gbterr_fmt = traceback.format_exc()
			if tries > len(servers):
				msg = 'Upstream \'{0}\' block submission failed: {1}'.format(RS['name'], gbterr_fmt)
				rootstockSubmissionThread.logger.error(msg)
				return
			servers.append(RS)
			continue
	if finish_time is not None:
		rootstockSubmissionThread.logger.info("ROOTSTOCK: submitBitcoinBlock: {}, {}, {}, {}".format(start_time, finish_time, share['jobid'], b2a_hex(share['nonce']).decode('ascii')))
	else:
		rootstockSubmissionThread.logger.info("submitBitcoinBlock failed: {}".format(tries))


rootstockSubmissionThread.logger = logging.getLogger('rootstockSubmission')

rootstock = Rootstock()
rootstockSubmissionThread.rootstock = rootstock
