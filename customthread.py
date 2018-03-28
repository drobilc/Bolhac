from threading import Thread, Event
import time
import json

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
					print("Searching for {}, interval: {}.".format(searcher.q, searcher.interval))
					# Prenesemo podatke
					newAds = searcher.getNewAds()
					if len(newAds) > 0:
						for user in searcher.users:
							user.addAds(newAds)
					searcher.lastChecked = time.time()
			else:
				# Prenesemo podatke in shranimo cas
				newAds = searcher.getNewAds()
				print("Searching for {}, interval: {}.".format(searcher.q, searcher.interval))
				if len(newAds) > 0:
					for user in searcher.users:
						user.addAds(newAds)
				searcher.lastChecked = time.time()