#

import jsonrpc
import logging
import threading
import traceback
from time import sleep

class Rootstock(threading.Thread):
	def __init__(self, *a, **k):
		super().__init__(*a, **k)
		self.daemon = True
		self.logger = logging.getLogger('rootstock')

	def _prepare(self):
		self.RootstockSources = list(getattr(self, 'RootstockSources', ()))
		self.RootstockPollPeriod = getattr(self, 'RootstockPollPeriod', 0)
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
		for RSPriList in self.RootstockSources:
			for i in range(len(RSPriList)):
				RS = RSPriList.pop(0)
				RSPriList.append(RS)
				try:
					r = self._callGetWork(RS)
					if r is None:
						continue
					self.logger.debug('Updating work \'{0}\''.format(r))
				except:
					if RSPriList == self.RootstockSources[-1] and i == len(RSPriList) - 1:
						raise
					else:
						self.logger.error(traceback.format_exc())
		sleep(self.RootstockPollPeriod)

	def _callGetWork(self, RS):
		access = RS['access']
		return access.eth_getWork()
