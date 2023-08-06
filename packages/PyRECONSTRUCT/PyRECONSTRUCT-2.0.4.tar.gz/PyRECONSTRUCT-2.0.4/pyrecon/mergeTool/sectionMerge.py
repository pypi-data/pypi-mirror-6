'''Driver for merging two section objects (as per section XML file).'''
from pyrecon.classes import *
import conflictResolution as handlers
import gui.sectionHandlers as handlersGUI
# MAIN FUNCTIONS
def main(section1, section2, graphical=False):
	# Check for type/index issues
	if section1.__class__.__name__ != 'Section' or section2.__class__.__name__ != 'Section':
		print('Incorrect data types for section1 and/or section2:\n\tMust both be a pyrecon.classes.Section object.')
		return
	elif section1.index != section2.index:
		print('Section indices must match in order to use the mergeTool!')
		return
	print('Sections: '+str(section1.name)+', '+str(section2.name))
	# GUI or not GUI?
	if graphical: # GUI
		mergedSection = graphicalMerge(section1, section2)
	else: # Terminal
		# Combine merged properties into a section object
		mergedSection = nonGraphicalMerge(section1, section2)
	return mergedSection
def nonGraphicalMerge(section1, sections2):
	mergedImage = mergeImages(section1, section2)
	mergedContours = mergeContours(section1, section2)
	mergedAttributes = mergeAttributes(section1, section2)
	# Combine merged properties into a section object
	return Section(mergedImage, mergedContours, mergedAttributes)
def graphicalMerge(section1, section2):
	from PySide.QtGui import QApplication
	# Merge 
	app = QApplication.instance()
	if app is None: # Create QApplication if doesn't exist
		app = QApplication([])
	newImage = mergeImages(section1, section2,
		handler=handlersGUI.sectionImages)
	newContours = mergeContours(section1, section2,
		handler=handlersGUI.sectionContours)
	newAttributes = mergeAttributes(section1, section2,
		handler=handlersGUI.sectionAttributes)
	# Gather data from handlers
	try: # GUI resolution used
		mergedImage = newImage.output
	except: # No conflict, no GUI
		mergedImage = newImage
	try: # "
		mergedContours = newContours.output
	except: # "
		mergedContours = newContours
	try: # "
		mergedAttributes = newAttributes.output
	except: # "
		mergedAttributes = newAttributes
	# Combine merged properties into a section object
	return Section(mergedImage, mergedContours, mergedAttributes)
# MERGE FUNCTIONS
# - Image
def mergeImages(sectionA, sectionB, handler=handlers.sectionImages, parent=None):
	return handler(sectionA.image, sectionB.image, parent=parent)
# - Contours
def mergeContours(sectionA, sectionB, handler=handlers.sectionContours, parent=None):
	'''Returns merged contours between two sections'''
	# Populate shapely shapes
	sectionA.popShapes()
	sectionB.popShapes()
	# Copy contour lists for both sections;
	# These lists only contain unique contours after next two functions
	contsA = [cont for cont in sectionA.contours]
	contsB = [cont for cont in sectionB.contours]
	# Find overlapping contours
	ovlpsA, ovlpsB = checkOverlappingContours(contsA, contsB)
	# Remove all non-unique contours from contsA and contsB
	for cont in ovlpsA:
		if cont in contsA:
			contsA.remove(cont)
	for cont in ovlpsB:
		if cont in contsB:
			contsB.remove(cont)
	# Separate into completely overlapping or incompletely overlapping
	compOvlp, confOvlp = separateOverlappingContours(ovlpsA, ovlpsB)
	# Identify unique contours
	uniqueA, uniqueB = contsA, contsB
	# Handle conflicts
	mergedConts = handler(uniqueA, compOvlp, confOvlp, uniqueB, sections=(sectionA,sectionB), parent=parent)
	return mergedConts
def checkOverlappingContours(contsA, contsB, threshold=(1+2**(-17)), sameName=True):
	'''Returns lists of mutually overlapping contours.''' 
	ovlpsA = [] # Section A contours that have overlaps in section B
	ovlpsB = [] # Section B contours that have overlaps in section A
	for contA in contsA:
		ovlpA = []
		ovlpB = []
		for contB in contsB:
			# If sameName: only check contours with the same name
			if sameName and contA.name == contB.name and contA.overlaps(contB, threshold) != 0:
				ovlpA.append(contA)
				ovlpB.append(contB)
			# If not sameName: check all contours, regardless of same name
			elif not sameName and contA.overlaps(contB, threshold) != 0:
				ovlpA.append(contA)
				ovlpB.append(contB)
		ovlpsA.extend(ovlpA)
		ovlpsB.extend(ovlpB)
	return ovlpsA, ovlpsB
def separateOverlappingContours(ovlpsA, ovlpsB, threshold=(1+2**(-17)), sameName=True):
	'''Returns a list of completely overlapping pairs and a list of conflicting overlapping pairs.'''
	compOvlps = [] # list of completely overlapping contour pairs
	confOvlps = [] # list of conflicting overlapping contour pairs
	# Check for COMPLETELY overlapping contours first (overlaps == 1)
	for contA in ovlpsA:
		for contB in ovlpsB:
			if sameName and contA.name == contB.name:
				if contA.overlaps(contB, threshold) == 1:
					compOvlps.append([contA, contB])
			elif not sameName:
				if contA.overlaps(contB, threshold) == 1:
					compOvlps.append([contA, contB])		
	# Check for CONFLICTING overlapping contours (overlaps != 0 or 1)
	for contA in ovlpsA:
		for contB in ovlpsB:
			if sameName and contA.name == contB.name:
				overlap = contA.overlaps(contB, threshold)
				if overlap != 0 and overlap != 1:
					confOvlps.append([contA, contB])
			elif not sameName:
				overlap = contA.overlaps(contB, threshold)
				if overlap != 0 and overlap != 1:
					confOvlps.append([contA, contB])
	return compOvlps, confOvlps
# - Attributes
def mergeAttributes(sectionA, sectionB, handler=handlers.sectionAttributes, parent=None):
	# extract attributes from class dictionaries
	attributes = ['name', 'index', 'thickness', 'alignLocked']
	secAatts = {} 
	secBatts = {}
	for key in attributes:
		secAatts[key] = sectionA.__dict__[key]
		secBatts[key] = sectionB.__dict__[key]
	return handler(secAatts, secBatts, parent=parent)