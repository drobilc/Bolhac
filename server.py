from flask import Flask, request, send_from_directory
from bolha import BolhaSearch

app = Flask(__name__)

# Tabela v kateri hranimo vse iskalnike
searchers = []

@app.route("/")
def sendMainPage():
	return send_from_directory("public", "plugin.html")

@app.route("/add", methods=["POST"])
def addSearch():
	keywords = request.form.get("keywords")
	category = request.form.get("category")
	searcher = BolhaSearch(q=keywords)
	searchers.append(searcher)
	# Interval prenasanja strani je 10 sekund
	searcher.interval = 10
	return "ok"

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=3000, debug=True)