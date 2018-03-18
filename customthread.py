from threading import Thread, Event
import time

class BolhaSearchThread(Thread):

	def __init__(self, event, waitingTime, searchers):
		Thread.__init__(self)
		self.stopped = event
		self.waitingTime = waitingTime
		self.searchers = searchers

	def run(self):
		while not self.stopped.wait(self.waitingTime):
			self.getData()

	def getData(self):
		for searcher in self.searchers:
			if hasattr(searcher, "lastChecked"):
				timeDelta = time.time() - searcher.lastChecked
				if timeDelta > searcher.interval:
					# Prenesemo podatke
					print(searcher.search())
					searcher.lastChecked = time.time()
			else:
				# Prenesemo podatke in shranimo cas
				print(searcher.search())
				searcher.lastChecked = time.time()