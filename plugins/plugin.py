import jinja2, os

class Plugin(object):
	
	def __init__(self, database, options={}):
		self.path = "plugins/"
		self.database = database
		self.options = options

	def getOption(self, key):
		if key in self.options:
			return self.options[key]
		return None

	def setOption(self, key, value):
		self.options[key] = value
		self.saveOptions()

	def addOption(self, key, value):
		self.options[key] = value
		self.saveOptions()

	def saveOptions(self):
		pluginName = self.__class__.__name__
		for key in self.options:
			option = self.database.session.query(Options).filter_by(plugin_name=pluginName, key=key).first()
			if option:
				option.value = self.options[key]
			else:
				option = Options(plugin_name=pluginName, key=key, value=self.options[key])
				self.database.session.add(option)
		self.database.session.commit()

	def getPath(self):
		if hasattr(self, 'absolutePath'):
			return self.absolutePath
		return "."

	def getTemplate(self, relativePath):
		realPath = os.path.join(self.getPath(), relativePath)
		path, filename = os.path.split(realPath)
		template = jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename)
		return template

	def returnJsonData(self, request):
		return {}

	def renderView(self, data):
		return None

	def renderCard(self):
		return None