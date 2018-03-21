from flask import Flask, request, render_template, redirect, url_for
from threading import Thread, Event
from bolha import BolhaSearch
from customthread import BolhaSearchThread

app = Flask(__name__)
stopFlag = Event()

# Tabela v kateri hranimo vse iskalnike
searchers = []

@app.route("/")
def sendMainPage():
	return render_template('index.html', searchers=searchers)

@app.route("/login", methods=["GET", "POST"])
def sendLoginPage():
	email = request.form.get("email")
	password = request.form.get("password")
	rememberMe = request.form.get("remember-me")

	if email and password and rememberMe:
		# Preveri ali uporabnik obstaja
		pass

	return render_template('login.html')

@app.route("/register", methods=["GET", "POST"])
def sendRegisterPage():
	email = request.form.get("email")
	password = request.form.get("password")
	repeatedPassword = request.form.get("repeat-password")
	#ponovitveni paa? if pass == repeatedPass?

	if email and password and repeatedPassword and password == repeatedPassword:
		#preveri ce je na ta postni naslov ze kdo vpisan
		pass
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