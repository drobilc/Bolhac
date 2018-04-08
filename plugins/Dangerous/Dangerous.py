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
			result = cursor.fetchall()
			table = '<h2 class="my-heading">Query result</h2><table class="table is-fullwidth is-hoverable">'
			if result:
				table += '<tr><th>{}</th></tr>'.format("</th><th>".join(result[0]))
				for row in result:
					table += '<tr><td>{}</td></tr>'.format("</td><td>".join(map(str, [row[key] for key in row])))
				table += "</table>"
				cursor.close()
			else:
				table += "<tr><td>No results found</td></tr>"
				table += "</table>"
			html += table
			value = query

		elif "remove_all_users" in data:
			self.removeAllUsers()

		elif "remove_all_searchers" in data:
			self.removeAllSearchers()

		elif "remove_all_data" in data:
			self.removeAllData()

		html += """
			<h2 class="my-heading">Executing SQL</h2>
			<form action="" method="POST">
				<textarea name="sql_query" class="textarea" style="font-family: "Courier New", Courier, monospace;" placeholder="Enter your SQL query here">{}</textarea>
				<div class="buttons is-right" style="margin-top: 6px">
					<input type="submit" class="button is-danger" value="Execute">
				</div>
			</form>
		""".format(value)
		return html

	def renderCard(self):
		return """
		<h1 style="margin-bottom: 8px; font-weight: bold;">Dangerous options</h1>
		<p style="margin-bottom: 12px;">Do not use this if you don't know what you are doing.</p>
		<div class="buttons">
			<a href="/admin/plugin/Dangerous?remove_all_users" class="button is-danger is-fullwidth" style="margin-right: 0">Remove all users</a>
			<a href="/admin/plugin/Dangerous?remove_all_searchers" class="button is-danger is-fullwidth" style="margin-right: 0">Remove all searchers</a>
			<a href="/admin/plugin/Dangerous?remove_all_data" class="button is-danger is-fullwidth">Remove all data</a>
		</div>
		"""