from threading import Thread, Event
from emailer import Emailer
import time
import json

with open("config.json", "r") as configFile:
	jsonData = json.load(configFile)
	emailServer = jsonData["email"]["server"]
	emailPort = jsonData["email"]["port"]
	emailUsername = jsonData["email"]["username"]
	emailPassword = jsonData["email"]["password"]

class BolhaSearchThread(Thread):

	def __init__(self, event, waitingTime, searchers):
		Thread.__init__(self)
		self.stopped = event
		self.waitingTime = waitingTime
		self.searchers = searchers

		self.emailer = Emailer(emailServer, emailPort, emailUsername, emailPassword)

	def run(self):
		while not self.stopped.wait(self.waitingTime):
			self.getData()

	def getData(self):
		for searcher in self.searchers:
			if hasattr(searcher, "lastChecked"):
				timeDelta = time.time() - searcher.lastChecked
				if timeDelta > searcher.interval:
					# Prenesemo podatke
					newAds = searcher.getNewAds()
					if len(newAds) > 0:
						for user in searcher.users:
							self.emailer.sendEmail(user.email, "Novi oglasi", "templates/email_template.html", {"ads": newAds})
						pass
					searcher.lastChecked = time.time()
			else:
				# Prenesemo podatke in shranimo cas
				newAds = searcher.getNewAds()
				if len(newAds) > 0:
					for user in searcher.users:
						self.emailer.sendEmail(user.email, "Novi oglasi", "templates/email_template.html", {"ads": newAds})
				searcher.lastChecked = time.time()