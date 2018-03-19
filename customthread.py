from threading import Thread, Event
from emailer import Emailer
import time
import json

with open("config.json", "r") as configFile:
	jsonData = json.load(configFile)
	emailServer = jsonData["email_server"]
	emailPort = jsonData["email_port"]
	emailUsername = jsonData["email_username"]
	emailPassword = jsonData["email_password"]

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
						#self.emailer.sendEmail("", "Novi oglasi", "templates/email_template.html", {"ads": newAds})
						pass
					searcher.lastChecked = time.time()
			else:
				# Prenesemo podatke in shranimo cas
				newAds = searcher.getNewAds()
				if len(newAds) > 0:
					#self.emailer.sendEmail("drobilc@gmail.com", "Novi oglasi", "templates/email_template.html", {"ads": newAds})
					pass
				searcher.lastChecked = time.time()