from ..plugin import Plugin
from .. models import User

class UserEditor(Plugin):
	
	def __init__(self, database, options={}):
		super().__init__(database, options)
		self.database = database

	def deleteUser(self, userId):
		user = self.database.session.query(User).filter_by(id=userId).first()
		if user:
			self.database.session.delete(user)
			self.database.session.commit()

	def makeAdmin(self, userId):
		user = self.database.session.query(User).filter_by(id=userId).first()
		if user:
			user.account_type = 1
			self.database.session.add(user)
			self.database.session.commit()

	def getAllUsers(self):
		return self.database.session.query(User).all()

	def renderView(self, data):
		if "delete_user" in data:
			userId = int(data["delete_user"])
			self.deleteUser(userId)

		elif "admin_user" in data:
			userId = int(data["admin_user"])
			self.makeAdmin(userId)

		template = self.getTemplate("templates/view.html")
		return template.render(users=self.getAllUsers())

	def renderCard(self):
		return self.getTemplate("templates/card.html").render()