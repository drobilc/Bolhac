import glob, os, importlib, inspect

def getAvailablePlugins(path="."):
	availablePlugins = glob.glob("{}/plugins/**/*.py".format(path))
	return availablePlugins

def getPluginName(pluginPath):
	pluginName = os.path.basename(pluginPath)
	if ".py" in pluginName:
		pluginName = pluginName.replace(".py", "")
	return pluginName

def getMainClass(plugin, pluginName):
	allClasses = inspect.getmembers(plugin, inspect.isclass)
	if len(allClasses) > 0:
		mainClass = None
		for className in allClasses:
			if className[0] == pluginName:
				mainClass = className[1]
				return mainClass

def importPlugin(pluginPath):
	# Get plugin name and print debug info
	pluginName = getPluginName(pluginPath)
	absolutePath, filename = os.path.split(pluginPath)

	# Import plugin from path
	importedPlugin = importlib.import_module("plugins.{}.{}".format(pluginName, pluginName))

	# Get main class from plugin
	mainClass = getMainClass(importedPlugin, pluginName)
	if mainClass:
		# Create object from class
		database = []
		pluginObject = mainClass(database)
		pluginObject.absolutePath = absolutePath
		# Return object
		return pluginObject