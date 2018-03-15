import requests
from bs4 import BeautifulSoup

class BolhaSearch(object):

	def __init__(self, **kwargs):
		self.session = requests.Session()

		self.parameters = {
			"q": None,
			"category": None,
			"location": None,
			"adTypeH": None,
			"priceSortField": None,
			"hasImages": None,
			"datePlaced": None,
			"ast": None,
			"sort": None,
			"unomitted": None
		}

		self.parameters.update(kwargs)
		self.interval = 10

		for value in self.parameters:
			setattr(self, value, self.parameters[value])

	def search(self, page=1):
		url = "http://www.bolha.com/iskanje"

		self.parameters["page"] = page

		response = self.session.get(url, params=self.parameters)
		html = BeautifulSoup(response.text, "html.parser")

		# Get ads list
		adList = html.find("section", {"id": "list"})
		ads = adList.findAll("div", {"class": "ad"})

		allAds = []

		for ad in ads:
			adId = ad.find("div", {"class": "miscellaneous"}).find("div", {"class": "saveAd"}).find("a")["data-id"]
			ad = Ad(adId, ad)
			allAds.append(ad)

		return allAds


class Ad(object):

	def __init__(self, id, adHtml=None):
		self.id = id
		if adHtml:
			self.getDataFromHtml(adHtml)

	def getDataFromHtml(self, html):
		image = html.find("img")
		self.image = image["src"]

		adContent = html.find("div", {"class": "content"})
		adLink = adContent.find("a")
		self.url = adLink["href"]
		self.title = adLink.text.strip()

		self.description = adContent.text.strip()

		adPrice = html.find("div", {"class": "price"})
		self.price = adPrice.text

	def __repr__(self):
		return u"{}".format(self.title)