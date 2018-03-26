class User(object):

	def __init__(self, id, email):
		self.id = id
		self.email = email

	@staticmethod
	def get(user_id):
		pass

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return u'{}'.format(self.id)