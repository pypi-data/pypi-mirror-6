'''Terminal(Non-GUI) handler functions for mergeTool conflicts'''
# SECTION
# - Image
def sectionImages(imageA, imageB):
	if imageA == imageB:
		return imageA
	padding = 20
	print('Section image conflicts:')
	print('='*(padding*3))
	# Header
	print( 'Attribute'.ljust(padding) ),
	print( 'Image A Value'.ljust(padding) ),
	print( 'Image B Value'.ljust(padding) )
	print( '---------'.ljust(padding) ),
	print( '-------------'.ljust(padding) ),
	print( '-------------'.ljust(padding) )

	# Attributes
	print( 'Source:'.ljust(padding) ),
	print( imageA.src.ljust(padding) ),
	print( imageB.src.ljust(padding) )
	print( 'Magnification:'.ljust(padding) ),
	print( str(imageA.mag).ljust(padding) ),
	print( str(imageB.mag).ljust(padding) )
	print('='*(padding*3))
	resp = 0
	while str(resp).lower() not in ['a','b']:
		resp = raw_input('Enter either A or B to choose image for merged section: ')
		if str(resp).lower() == 'a':
			return imageA
		elif str(resp).lower() == 'b':
			return imageB
# - Contours
def sectionContours(uniqueA, compOvlp, confOvlp, uniqueB, sections=None):
	'''Returns list of contours to be added to merged series'''
	outputContours = []

	# Unique: Add unique contours to output
	outputContours.extend(uniqueA)
	outputContours.extend(uniqueB)

	# Completely overlapping: Add a single copy of compOvlp pair to output
	for pair in compOvlp:
		outputContours.append(pair[0])

	# Conflicting: Handle conflicting overlaps
	if sections != None:
		print('Contour Conflicts between: '+str(sectionA.name)+' and '+str(sectionB.name))
	for pair in confOvlp:
		print('Conflicting contour overlap')
		print(pair[0].__dict__) #===
		print(pair[1].__dict__) #=== 
		sel = 0
		while str(sel).lower() not in ['a','b']:
			sel = raw_input('Please enter A, B, or both to select what to output: ')
			if str(sel).lower() == 'a':
				outputContours.append(pair[0])
			elif str(sel).lower() == 'b':
				outputContours.append(pair[1])
			else:
				outputContours.append(pair[0])
				outputContours.append(pair[1])
	return outputContours
# - Attributes
def sectionAttributes(dictA, dictB):
	outputAttributes = {}
	for attribute in ['name','index','thickness', 'alignLocked']:
		if dictA[attribute] == dictB[attribute]:
			outputAttributes[attribute] = dictA[attribute]
		else:
			print('Conflict in attribute: '+str(attribute))
			print('A:{} or B:{}'.format(dictA[attribute], dictB[attribute]))
			choice = 0
			while str(choice).lower() not in ['a','b']: 
				choice = raw_input('Enter either A or B to choose attribute: ')
				if str(choice).lower() == 'a':
					outputAttributes[attribute] = dictA[attribute]
				elif str(choice).lower() == 'b':
					outputAttributes[attribute] = dictB[attribute]
				else:
					print('Invalid entry, try again.')
	return outputAttributes
# SERIES
# - Contours
def seriesContours(contsA, contsB): #=== low priority, return A's contours
	return contsA
# - ZContours
def seriesZContours(ser1zconts, ser2zconts, ser3zconts): #=== HIGH PRIORITY
	# add leftover, unique zcontours to ser3zconts
	ser3zconts.extend(ser1zconts)
	ser3zconts.extend(ser2zconts)
	return ser3zconts
# - Attributes
def seriesAttributes(dictA, dictB): #=== low priority, return A's attributes
	mergedAttributes = {}
	for key in dictA:
		if key not in ['zcontours','contours', 'sections']: # ignore zcontours, contours, sections -- they have their own merge functions
			mergedAttributes[key] = dictA[key]
	return mergedAttributes
