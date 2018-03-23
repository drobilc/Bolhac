from flask import Flask, request, render_template, redirect, url_for
from threading import Thread, Event
from bolha import BolhaSearch
from customthread import BolhaSearchThread
import MySQLdb
import json

with open("config.json", "r") as configFile:
	jsonData = json.load(configFile)
	mysqlHost = jsonData["database"]["host"]
	mysqlUsername = jsonData["database"]["username"]
	mysqlPassword = jsonData["database"]["password"]
	mysqlDatabase = jsonData["database"]["database"]

app = Flask(__name__)
stopFlag = Event()

# Tabela v kateri hranimo vse iskalnike
searchers = []

database = MySQLdb.connect(host=mysqlHost, user=mysqlUsername, passwd=mysqlPassword, db=mysqlDatabase)

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
			# Uporabnik obstaja
			return "USER EXISTS! ID: {}".format(userId)
		else:
			# Uporabnik ne obstaja
			return "USER DOES NOT EXIST!"

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


@app.route("/add", methods=["POST"])
def addSearch():
	keywords = request.form.get("keywords")
	category = request.form.get("category")
	searcher = BolhaSearch(q=keywords)
	searchers.append(searcher)
	# Interval prenasanja strani je 10 sekund
	searcher.interval = 60
	return redirect(url_for('sendMainPage'))

if __name__ == '__main__':
	# Ustvarimo nit v kateri bomo iskali po bolhi
	searchThread = BolhaSearchThread(stopFlag, 5, searchers)
	searchThread.daemon = True
	searchThread.start()

	# Pozenemo streznik
	app.run(host="0.0.0.0", port=3000, debug=True)