import MySQLdb, MySQLdb.cursors

class DatabaseHelper(object):

	def __init__(self, mysqlHost, mysqlUsername, mysqlPassword, mysqlDatabase):
		self.mysqlHost = mysqlHost
		self.mysqlUsername = mysqlUsername
		self.mysqlPassword = mysqlPassword
		self.mysqlDatabase = mysqlDatabase
		self.database = None
		self.connect()

	def connect(self):
		self.database = MySQLdb.connect(host=self.mysqlHost, user=self.mysqlUsername, passwd=self.mysqlPassword, db=self.mysqlDatabase, cursorclass=MySQLdb.cursors.DictCursor)
		self.database.autocommit(True)

	def query(self, query, data):
		try:
			cursor = self.database.cursor()
			cursor.execute(query, data)
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			return self.query(query, data)
		return cursor

	def cursor(self):
		try:
			cursor = self.database.cursor()
		except (AttributeError, MySQLdb.OperationalError):
			self.connect()
			return self.cursor()
		return cursor

	def commit(self):
		self.database.commit()