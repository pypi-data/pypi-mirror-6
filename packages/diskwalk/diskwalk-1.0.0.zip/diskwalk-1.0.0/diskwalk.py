import os

class diskwalk(object):
	def __init__(self, path):
		self.path = path

	def enumeratepaths(self):
		path_collection = []
		for dirpath, dirnames, filenames in os.walk(self.path):
			for file in filenames:
				fullpath = os.path.join(dirpath, file)
				path_collection.append(fullpath)
		return path_collection

	def enumeratefiles(self):
		file_collection = []
		for dirpath, dirnames, filenames in os.walk(self.path):
			for file in filenames:
				file_collection.append(file)
		return file_collection

	def enumeratedir(self):
		dir_collection = []
		for dirpath,dirnames, filenames in os.walk(self.path):
			for dir in dirnames:
				fullpath = os.path.join(dirpath, dir)
				dir_collection.append(fullpath)
		return dir_collection
