from flask import Flask, request, render_template, redirect, url_for, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from threading import Thread, Event
from bolha import BolhaSearch
from emailer import Emailer
from customthread import BolhaSearchThread
from user import User, Anonymous
import MySQLdb, MySQLdb.cursors
import json
import hashlib
import glob, os, importlib, inspect
from options import Options

with open("config.json", "r") as configFile:
	jsonData = json.load(configFile)

	# MySQL database configuration
	mysqlHost = jsonData["database"]["host"]
	mysqlUsername = jsonData["database"]["username"]
	mysqlPassword = jsonData["database"]["password"]
	mysqlDatabase = jsonData["database"]["database"]
	loginManagerSecretKey = jsonData["secret_key"]

	# Email server configuration
	emailServer = jsonData["email"]["server"]
	emailPort = jsonData["email"]["port"]
	emailUsername = jsonData["email"]["username"]
	emailPassword = jsonData["email"]["password"]

# Get dashboard and plugin options
print("Reading options from file config.json")
options = Options("config.json")

# Enabled plugins vs Available plugins
availablePlugins = glob.glob("plugins/**/*.py")

# Connect to database
pluginDatabase = MySQLdb.connect(host=mysqlHost, user=mysqlUsername, passwd=mysqlPassword, db=mysqlDatabase, cursorclass=MySQLdb.cursors.DictCursor)

def getPluginName(pluginPath):
	pluginName = os.path.basename(pluginPath)
	if ".py" in pluginName:
		pluginName = pluginName.replace(".py", "")
	return pluginName

def getMainClass(plugin):
	allClasses = inspect.getmembers(plugin, inspect.isclass)
	if len(allClasses) > 0:
		mainClass = None
		for className in allClasses:
			if className[0] != 'Plugin':
				mainClass = className[1]
				break;
		return mainClass

def importPlugin(pluginPath):
	# Get plugin name and print debug info
	pluginName = getPluginName(pluginPath)
	print(" - Importing plugin {}".format(pluginName))

	# Import plugin from path
	importedPlugin = importlib.import_module("plugins.{}.{}".format(pluginName, pluginName))

	# Get main class from plugin
	mainClass = getMainClass(importedPlugin)
	if mainClass:
		# Get plugin options from options
		pluginOptions = options.pluginOptions(mainClass.__name__)
		# Create object from class
		pluginObject = mainClass(pluginDatabase, pluginOptions)
		# Return object
		return pluginObject

enabledPlugins = {}

# Observer class observes changes and calls hooks
class Observer(object):
	
	def __init__(self, plugins):
		self.plugins = plugins

	def getHook(self, plugin, hookName):
		hook = getattr(plugin, hookName, None)
		if hook and callable(hook):
			return hook
		return None

	def callHook(self, hookName, data=None):
		for plugin in self.plugins:
			hook = self.getHook(self.plugins[plugin], hookName)
			if hook:
				hook(data)

# Import plugins
print("Importing plugins")
for pluginPath in availablePlugins:
	pluginName = getPluginName(pluginPath)
	# Create plugin object
	importedPlugin = importPlugin(pluginPath)
	enabledPlugins[pluginName] = importedPlugin

app = Flask(__name__)
app.secret_key = loginManagerSecretKey
loginManager = LoginManager()
loginManager.init_app(app)
loginManager.anonymous_user = Anonymous

@loginManager.user_loader
def load_user(user_id):
	return getUserData(user_id)

stopFlag = Event()

emailer = Emailer(emailServer, emailPort, emailUsername, emailPassword)

# Tabela v kateri hranimo vse iskalnike
searchers = []

# Slovar v katerem hranimo podatke
userObjects = {}

database = MySQLdb.connect(host=mysqlHost, user=mysqlUsername, passwd=mysqlPassword, db=mysqlDatabase)

def getUserData(user_id):
	cursor = database.cursor()
	cursor.execute("SELECT id, email, status FROM user WHERE id = %s", [int(user_id)])
	result = cursor.fetchone()
	if result:
		if result[0] in userObjects:
			return userObjects[result[0]]
		else:
			user = User(result[0], result[1], emailer)
			user.status = result[2]
			userObjects[result[0]] = user
			return user

def getMd5Hash(text):
	return hashlib.md5(text.encode('utf-8')).hexdigest()

def getUserId(email=None, password=None):
	cursor = database.cursor()
	if email and password:
		cursor.execute("SELECT id FROM user WHERE email = %s AND password = %s", [email, getMd5Hash(password)])
	elif email:
		cursor.execute("SELECT id FROM user WHERE email = %s", [email])
	else:
		return None
	result = cursor.fetchone()
	if result:
		return result[0]
	return None

def addUser(email, password):
	cursor = database.cursor()
	cursor.execute("INSERT INTO user (email, password) VALUES (%s, %s)", [email, getMd5Hash(password)])
	database.commit()

def addSearchToDatabase(search):
	cursor = database.cursor()
	cursor.execute("INSERT INTO search (url) VALUES (%s)", [search.getUrl()])
	database.commit()
	return cursor.lastrowid

def addSearchToUser(user, search):
	cursor = database.cursor()
	cursor.execute("INSERT INTO has_search (user_id, search_id) VALUES (%s, %s)", [user, search])
	database.commit()

