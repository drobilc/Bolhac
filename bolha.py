import requests
from bs4 import BeautifulSoup
import urllib.parse as urlparse
import time

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

		self.foundAds = []

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
			self.foundAds.append(ad)
			
		return allAds

	def getUrl(self):
		realUrl = requests.Request("GET", "http://www.bolha.com/iskanje", params=self.parameters).prepare().url
		return realUrl

	def getNewAds(self):
		# Hranimo zadnji cas prenosa podatkov (lastTimeChecked)
		# Ce tega casa se ni, potem ne vemo ali so novi oglasi, ker je to prvic
		if not hasattr(self, "lastTimeChecked"):
			# Nastavimo ta cas
			self.lastTimeChecked = time.time()
			return []
		else:
			newAds = []

			self.parameters["sort"] = 1

			currentPage = 1
			exit = False
			while not exit:
				ads = self.search(page=currentPage)
				for ad in ads:
					if hasattr(ad, "timeAdded") and ad.timeAdded > self.lastTimeChecked:
						newAds.append(ad)
					elif hasattr(ad, "timeAdded") and ad.timeAdded < self.lastTimeChecked:
						exit = True
						break
				currentPage += 1

			self.lastTimeChecked = time.time()
			return newAds

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
		if "http://www.bolha.com" not in self.url:
			self.url = "http://www.bolha.com" + self.url

		# Pridobimo cas iz urlja
		if "aclct" in self.url:
			parsedUrl = urlparse.urlparse(self.url)
			if "aclct" in urlparse.parse_qs(parsedUrl.query):
				self.timeAdded = int(urlparse.parse_qs(parsedUrl.query)["aclct"][0])
		
		self.title = adLink.text.strip()

		self.description = adContent.text.strip()

		adPrice = html.find("div", {"class": "price"})
		self.price = adPrice.text

	def __cmp__(self, other):
		return self.id == other.id

	def __repr__(self):
		return u"{}".format(self.title)