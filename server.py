from flask import Flask, request, render_template, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from threading import Thread, Event
from bolha import BolhaSearch
from emailer import Emailer
from customthread import BolhaSearchThread
from user import User
import MySQLdb
import json

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

app = Flask(__name__)
app.secret_key = loginManagerSecretKey
loginManager = LoginManager()
loginManager.init_app(app)

@loginManager.user_loader
def load_user(user_id):
	return getUserData(user_id)

stopFlag = Event()

emailer = Emailer(emailServer, emailPort, emailUsername, emailPassword)

# Tabela v kateri hranimo vse iskalnike
searchers = []

database = MySQLdb.connect(host=mysqlHost, user=mysqlUsername, passwd=mysqlPassword, db=mysqlDatabase)

def getUserData(user_id):
	cursor = database.cursor()
	cursor.execute("SELECT id, email FROM user WHERE id = %s", [int(user_id)])
	result = cursor.fetchone()
	if result:
		return User(result[0], result[1], emailer)

def getUserId(email=None, password=None):
	cursor = database.cursor()
	if email and password:
		cursor.execute("SELECT id FROM user WHERE email = %s AND password = %s", [email, password])
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
	cursor.execute("INSERT INTO user (email, password) VALUES (%s, %s)", [email, password])
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
	searchers = []
	cursor = database.cursor()
	cursor.execute("SELECT search.url FROM has_search INNER JOIN search ON has_search.search_id = search.id WHERE has_search.user_id = %s;", [user])
	results = cursor.fetchall()
	for result in results:
		searchers.append(BolhaSearch(url=result[0]))
	return searchers

def getUsersToNotify(searcher):
	users = []
	cursor = database.cursor()
	cursor.execute("SELECT has_search.user_id, user.email FROM has_search INNER JOIN user ON has_search.user_id = user.id WHERE has_search.search_id = %s;", [searcher])
	results = cursor.fetchall()
	for result in results:
		users.append(User(result[0], result[1], emailer))
	return users

def getAllSearchers():
	searchers = []
	cursor = database.cursor()
	cursor.execute("SELECT search.id, search.url FROM has_search INNER JOIN search ON has_search.search_id = search.id;")
	results = cursor.fetchall()
	for result in results:
		users = getUsersToNotify(result[0])
		searcher = BolhaSearch(url=result[1])
		searcher.users = users
		searcher.interval = 60
		searchers.append(searcher)
	return searchers

@app.route("/")
def sendMainPage():
	userSearchers = []
	if current_user and current_user.is_authenticated:
		userId = current_user.get_id()
		userSearchers = getUserSearchers(userId)
	return render_template('index.html', searchers=userSearchers)

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
			return "REGISTRATION COMPLETE!"

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
		searcher = BolhaSearch(q=keywords)
		searchers.append(searcher)
		# Interval prenasanja strani je 10 sekund
		searcher.interval = 60

		searcherId = addSearchToDatabase(searcher)
		addSearchToUser(current_user.get_id(), searcherId)
		searcher.users.append(current_user)

		return redirect(url_for('sendMainPage'))
	
	return render_template('add.html')
	

if __name__ == '__main__':
	# Get all searchers from database
	searchers.extend(getAllSearchers())

	# Ustvarimo nit v kateri bomo iskali po bolhi
	searchThread = BolhaSearchThread(stopFlag, 5, searchers)
	searchThread.daemon = True
	searchThread.start()

	# Pozenemo streznik
	app.run(host="0.0.0.0", port=3000, debug=True)