def getUserSearchers(user):
	userSearchers = []
	cursor = database.cursor()
	cursor.execute("SELECT search.id, search.url FROM has_search INNER JOIN search ON has_search.search_id = search.id WHERE has_search.user_id = %s;", [user])
	results = cursor.fetchall()
	for result in results:
		searcher = BolhaSearch(url=result[1])
		searcher.id = result[0]
		if searcher in searchers:
			searcher = searchers[searchers.index(searcher)]
		userSearchers.append(searcher)
	return userSearchers

def getUsersToNotify(searcher):
	users = []
	cursor = database.cursor()
	cursor.execute("SELECT has_search.user_id, user.email FROM has_search INNER JOIN user ON has_search.user_id = user.id WHERE has_search.search_id = %s;", [searcher])
	results = cursor.fetchall()
	for result in results:
		if result[0] in userObjects:
			user = userObjects[result[0]]
		else:
			user = User(result[0], result[1], emailer)
			userObjects[result[0]] = user
		users.append(user)
	return users

def getAllSearchers():
	searchers = []
	cursor = database.cursor()
	cursor.execute("SELECT search.id, search.url FROM has_search INNER JOIN search ON has_search.search_id = search.id;")
	results = cursor.fetchall()
	for result in results:
		users = getUsersToNotify(result[0])
		searcher = BolhaSearch(url=result[1])
		searcher.id = result[0]
		searcher.users = users
		searcher.interval = 60
		searchers.append(searcher)
	return searchers

def deleteSearcherFromDatabase(userId, searcher):
	cursor = database.cursor()
	cursor.execute("DELETE FROM has_search WHERE user_id = %s AND search_id = %s;", [userId, searcher])

def deleteSearcherFromCurrentSearchers(searcherId):
	for i, searcher in enumerate(searchers):
		if searcher.id == searcherId:
			del searchers[i]
			return

@app.route("/remove/<int:searcher>", methods=["GET"])
@login_required
def deleteSearcher(searcher):
	if current_user and current_user.is_authenticated:
		userId = current_user.get_id()
		deleteSearcherFromDatabase(userId, searcher)
		# Potrebno ga je se izbrisati iz trenutnih iskalnikov
		deleteSearcherFromCurrentSearchers(searcher)

@app.route("/")
def sendMainPage():
	userSearchers = []
	if current_user and current_user.is_authenticated:
		userId = current_user.get_id()
		userSearchers = getUserSearchers(userId)
	return render_template('index.html', searchers=userSearchers)

@app.route("/get_started")
def sendGetStartedPage():
	return render_template('get_started.html')

@app.route("/pricing")
def sendPricingPage():
	return render_template('pricing.html')

@app.route("/login", methods=["GET", "POST"])
def sendLoginPage():
	email = request.form.get("email")
	password = request.form.get("password")
	rememberMe = request.form.get("remember-me")

	if email and password:
		# Preveri ali uporabnik obstaja
		userId = getUserId(email=email, password=password)
		if userId:
			user = getUserData(userId)
			login_user(user)
			return redirect(url_for('sendMainPage'))
		else:
			# Uporabnik ne obstaja
			return redirect(url_for('sendLoginPage'))

	return render_template('login.html')

@app.route("/register", methods=["GET", "POST"])
def sendRegisterPage():
	email = request.form.get("email")
	password = request.form.get("password")
	repeatedPassword = request.form.get("repeat-password")
	#ponovitveni paa? if pass == repeatedPass?

	if email and password and repeatedPassword and password == repeatedPassword:
		#preveri ce je na ta postni naslov ze kdo vpisan
		userId = getUserId(email=email)
		if not userId:
			# Naslova se ni v bazi
			addUser(email=email, password=password)
			return redirect(url_for('sendLoginPage'))

	return render_template('register.html')

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('sendMainPage'))

@app.route("/add", methods=["GET", "POST"])
@login_required
def addSearch():
	keywords = request.form.get("keywords")
	if keywords:
		keys = request.form.getlist("key[]")
		values = request.form.getlist("value[]")
		data = dict(zip(keys, values))
		data["q"] = keywords

		searcher = BolhaSearch(**data)
		searchers.append(searcher)
		# Interval prenasanja strani je 10 sekund
		searcher.interval = 60

		searcherId = addSearchToDatabase(searcher)
		addSearchToUser(current_user.get_id(), searcherId)
		searcher.users.append(current_user)

		return redirect(url_for('sendMainPage'))
	
	temp = BolhaSearch()
	return render_template('add.html', parameters=json.dumps([key for key in temp.parameters]))

@app.route("/admin")
@login_required
def sendAdminDashboard():
	if not current_user or not current_user.is_admin():
		return abort(404)
	return render_template('admin_dashboard.html', plugins=[enabledPlugins[p] for p in enabledPlugins])
	

@app.route("/admin/plugin/<pluginName>", methods=["GET", "POST"])
@login_required
def sendPluginPage(pluginName):
	if not current_user or not current_user.is_admin():
		return abort(404)

	if pluginName in enabledPlugins:
		plugin = enabledPlugins[pluginName]
		html = plugin.renderView(request.values)
		return render_template('admin_plugin.html', plugin=plugin, pluginView=html, plugins=[enabledPlugins[p] for p in enabledPlugins])
	return redirect(url_for('sendAdminDashboard'))
	

if __name__ == '__main__':
	# Get all searchers from database
	searchers.extend(getAllSearchers())

	# Ustvarimo nit v kateri bomo iskali po bolhi
	searchThread = BolhaSearchThread(stopFlag, 5, searchers)
	searchThread.daemon = True
	searchThread.start()

	# Pozenemo streznik
	app.run(host="0.0.0.0", port=3000, debug=True)