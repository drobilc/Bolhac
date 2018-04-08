import json
import copy

class Options(object):
	
	def __init__(self, filename):
		self.filename = filename
		self.loadData()

	def saveData(self):
		f = open(self.filename, "w")
		json.dump(self.options, f)
		f.close()

	def loadData(self):
		f = open(self.filename, "r")
		self.options = json.load(f)
		f.close()

	def findPlugin(self, pluginName):
		for i, plugin in enumerate(self.options["plugins"]):
			if plugin["name"] == pluginName:
				return i
		return -1

	def pluginOptions(self, pluginName):
		pluginIndex = self.findPlugin(pluginName)  
		if pluginIndex > -1:
			return self.options["plugins"][pluginIndex]
		return None

	def get(self, propertyName):
		if propertyName in self.options:
			return self.options[propertyName]
		return None