'''Main, overarching functions.'''
try:
	from PySide.QtCore import *
	from PySide.QtGui import *
	print('PySide imported successfully.')
except:
	print('Problem importing PySide. You will not be able to use GUI functions.')

def openSeries(path):
	'''Returns a Series object with associated Sections from the same directory.'''
	from pyrecon.classes import Section, Series
	import os
	# Process <path> and create Series object
	if '.ser' in path: # Search path for .ser 
		pathToSeries = path
	else: # or .ser in directory path?
		if path[-1] != '/':
			path += '/'
		pathToSeries = path+str([f for f in os.listdir(path) if '.ser' in f].pop())
	series = Series(pathToSeries)
	series.update(sections=True) # find sections in directory
	return series

def start():
	app = QApplication.instance()
	if app is None: # Create QApplication if doesn't exist
		app = QApplication([])
	import pyrecon.pyreconGUI
	gui = pyrecon.pyreconGUI.pyreconMainWindow()
	app.exec_() # Start event-loop
