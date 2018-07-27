from flask import Flask, request, render_template, redirect, url_for, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from threading import Thread, Event
from bolha import BolhaSearch
from emailer import Emailer
from customthread import BolhaSearchThread
import MySQLdb, MySQLdb.cursors
import json
from flask_sqlalchemy import SQLAlchemy
import datetime

import plugin_manager

from database.models import Base, User, Anonymous, Search

with open("config.json", "r") as configFile:
	jsonData = json.load(configFile)

	# Secret key for login manager
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
loginManager.anonymous_user = Anonymous

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
database = SQLAlchemy(app)

# FOR PLUGIN SYSTEM
enabledPlugins = {}
availablePlugins = plugin_manager.getAvailablePlugins()

print("Importing plugins")
for pluginPath in availablePlugins:
	pluginName = plugin_manager.getPluginName(pluginPath)
	print(" - Importing plugin {}".format(pluginName))
	importedPlugin = plugin_manager.importPlugin(pluginPath)
	enabledPlugins[pluginName] = importedPlugin

@loginManager.user_loader
def load_user(user_id):
	return database.session.query(User).filter_by(id=user_id).first()

stopFlag = Event()

emailer = Emailer(emailServer, emailPort, emailUsername, emailPassword)

# Tabela v kateri hranimo vse iskalnike
searchers = []

# Slovar v katerem hranimo podatke
userObjects = {}

@app.route("/remove/<int:searcher>", methods=["GET"])
@login_required
def deleteSearcher(searcher):
	if current_user and current_user.is_authenticated:
		search = database.session.query(Search).filter_by(id=searcher).first()
		if search:
			print("Deleting {}".format(search))
			database.session.delete(search)
			database.session.commit()


@app.route("/")
def sendMainPage():
	userSearchers = []
	if current_user and current_user.is_authenticated:
		userSearchers = [BolhaSearch(url=s.url) for s in current_user.searchers]
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
		user = database.session.query(User).filter_by(email=email, password=password).first()
		if user:
			login_user(user)
			return redirect(url_for('sendMainPage'))
		else:
			return redirect(url_for('sendLoginPage'))

	return render_template('login.html')

@app.route("/register", methods=["GET", "POST"])
def sendRegisterPage():
	email = request.form.get("email")
	password = request.form.get("password")
	repeatedPassword = request.form.get("repeat-password")

	if email and password and repeatedPassword and password == repeatedPassword:
		#preveri ce je na ta postni naslov ze kdo vpisan
		user = database.session.query(User).filter_by(email=email).first()
		if not user:
			# Naslova se ni v bazi
			user = User(email=email, password=password, account_type=0)
			database.session.add(user)
			database.session.commit()
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

		search = Search(url=searcher.getUrl(), date_added=datetime.datetime.now(), last_search=datetime.datetime.now())
		current_user.searchers.append(search)
		database.session.add(current_user)
		database.session.commit()

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

@app.route("/admin/plugin/<pluginName>/data", methods=["GET", "POST"])
def sendPluginData(pluginName):
	if pluginName in enabledPlugins:
		plugin = enabledPlugins[pluginName]
		data = plugin.returnJsonData(request.values)
		return jsonify(data)
	return jsonify({})

def getAllSearchers():
	searchers = database.session.query(Search).all()
	realSearchers = []
	for searcher in searchers:
		realSearchers.append(BolhaSearch(url=searcher.url))
	return realSearchers

if __name__ == '__main__':
	# Create database
	Base.metadata.create_all(bind=database.engine)
	database.session.commit()

	# Get all searchers from database
	searchers.extend(getAllSearchers())

	# Ustvarimo nit v kateri bomo iskali po bolhi
	searchThread = BolhaSearchThread(stopFlag, 5, searchers)
	searchThread.daemon = True
	searchThread.start()

	# Pozenemo streznik
	app.run(host="0.0.0.0", port=3000, debug=True)