import time

class User(object):

	def __init__(self, id, email, emailer):
		self.id = id
		self.email = email
		self.emailer = emailer
		self.lastAdded = time.time()
		self.unsentAds = []

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return u'{}'.format(self.id)

	def addAds(self, newAds):
		self.unsentAds.extend(newAds)
		
		timeDelta = time.time() - self.lastAdded
		if timeDelta > 20 * 60:
			self.sendData()
			self.lastAdded = time.time()

	def sendData(self):
		self.emailer.sendEmail(self.email, "Novi oglasi", "templates/email_template.html", {"ads": self.unsentAds})
		self.unsentAds = []