#

import jsonrpc
import logging
import threading
import traceback
import base64
from time import sleep

class Rootstock(threading.Thread):
	def __init__(self, *a, **k):
		super().__init__(*a, **k)
		self.daemon = True
		self.logger = logging.getLogger('rootstock')
		self.blockhash = None
		self.minerfees = None
		self.difficulty = None
		self.notify = None

	def _prepare(self):
		self.RootstockSources = list(getattr(self, 'RootstockSources', ()))
		self.RootstockPollPeriod = getattr(self, 'RootstockPollPeriod', 0)
		self.RootstockNotifyPolicy = getattr(self, 'RootstockNotifyPolicy', 0)
		if not self.RootstockPollPeriod:
			self.RootstockPollPeriod = self.MM.IdleSleepTime
		LeveledRS = {}
		URI2Access = {}
		for i in range(len(self.RootstockSources)):
			RS = self.RootstockSources[i]
			if 'uri' not in RS:
				continue
			if 'name' not in RS:
				RS['name'] = 'RootstockSources[{0}]'.format(i)
			RS.setdefault('priority', 0)
			RS.setdefault('weight', 1)
			if RS['uri'] not in URI2Access:
				access = jsonrpc.ServiceProxy(RS['uri'])
				URI2Access[RS['uri']] = access
			RS['access'] = URI2Access[RS['uri']]
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
	
	def updateRootstock(self):
		work = self._callGetWork()
		if work is not None:
			notify = work['notifyFlag']
			blockhash = base64.b64decode(work['blockHashForMergedMining'])
			minerfees = float(work['feesPaidToMiner'])
			difficulty = float(work['difficultyBI'])
			self._updateBlockHash(blockhash, notify, minerfees, difficulty)
		sleep(self.RootstockPollPeriod)

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
					if RSPriList == self.RootstockSources[-1] and i == len(RSPriList) - 1:
						raise
					else:
						self.logger.error(traceback.format_exc())
		return None

	def _callGetWorkFrom(self, RS):
		access = RS['access']
		return access.eth_getWork()

	def _updateBlockHash(self, blockhash, notify, minerfees, difficulty):
		if self.blockhash != blockhash:
			self.blockhash, self.notify, self.minerfees, self.difficulty = blockhash, notify, minerfees, difficulty
			#FIXME notify to generate a new block
