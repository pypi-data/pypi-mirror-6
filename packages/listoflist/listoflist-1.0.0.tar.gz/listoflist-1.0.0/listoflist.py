def printlol(listinlist):
	for each_item in listinlist:
		if isinstance(each_item, list):
			printlol(each_item)
		else:
			print(each_item)