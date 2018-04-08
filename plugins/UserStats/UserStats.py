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
		return """
			<h1 style="margin-bottom: 8px; font-weight: bold;">Stats</h1>
			<table class="table is-fullwidth is-hoverable">
				<tr>
					<td>Number of users</td>
					<td><strong>{}</strong></td>
				</tr>
				<tr>
					<td>Number of searchers</td>
					<td><strong>{}</strong></td>
				</tr>
			</table>
		""".format(self.getNumberOfUsers(), self.getNumberOfSearchers())