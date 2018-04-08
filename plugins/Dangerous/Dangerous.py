from ..plugin import Plugin

class Dangerous(Plugin):
	
	def __init__(self, database, options={}):
		self.database = database
		self.options = options

	def removeAllUsers(self):
		cursor = self.database.cursor()
		cursor.execute("DELETE FROM has_search")
		cursor.execute("DELETE FROM user")
		self.database.commit()
		cursor.close()

	def removeAllSearchers(self):
		cursor = self.database.cursor()
		cursor.execute("DELETE FROM has_search")
		cursor.execute("DELETE FROM search")
		self.database.commit()
		cursor.close()

	def removeAllData(self):
		cursor = self.database.cursor()
		cursor.execute("DELETE FROM has_search")
		cursor.execute("DELETE FROM user")
		cursor.execute("DELETE FROM search")
		self.database.commit()
		cursor.close()

	def renderView(self, data):
		html = ""
		value = ""

		if "sql_query" in data:
			query = data["sql_query"].strip()

			cursor = self.database.cursor()
			cursor.execute(query)
			result = list(cursor.fetchall())
			cursor.close()

			return self.getTemplate("templates/view_sql_query.html").render(rows=result, value=query)

		elif "remove_all_users" in data:
			self.removeAllUsers()

		elif "remove_all_searchers" in data:
			self.removeAllSearchers()

		elif "remove_all_data" in data:
			self.removeAllData()

		return self.getTemplate("templates/view.html").render()

	def renderCard(self):
		return self.getTemplate("templates/card.html").render()