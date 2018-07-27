import requests
from bs4 import BeautifulSoup
import urllib.parse as urlparse
import time
from plugins.models import Search, Ad
import datetime

class BolhaSearch(Search):

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

		if "url" in kwargs:
			parsedUrl = urlparse.urlparse(kwargs["url"])
			queryParameters = urlparse.parse_qs(parsedUrl.query)
			joinedParameters = {}
			for param in queryParameters:
				joinedParameters[param] = " ".join(queryParameters[param])
			self.parameters.update(joinedParameters)
		else:
			self.parameters.update(kwargs)
		
		self.interval = 10

		for value in self.parameters:
			setattr(self, value, self.parameters[value])

		self.foundAds = []
		self.users = []

	def parseAd(self, adId, html):
		# Get ad image
		adImage = html.find("img")
		if "data-original" in adImage.attrs:
			imageUrl = adImage["data-original"]
		else:
			imageUrl = adImage["src"]

		# Get ad content (url, title, description)
		adContent = html.find("div", {"class": "content"})
		adLink = adContent.find("a")

		# Get url from ad content
		url = adLink["href"]
		if "http://www.bolha.com" not in url:
			url = "http://www.bolha.com" + url

		# Get title and description
		title = adLink.text.strip()
		description = adContent.text.strip()

		adPrice = html.find("div", {"class": "price"})
		price = adPrice.text

		timeAdded = 0
		# Time of ad
		if "aclct" in url:
			parsedUrl = urlparse.urlparse(url)
			if "aclct" in urlparse.parse_qs(parsedUrl.query):
				timeAdded = int(urlparse.parse_qs(parsedUrl.query)["aclct"][0])

		ad = Ad(
			#id = adId,
			title = title,
			description = description,
			url = url,
			image_url = imageUrl,
			price = price,
			ad_added = timeAdded,
			time_added = datetime.datetime.now()
		)
		return ad		

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
			#ad = BolhaAd(adId, ad, self.session)
			allAds.append(self.parseAd(adId, ad))
			#if ad not in self.foundAds:
			#	self.foundAds.append(ad)
		#print(allAds)
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

	def __cmp__(self, other):
		return (hasattr(self, "id") and hasattr(other, "id") and self.id == other.id) or (self.getUrl() == other.getUrl())

	def __eq__(self, other):
		return (hasattr(self, "id") and hasattr(other, "id") and self.id == other.id) or (self.getUrl() == other.getUrl())

class BolhaAd(object):

	def __init__(self, id, adHtml=None, session=None):
		self.id = id
		self.session = session
		self.__dataDownloaded = False
		if adHtml:
			self.getDataFromHtml(adHtml)

	def getDataFromHtml(self, html):
		image = html.find("img")
		if "data-original" in image.attrs:
			self.image = image["data-original"]
		else:
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

	def getMoreData(self):
		reponse = self.session.get(self.url)
		html = BeautifulSoup(reponse.text, "html.parser")

		# Get seller info
		sellerInfo = html.find("div", {"id": "sellerInfo"})

		self.__dataDownloaded = True

	def __cmp__(self, other):
		return self.id == other.id

	def __eq__(self, other):
		return self.id == other.id

	def __repr__(self):
		return u"{}".format(self.title)