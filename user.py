import time
from flask.ext.login import AnonymousUserMixin

class User(AnonymousUserMixin):

	def __init__(self, id, email, emailer):
		self.id = id
		self.status = 1
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

	def is_admin(self):
		return self.status == 2

	def addAds(self, newAds):
		self.unsentAds.extend(newAds)
		
		timeDelta = time.time() - self.lastAdded
		if timeDelta > 20 * 60:
			self.sendData()
			self.lastAdded = time.time()

	def sendData(self):
		self.emailer.sendEmail(self.email, "Novi oglasi", "templates/email_template.html", {"ads": self.unsentAds})
		self.unsentAds = []

class Anonymous(AnonymousUserMixin):
	
	def __init__(self):
		self.username = 'Guest'

	def is_admin(self):
		return False