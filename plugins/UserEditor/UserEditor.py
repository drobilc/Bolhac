from ..plugin import Plugin

class UserEditor(Plugin):
	
	def __init__(self, database, options={}):
		self.database = database
		self.options = options

	def deleteUser(self, userId):
		cursor = self.database.cursor()
		cursor.execute("DELETE FROM user WHERE id = %s", [userId])
		self.database.commit()
		cursor.close()

	def makeAdmin(self, userId):
		cursor = self.database.cursor()
		cursor.execute("UPDATE user SET status = 2 WHERE id = %s", [userId])
		self.database.commit()
		cursor.close()

	def getAllUsers(self):
		cursor = self.database.cursor()
		cursor.execute("SELECT id, email, status FROM user")
		result = list(cursor.fetchall())
		cursor.close()
		return result

	def renderView(self, data):
		if "delete_user" in data:
			userId = int(data["delete_user"])
			self.deleteUser(userId)

		elif "admin_user" in data:
			userId = int(data["admin_user"])
			self.makeAdmin(userId)

		template = self.getTemplate("templates/view.html")
		return template.render(rows=self.getAllUsers())

	def renderCard(self):
		return self.getTemplate("templates/card.html").render()