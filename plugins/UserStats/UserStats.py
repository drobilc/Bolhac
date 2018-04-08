from ..plugin import Plugin

class UserStats(Plugin):
	
	def __init__(self, database, options={}):
		self.database = database
		self.options = options

	def renderView(self, data):
		return self.renderCard()

	def getNumberOfUsers(self):
		cursor = self.database.cursor()
		cursor.execute("SELECT COUNT(id) as count FROM user")
		result = cursor.fetchone()
		numberOfUsers = 0
		if result:
			numberOfUsers = result["count"]
		return numberOfUsers

	def getNumberOfSearchers(self):
		cursor = self.database.cursor()
		cursor.execute("SELECT COUNT(id) as count FROM search")
		result = cursor.fetchone()
		numberOfSearchers = 0
		if result:
			numberOfSearchers = result["count"]
		return numberOfSearchers

	def renderCard(self):
		template = self.getTemplate("templates/card.html")
		return template.render(numberOfUsers=self.getNumberOfUsers(), numberOfSearchers=self.getNumberOfSearchers())

	def returnJsonData(self, request):
		data = {
			"numberOfUsers": self.getNumberOfUsers(),
			"numberOfSearchers": self.getNumberOfSearchers()
		}
		return data