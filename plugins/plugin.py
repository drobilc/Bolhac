import jinja2, os

class Plugin(object):
	
	def __init__(self, database, options={}):
		self.path = "plugins/"

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