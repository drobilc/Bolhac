from flask import Flask, request, render_template, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user
from threading import Thread, Event
from bolha import BolhaSearch
from customthread import BolhaSearchThread
from user import User
import MySQLdb
import json

with open("config.json", "r") as configFile:
	jsonData = json.load(configFile)
	mysqlHost = jsonData["database"]["host"]
	mysqlUsername = jsonData["database"]["username"]
	mysqlPassword = jsonData["database"]["password"]
	mysqlDatabase = jsonData["database"]["database"]

app = Flask(__name__)
app.secret_key = 'super secret key'
loginManager = LoginManager()
loginManager.init_app(app)

@loginManager.user_loader
def load_user(user_id):
	return getUserData(user_id)

stopFlag = Event()

# Tabela v kateri hranimo vse iskalnike
searchers = [BolhaSearch(q="Gorsko kolo"), BolhaSearch(q="Usnjena jakna"), BolhaSearch(q="Fotoaparat Nikon")]

database = MySQLdb.connect(host=mysqlHost, user=mysqlUsername, passwd=mysqlPassword, db=mysqlDatabase)

def getUserData(user_id):
	cursor = database.cursor()
	cursor.execute("SELECT id, email FROM user WHERE id = %s", [int(user_id)])
	result = cursor.fetchone()
	if result:
		return User(result[0], result[1])

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

@app.route("/")
def sendMainPage():
	return render_template('index.html', searchers=searchers)

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
		return redirect(url_for('sendMainPage'))
	
	return render_template('add.html')
	

if __name__ == '__main__':
	# Ustvarimo nit v kateri bomo iskali po bolhi
	searchThread = BolhaSearchThread(stopFlag, 5, searchers)
	searchThread.daemon = True
	searchThread.start()

	# Pozenemo streznik
	app.run(host="0.0.0.0", port=3000, debug=True)